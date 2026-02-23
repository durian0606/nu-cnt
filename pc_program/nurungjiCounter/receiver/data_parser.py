"""
누룽지 생산량 카운팅 시스템 - 데이터 파싱 모듈
MQTT 메시지 데이터 검증 및 변환
"""

from datetime import datetime


class DataParser:
    """
    데이터 파싱 및 검증 클래스
    """

    @staticmethod
    def parse_count_message(payload):
        """
        카운트 메시지 파싱

        Args:
            payload (dict): MQTT 메시지 페이로드

        Returns:
            dict: 파싱된 데이터
        """
        try:
            return {
                "timestamp": payload.get("timestamp", datetime.now().timestamp()),
                "count": int(payload.get("count", 0)),
                "stable_count": int(payload.get("stable_count", payload.get("count", 0))),
                "boxes": payload.get("boxes", [])
            }
        except (ValueError, TypeError) as e:
            print(f"[DataParser] 카운트 메시지 파싱 오류: {e}")
            return None

    @staticmethod
    def parse_batch_message(payload):
        """
        팬 확정 메시지 파싱

        Args:
            payload (dict): MQTT 메시지 페이로드

        Returns:
            dict: 파싱된 데이터
        """
        try:
            return {
                "timestamp": payload.get("timestamp", datetime.now().timestamp()),
                "final_count": int(payload.get("final_count", 0))
            }
        except (ValueError, TypeError) as e:
            print(f"[DataParser] 팬 확정 메시지 파싱 오류: {e}")
            return None

    @staticmethod
    def parse_status_message(payload):
        """
        상태 메시지 파싱

        Args:
            payload (dict): MQTT 메시지 페이로드

        Returns:
            dict: 파싱된 데이터
        """
        try:
            return {
                "timestamp": payload.get("timestamp", datetime.now().timestamp()),
                "battery_level": payload.get("battery_level"),
                "cpu_temperature": payload.get("cpu_temperature"),
                "uptime": payload.get("uptime"),
                "device_type": payload.get("device_type", "unknown")
            }
        except Exception as e:
            print(f"[DataParser] 상태 메시지 파싱 오류: {e}")
            return None

    @staticmethod
    def format_timestamp(timestamp):
        """
        타임스탬프 포맷팅

        Args:
            timestamp (float): Unix 타임스탬프

        Returns:
            str: 포맷된 시간 문자열
        """
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return "N/A"
