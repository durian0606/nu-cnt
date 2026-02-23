"""
누룽지 생산량 카운팅 시스템 - 팬 추적 모듈
팬 단위 추적 및 이력 관리
"""

from datetime import datetime


class BatchTracker:
    """
    팬 추적 및 이력 관리 클래스
    """

    def __init__(self):
        """추적기 초기화"""
        self.batches = []  # 모든 팬 이력
        self.current_batch_id = 0

    def create_batch(self, count):
        """
        새 팬 생성

        Args:
            count (int): 팬에 담긴 누룽지 개수

        Returns:
            dict: 생성된 팬 정보
        """
        self.current_batch_id += 1

        batch = {
            "id": self.current_batch_id,
            "count": count,
            "timestamp": datetime.now(),
            "notes": ""
        }

        self.batches.append(batch)
        return batch

    def get_batch(self, batch_id):
        """
        특정 팬 조회

        Args:
            batch_id (int): 팬 ID

        Returns:
            dict: 팬 정보 (없으면 None)
        """
        for batch in self.batches:
            if batch["id"] == batch_id:
                return batch
        return None

    def get_recent_batches(self, limit=10):
        """
        최근 팬 목록

        Args:
            limit (int): 반환할 최대 개수

        Returns:
            list: 최근 팬 목록
        """
        return self.batches[-limit:]

    def get_batches_by_date(self, target_date):
        """
        특정 날짜의 팬 목록

        Args:
            target_date (date): 날짜

        Returns:
            list: 해당 날짜의 팬 목록
        """
        return [
            b for b in self.batches
            if b["timestamp"].date() == target_date
        ]

    def update_notes(self, batch_id, notes):
        """
        팬 메모 업데이트

        Args:
            batch_id (int): 팬 ID
            notes (str): 메모

        Returns:
            bool: 성공 여부
        """
        batch = self.get_batch(batch_id)
        if batch:
            batch["notes"] = notes
            return True
        return False

    def get_total_count(self):
        """
        총 팬 개수

        Returns:
            int: 총 팬 개수
        """
        return len(self.batches)

    def get_total_production(self):
        """
        총 생산량

        Returns:
            int: 총 누룽지 개수
        """
        return sum(b["count"] for b in self.batches)
