"""
누룽지 생산량 카운팅 시스템 - MQTT 수신 모듈
라즈베리 파이로부터 데이터 수신
"""

import paho.mqtt.client as mqtt
import json
import threading
from ..config import MQTT_BROKER_ADDRESS, MQTT_BROKER_PORT, MQTT_TOPICS, DEBUG_MODE


class MQTTReceiver:
    """
    MQTT 메시지 수신 클래스
    """

    def __init__(self, on_count_update=None, on_batch_complete=None, on_status_update=None):
        """
        MQTT 수신기 초기화

        Args:
            on_count_update (callable): 카운트 업데이트 콜백 (count, boxes)
            on_batch_complete (callable): 팬 확정 콜백 (final_count)
            on_status_update (callable): 상태 업데이트 콜백 (status_data)
        """
        self.client = None
        self.connected = False
        self.lock = threading.Lock()

        # 콜백 함수
        self.on_count_update = on_count_update
        self.on_batch_complete = on_batch_complete
        self.on_status_update = on_status_update

        # 통계
        self.messages_received = 0
        self.last_message_time = None

        self._initialize_client()

    def _initialize_client(self):
        """MQTT 클라이언트 초기화"""
        try:
            # 클라이언트 생성
            self.client = mqtt.Client(client_id="nurungji_pc_receiver")

            # 콜백 설정
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message

            if DEBUG_MODE:
                print(f"[MQTT Receiver] 클라이언트 생성 완료")

        except Exception as e:
            print(f"[MQTT Receiver] 오류: 클라이언트 초기화 실패 - {e}")
            raise

    def connect(self, broker_address=None, port=None):
        """
        브로커에 연결

        Args:
            broker_address (str): 브로커 주소 (None이면 config 사용)
            port (int): 브로커 포트 (None이면 config 사용)
        """
        broker = broker_address or MQTT_BROKER_ADDRESS
        broker_port = port or MQTT_BROKER_PORT

        try:
            if DEBUG_MODE:
                print(f"[MQTT Receiver] 브로커 연결 시도: {broker}:{broker_port}")

            self.client.connect(broker, broker_port, keepalive=60)
            self.client.loop_start()

        except Exception as e:
            print(f"[MQTT Receiver] 오류: 연결 실패 - {e}")
            raise

    def _on_connect(self, client, userdata, flags, rc):
        """
        연결 성공 콜백
        """
        with self.lock:
            if rc == 0:
                self.connected = True
                if DEBUG_MODE:
                    print(f"[MQTT Receiver] ✓ 브로커 연결 성공")

                # 모든 토픽 구독
                for topic_name, topic in MQTT_TOPICS.items():
                    self.client.subscribe(topic)
                    if DEBUG_MODE:
                        print(f"[MQTT Receiver] 구독: {topic}")
            else:
                self.connected = False
                print(f"[MQTT Receiver] ✗ 연결 실패 - 코드: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """
        연결 해제 콜백
        """
        with self.lock:
            self.connected = False

        if rc != 0:
            print(f"[MQTT Receiver] 예기치 않은 연결 해제 - 코드: {rc}")

    def _on_message(self, client, userdata, msg):
        """
        메시지 수신 콜백
        """
        try:
            with self.lock:
                self.messages_received += 1
                import time
                self.last_message_time = time.time()

            # JSON 파싱
            payload = json.loads(msg.payload.decode('utf-8'))

            # 토픽별 처리
            if msg.topic == MQTT_TOPICS["count"]:
                self._handle_count_update(payload)

            elif msg.topic == MQTT_TOPICS["batch_complete"]:
                self._handle_batch_complete(payload)

            elif msg.topic == MQTT_TOPICS["status"]:
                self._handle_status_update(payload)

        except json.JSONDecodeError as e:
            print(f"[MQTT Receiver] JSON 파싱 오류: {e}")

        except Exception as e:
            print(f"[MQTT Receiver] 메시지 처리 오류: {e}")

    def _handle_count_update(self, payload):
        """
        카운트 업데이트 처리

        Args:
            payload (dict): 메시지 데이터
        """
        count = payload.get("count", 0)
        boxes = payload.get("boxes", [])

        if DEBUG_MODE:
            print(f"[MQTT Receiver] 카운트 수신: {count}개")

        # 콜백 호출
        if self.on_count_update:
            self.on_count_update(count, boxes)

    def _handle_batch_complete(self, payload):
        """
        팬 확정 처리

        Args:
            payload (dict): 메시지 데이터
        """
        final_count = payload.get("final_count", 0)

        if DEBUG_MODE:
            print(f"[MQTT Receiver] 팬 확정 수신: {final_count}개")

        # 콜백 호출
        if self.on_batch_complete:
            self.on_batch_complete(final_count)

    def _handle_status_update(self, payload):
        """
        상태 업데이트 처리

        Args:
            payload (dict): 메시지 데이터
        """
        if DEBUG_MODE:
            print(f"[MQTT Receiver] 상태 수신: {payload}")

        # 콜백 호출
        if self.on_status_update:
            self.on_status_update(payload)

    def is_connected(self):
        """
        연결 상태 확인

        Returns:
            bool: 연결 여부
        """
        with self.lock:
            return self.connected

    def get_stats(self):
        """
        수신 통계 반환

        Returns:
            dict: 통계 정보
        """
        with self.lock:
            return {
                "connected": self.connected,
                "messages_received": self.messages_received,
                "last_message_time": self.last_message_time
            }

    def disconnect(self):
        """MQTT 클라이언트 종료"""
        if self.client is not None:
            self.client.loop_stop()
            self.client.disconnect()
            if DEBUG_MODE:
                print("[MQTT Receiver] 연결 종료")


# 테스트 코드
if __name__ == "__main__":
    import time

    print("MQTT 수신기 테스트 시작...")
    print("주의: MQTT 브로커와 엣지 디바이스가 실행 중이어야 합니다.\n")

    # 콜백 함수
    def on_count(count, boxes):
        print(f"✓ 카운트 업데이트: {count}개, 박스: {len(boxes)}개")

    def on_batch(final_count):
        print(f"✓ 팬 확정: {final_count}개")

    def on_status(status):
        print(f"✓ 상태: {status}")

    # 수신기 생성
    receiver = MQTTReceiver(
        on_count_update=on_count,
        on_batch_complete=on_batch,
        on_status_update=on_status
    )

    # 연결
    try:
        receiver.connect()
        time.sleep(2)

        if receiver.is_connected():
            print("✓ MQTT 브로커 연결 성공\n")
            print("메시지 수신 대기 중... (Ctrl+C로 종료)\n")

            # 30초 대기
            for i in range(30):
                time.sleep(1)
                if i % 5 == 0:
                    stats = receiver.get_stats()
                    print(f"통계: {stats}")

        else:
            print("✗ MQTT 브로커 연결 실패")

    except KeyboardInterrupt:
        print("\n\n사용자가 중단함")

    finally:
        receiver.disconnect()
        print("\nMQTT 수신기 테스트 완료")
