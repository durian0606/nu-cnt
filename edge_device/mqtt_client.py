"""
누룽지 생산량 카운팅 시스템 - MQTT 클라이언트 모듈
라즈베리 파이에서 PC로 감지 결과 전송
"""

import paho.mqtt.client as mqtt
import json
import time
from config import (
    MQTT_BROKER_ADDRESS,
    MQTT_BROKER_PORT,
    MQTT_TOPICS,
    DEBUG_MODE
)


class MQTTClient:
    """
    MQTT 통신 클라이언트 클래스
    """

    def __init__(self):
        """MQTT 클라이언트 초기화"""
        self.client = None
        self.connected = False
        self._initialize_client()

    def _initialize_client(self):
        """MQTT 클라이언트 설정 및 연결"""
        try:
            # 클라이언트 생성
            self.client = mqtt.Client(client_id="nurungji_edge_device")

            # 콜백 설정
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_publish = self._on_publish

            # 브로커 연결
            if DEBUG_MODE:
                print(f"[MQTT] 브로커 연결 시도: {MQTT_BROKER_ADDRESS}:{MQTT_BROKER_PORT}")

            self.client.connect(MQTT_BROKER_ADDRESS, MQTT_BROKER_PORT, keepalive=60)

            # 백그라운드 네트워크 루프 시작
            self.client.loop_start()

        except Exception as e:
            print(f"[MQTT] 오류: 클라이언트 초기화 실패 - {e}")
            raise

    def _on_connect(self, client, userdata, flags, rc):
        """
        연결 성공 콜백

        Args:
            rc (int): 연결 결과 코드 (0=성공)
        """
        if rc == 0:
            self.connected = True
            if DEBUG_MODE:
                print(f"[MQTT] ✓ 브로커 연결 성공")
        else:
            self.connected = False
            print(f"[MQTT] ✗ 연결 실패 - 코드: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """
        연결 해제 콜백
        """
        self.connected = False
        if rc != 0:
            print(f"[MQTT] 예기치 않은 연결 해제 - 코드: {rc}")
            if DEBUG_MODE:
                print(f"[MQTT] 재연결 시도 중...")

    def _on_publish(self, client, userdata, mid):
        """
        메시지 발행 완료 콜백
        """
        if DEBUG_MODE:
            print(f"[MQTT] 메시지 전송 완료 - ID: {mid}")

    def publish_count(self, count, bounding_boxes):
        """
        감지된 누룽지 개수 전송

        Args:
            count (int): 감지된 개수
            bounding_boxes (list): 바운딩 박스 리스트

        Returns:
            bool: 전송 성공 여부
        """
        if not self.connected:
            print("[MQTT] 오류: 브로커에 연결되지 않음")
            return False

        try:
            # 페이로드 생성
            payload = {
                "timestamp": time.time(),
                "count": count,
                "stable_count": count,  # Phase 2에서 안정화 로직 추가 예정
                "boxes": bounding_boxes
            }

            # JSON 직렬화
            message = json.dumps(payload, ensure_ascii=False)

            # 발행
            result = self.client.publish(
                topic=MQTT_TOPICS["count"],
                payload=message,
                qos=1  # 최소 1회 전달 보장
            )

            if DEBUG_MODE:
                print(f"[MQTT] 카운트 전송: {count}개")

            return result.rc == mqtt.MQTT_ERR_SUCCESS

        except Exception as e:
            print(f"[MQTT] 오류: 카운트 전송 실패 - {e}")
            return False

    def publish_batch_complete(self, final_count):
        """
        팬 가득참 신호 전송

        Args:
            final_count (int): 확정된 개수

        Returns:
            bool: 전송 성공 여부
        """
        if not self.connected:
            print("[MQTT] 오류: 브로커에 연결되지 않음")
            return False

        try:
            payload = {
                "timestamp": time.time(),
                "final_count": final_count
            }

            message = json.dumps(payload, ensure_ascii=False)

            result = self.client.publish(
                topic=MQTT_TOPICS["batch_complete"],
                payload=message,
                qos=1
            )

            if DEBUG_MODE:
                print(f"[MQTT] 팬 확정 전송: {final_count}개")

            return result.rc == mqtt.MQTT_ERR_SUCCESS

        except Exception as e:
            print(f"[MQTT] 오류: 팬 확정 전송 실패 - {e}")
            return False

    def publish_status(self, status_data):
        """
        디바이스 상태 전송 (배터리, 온도 등)

        Args:
            status_data (dict): 상태 정보

        Returns:
            bool: 전송 성공 여부
        """
        if not self.connected:
            return False

        try:
            payload = {
                "timestamp": time.time(),
                **status_data
            }

            message = json.dumps(payload, ensure_ascii=False)

            result = self.client.publish(
                topic=MQTT_TOPICS["status"],
                payload=message,
                qos=0  # 상태는 최선 노력 전달
            )

            return result.rc == mqtt.MQTT_ERR_SUCCESS

        except Exception as e:
            print(f"[MQTT] 오류: 상태 전송 실패 - {e}")
            return False

    def is_connected(self):
        """
        연결 상태 확인

        Returns:
            bool: 연결 여부
        """
        return self.connected

    def disconnect(self):
        """MQTT 클라이언트 종료"""
        if self.client is not None:
            self.client.loop_stop()
            self.client.disconnect()
            if DEBUG_MODE:
                print("[MQTT] 연결 종료")


# 테스트 코드
if __name__ == "__main__":
    print("MQTT 클라이언트 테스트 시작...")
    print("주의: 실제 MQTT 브로커가 실행 중이어야 합니다.")

    try:
        # 클라이언트 초기화
        mqtt_client = MQTTClient()

        # 연결 대기
        time.sleep(2)

        if mqtt_client.is_connected():
            print("✓ MQTT 브로커 연결 성공")

            # 테스트 데이터 전송
            test_boxes = [
                {"x": 100, "y": 100, "w": 50, "h": 50},
                {"x": 200, "y": 100, "w": 50, "h": 50}
            ]

            # 카운트 전송 테스트
            success = mqtt_client.publish_count(2, test_boxes)
            print(f"카운트 전송: {'성공' if success else '실패'}")

            time.sleep(1)

            # 상태 전송 테스트
            status = {
                "battery_level": 85,
                "temperature": 45.2,
                "uptime": 3600
            }
            success = mqtt_client.publish_status(status)
            print(f"상태 전송: {'성공' if success else '실패'}")

        else:
            print("✗ MQTT 브로커 연결 실패")

    except Exception as e:
        print(f"테스트 실패: {e}")

    finally:
        # 정리
        time.sleep(1)
        mqtt_client.disconnect()
        print("\nMQTT 클라이언트 테스트 완료")
