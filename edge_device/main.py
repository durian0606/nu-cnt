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
from config import CAPTURE_INTERVAL, DEBUG_MODE, POWER_SAVE_MODE


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
            print("   PC에서 MQTT 브로커가 실행 중인지 확인하세요.")
        else:
            print("\n✓ 모든 시스템 준비 완료")

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

    def run(self):
        """
        메인 루프 실행
        """
        self.running = True
        frame_count = 0
        start_time = time.time()

        # 촬영 간격 설정
        interval = CAPTURE_INTERVAL * (2 if POWER_SAVE_MODE else 1)

        print(f"\n감지 시작 (간격: {interval}초)")
        print("종료하려면 Ctrl+C를 누르세요.\n")

        try:
            while self.running:
                loop_start = time.time()
                frame_count += 1

                # 1. 카메라로 프레임 캡처
                frame = self.camera.capture_frame()

                if frame is None:
                    print("⚠️  프레임 캡처 실패")
                    time.sleep(interval)
                    continue

                # 2. 객체 감지
                count, bounding_boxes = self.detector.detect(frame)

                # 3. 결과 전송 (MQTT)
                if self.mqtt_client.is_connected():
                    self.mqtt_client.publish_count(count, bounding_boxes)
                else:
                    print("⚠️  MQTT 연결 끊김 - 전송 실패")

                # 4. 통계 출력 (10초마다)
                if frame_count % 10 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    print(f"\n--- 통계 (프레임 #{frame_count}) ---")
                    print(f"현재 감지: {count}개")
                    print(f"평균 FPS: {fps:.2f}")
                    print(f"실행 시간: {elapsed:.1f}초")

                # 5. 상태 전송 (1분마다)
                if frame_count % 60 == 0:
                    status = self._get_device_status()
                    self.mqtt_client.publish_status(status)

                # 6. 다음 사이클까지 대기
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
        # 라즈베리 파이 시스템 정보 수집
        status = {
            "device_type": "raspberry_pi_4",
            "uptime": time.time()
        }

        # CPU 온도 (라즈베리 파이 전용)
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp = float(f.read()) / 1000.0
                status["cpu_temperature"] = round(temp, 1)
        except:
            status["cpu_temperature"] = None

        # 배터리 레벨 (실제 구현 필요 - 하드웨어 의존)
        # 여기서는 가상 데이터
        status["battery_level"] = 100  # TODO: 실제 배터리 레벨 읽기

        return status

    def stop(self):
        """
        시스템 종료
        """
        print("\n시스템 종료 중...")

        self.running = False

        # 컴포넌트 정리
        if hasattr(self, 'camera'):
            self.camera.close()

        if hasattr(self, 'mqtt_client'):
            self.mqtt_client.disconnect()

        print("✓ 종료 완료")


# 메인 실행
if __name__ == "__main__":
    # 시스템 시작
    edge_system = NurungjiCounterEdge()

    # 메인 루프 실행
    edge_system.run()
