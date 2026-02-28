"""
누룽지 생산량 카운팅 시스템 - 메인 프로그램
라즈베리 파이 엣지 디바이스에서 실행
"""

import time
import signal
import sys
from camera_capture import CameraCapture
from detector import NurungjiDetector
from mqtt_client import MQTTClient
from mjpeg_server import MJPEGServer
import config
import firebase_client
from config import CAPTURE_INTERVAL, DEBUG_MODE, POWER_SAVE_MODE

# Firebase activeProduction 조회 간격 (초)
ACTIVE_PRODUCT_POLL_INTERVAL = 30


class NurungjiCounterEdge:
    """
    누룽지 카운팅 엣지 디바이스 메인 클래스
    """

    def __init__(self):
        """시스템 초기화"""
        self.running = False

        # 컴포넌트 초기화
        print("=" * 50)
        print("누룽지 생산량 자동 카운팅 시스템 - 엣지 디바이스")
        print("=" * 50)

        print("\n[1/3] 카메라 초기화 중...")
        self.camera = CameraCapture()

        print("[2/3] 객체 감지기 초기화 중...")
        self.detector = NurungjiDetector()

        print("[3/3] MQTT 클라이언트 초기화 중...")
        self.mqtt_client = MQTTClient()

        # 연결 대기
        time.sleep(2)

        if not self.mqtt_client.is_connected():
            print("\n⚠️  경고: MQTT 브로커에 연결되지 않았습니다.")
            print("   MQTT 없이 Firebase 모드로 계속 실행합니다.")
        else:
            print("\n✓ 모든 시스템 준비 완료")

        # 팬 완료 감지용 이전 카운트
        self._previous_count = 0

        # Firebase activeProduction 캐시
        self._active_product = None
        self._last_product_poll = 0

        # 장치 상태 주기적 업데이트 (30초마다)
        self._last_status_push = 0
        # Firebase deviceSettings 주기적 갱신 (5분마다)
        self._last_settings_refresh = 0
        # 누적 프레임 수
        self._frames_total = 0
        # 동적 촬영 간격 (Firebase 설정 오버라이드 가능)
        self._capture_interval = CAPTURE_INTERVAL

        # 캘리브레이션 모드 (PC에서 원격으로 켜고 끔)
        self._calibration_mode = False
        self._last_calib_image = 0  # 마지막 이미지 전송 시각

        # 최신 바운딩 박스 (MJPEG 오버레이용)
        self._latest_boxes = []

        # MJPEG 스트리밍 서버 시작 (데몬 스레드)
        self.mjpeg_server = MJPEGServer(
            get_calibration_mode=lambda: self._calibration_mode,
            get_latest_boxes=lambda: self._latest_boxes,
        )
        self.mjpeg_server.start()

        # Firebase 명령 폴링 간격 (초)
        self._last_command_poll = 0
        self._command_poll_interval = 3  # 3초마다 폴링

        # MQTT 명령 핸들러 등록
        self.mqtt_client.set_command_handler(self._on_command)

        # 시그널 핸들러 설정 (Ctrl+C 처리)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, sig, frame):
        """
        종료 시그널 핸들러 (Ctrl+C)
        """
        print("\n\n종료 신호 수신...")
        self.stop()
        sys.exit(0)

    def _on_command(self, payload):
        """
        PC로부터 수신한 MQTT 명령 처리

        Args:
            payload (dict): {"action": "calibration_start" | "calibration_stop", ...}
        """
        action = payload.get("action", "")

        if action == "calibration_start":
            self._calibration_mode = True
            self._last_calib_image = 0  # 즉시 이미지 전송
            print("[캘리브레이션] 시작 - PC에서 실시간 영상 확인 가능")

        elif action == "calibration_stop":
            self._calibration_mode = False
            print("[캘리브레이션] 중지")

        else:
            print(f"[명령] 알 수 없는 명령: {action}")

    def _refresh_active_product(self):
        """
        Firebase에서 현재 생산 중인 제품명을 주기적으로 조회
        ACTIVE_PRODUCT_POLL_INTERVAL 초마다 갱신
        """
        now = time.time()
        if now - self._last_product_poll >= ACTIVE_PRODUCT_POLL_INTERVAL:
            product = firebase_client.get_active_product()
            if product != self._active_product:
                if product:
                    print(f"[Firebase] 생산 시작: {product}")
                else:
                    print("[Firebase] 생산 중인 제품 없음")
            self._active_product = product
            self._last_product_poll = now
        return self._active_product

    def _check_batch_complete(self, current_count):
        """
        팬 완료 감지: 이전 카운트 > 0 이고 현재 카운트 == 0 이면 팬 1판 완료

        Args:
            current_count (int): 현재 프레임의 감지 갯수

        Returns:
            int: 완료된 팬의 갯수 (0이면 완료 없음)
        """
        batch_count = 0
        if self._previous_count > 0 and current_count == 0:
            batch_count = self._previous_count
            print(f"\n🍚 팬 완료! 갯수: {batch_count}개")
        self._previous_count = current_count
        return batch_count

    def run(self):
        """
        메인 루프 실행
        """
        self.running = True
        frame_count = 0
        start_time = time.time()

        print(f"\n감지 시작 (간격: {self._capture_interval}초)")
        print("종료하려면 Ctrl+C를 누르세요.\n")

        # 시작 시 즉시 activeProduct 조회 및 deviceSettings 로드
        self._last_product_poll = 0

        try:
            while self.running:
                loop_start = time.time()
                frame_count += 1
                self._frames_total = frame_count

                # 촬영 간격 (Firebase 설정으로 동적 변경 가능)
                interval = self._capture_interval * (2 if config.POWER_SAVE_MODE else 1)

                # 1. 카메라로 프레임 캡처
                frame = self.camera.capture_frame()

                if frame is None:
                    print("⚠️  프레임 캡처 실패")
                    time.sleep(interval)
                    continue

                # 2. 객체 감지
                count, bounding_boxes = self.detector.detect(frame)

                # 2-1. MJPEG 서버에 최신 프레임 전달
                self._latest_boxes = bounding_boxes
                self.mjpeg_server.push_frame(frame, bounding_boxes)

                # 3. MQTT 전송 (연결된 경우)
                if self.mqtt_client.is_connected():
                    self.mqtt_client.publish_count(count, bounding_boxes)

                    # 캘리브레이션 모드: 3초마다 감지 결과 이미지 전송
                    if self._calibration_mode:
                        now = time.time()
                        if now - self._last_calib_image >= 3.0:
                            self.mqtt_client.publish_calibration_image(frame, count, bounding_boxes)
                            self._last_calib_image = now

                # 4. 팬 완료 감지 → Firebase 업데이트
                batch_count = self._check_batch_complete(count)
                if batch_count > 0:
                    active_product = self._refresh_active_product()
                    if active_product:
                        ok = firebase_client.increment_production(active_product, batch_count)
                        if ok:
                            print(f"   → Firebase 기록 완료: {active_product} +{batch_count}")
                        else:
                            print(f"   → Firebase 기록 실패")
                    else:
                        print("   → 생산 중인 제품 없음 (zego 웹앱에서 '생산 시작' 필요)")

                # 5. Firebase activeProduct 주기적 갱신 (팬 완료와 무관하게)
                self._refresh_active_product()

                # 6. Firebase에 장치 상태 주기적 업데이트 (30초마다)
                self._push_status_if_needed(count)

                # 7. Firebase deviceSettings 주기적 갱신 (5분마다)
                self._refresh_settings_if_needed()

                # 7-1. Firebase deviceCommands 폴링 (3초마다)
                self._poll_firebase_commands()

                # 8. 통계 출력 (10초마다)
                if frame_count % 10 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    print(f"\n--- 통계 (프레임 #{frame_count}) ---")
                    print(f"현재 감지: {count}개")
                    print(f"평균 FPS: {fps:.2f}")
                    print(f"실행 시간: {elapsed:.1f}초")
                    print(f"생산 중 제품: {self._active_product or '없음'}")

                # 9. MQTT 상태 전송 (1분마다)
                if frame_count % 60 == 0 and self.mqtt_client.is_connected():
                    status = self._get_device_status()
                    self.mqtt_client.publish_status(status)

                # 10. 다음 사이클까지 대기
                loop_duration = time.time() - loop_start
                sleep_time = max(0, interval - loop_duration)

                if sleep_time > 0:
                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            print("\n\n사용자가 중단함")

        except Exception as e:
            print(f"\n오류 발생: {e}")
            import traceback
            traceback.print_exc()

        finally:
            self.stop()

    def _get_device_status(self):
        """
        디바이스 상태 정보 수집

        Returns:
            dict: 상태 정보
        """
        status = {
            "device_type": "raspberry_pi_4",
            "uptime": time.time(),
            "active_product": self._active_product
        }

        # CPU 온도 (라즈베리 파이 전용)
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp = float(f.read()) / 1000.0
                status["cpu_temperature"] = round(temp, 1)
        except:
            status["cpu_temperature"] = None

        status["battery_level"] = 100

        return status

    def _push_status_if_needed(self, current_count):
        """30초마다 Firebase에 장치 상태 업데이트"""
        now = time.time()
        if now - self._last_status_push >= 30:
            status_info = self._get_device_status()
            cpu_temp = status_info.get("cpu_temperature")
            firebase_client.push_device_status(current_count, cpu_temp, self._frames_total)
            self._last_status_push = now

    def _poll_firebase_commands(self):
        """3초마다 Firebase deviceCommands 노드를 폴링하여 명령 처리"""
        now = time.time()
        if now - self._last_command_poll >= self._command_poll_interval:
            firebase_client.poll_command(self._on_command)
            self._last_command_poll = now

    def _refresh_settings_if_needed(self):
        """5분마다 Firebase deviceSettings를 읽어서 runtime config에 적용"""
        now = time.time()
        if now - self._last_settings_refresh >= 300:
            settings = firebase_client.get_device_settings()
            if settings:
                self._apply_device_settings(settings)
            self._last_settings_refresh = now

    def _apply_device_settings(self, settings):
        """Firebase deviceSettings를 runtime config에 오버라이드"""
        changed = []

        if 'BINARY_THRESHOLD' in settings:
            val = int(settings['BINARY_THRESHOLD'])
            if config.BINARY_THRESHOLD != val:
                config.BINARY_THRESHOLD = val
                changed.append(f"BINARY_THRESHOLD={val}")

        if 'MIN_AREA' in settings:
            val = int(settings['MIN_AREA'])
            if config.MIN_AREA != val:
                config.MIN_AREA = val
                changed.append(f"MIN_AREA={val}")

        if 'MAX_AREA' in settings:
            val = int(settings['MAX_AREA'])
            if config.MAX_AREA != val:
                config.MAX_AREA = val
                changed.append(f"MAX_AREA={val}")

        if 'CAPTURE_INTERVAL' in settings:
            val = float(settings['CAPTURE_INTERVAL'])
            if self._capture_interval != val:
                self._capture_interval = val
                changed.append(f"CAPTURE_INTERVAL={val}")

        if 'POWER_SAVE_MODE' in settings:
            val = bool(settings['POWER_SAVE_MODE'])
            if config.POWER_SAVE_MODE != val:
                config.POWER_SAVE_MODE = val
                changed.append(f"POWER_SAVE_MODE={val}")

        if changed:
            print(f"[설정] Firebase 설정 적용: {', '.join(changed)}")
        elif DEBUG_MODE:
            print("[설정] Firebase 설정 변경 없음")

    def stop(self):
        """
        시스템 종료
        """
        print("\n시스템 종료 중...")

        self.running = False

        # Firebase에 종료 상태 업데이트
        firebase_client.set_device_stopped()

        # 컴포넌트 정리
        if hasattr(self, 'camera'):
            self.camera.close()

        if hasattr(self, 'mqtt_client'):
            self.mqtt_client.disconnect()

        if hasattr(self, 'mjpeg_server'):
            self.mjpeg_server.stop()

        print("✓ 종료 완료")


# 메인 실행
if __name__ == "__main__":
    # 시스템 시작
    edge_system = NurungjiCounterEdge()

    # 메인 루프 실행
    edge_system.run()
