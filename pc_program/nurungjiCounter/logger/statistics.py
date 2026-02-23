"""
누룽지 생산량 카운팅 시스템 - 통계 관리
통계 계산 및 JSON 저장
"""

import json
import os
from datetime import datetime, timedelta
from ..config import LOG_DIR, STATISTICS_FILE


class Statistics:
    """
    통계 관리 클래스
    """

    def __init__(self, stats_dir=None, stats_file=None):
        """
        통계 관리자 초기화

        Args:
            stats_dir (str): 통계 디렉토리
            stats_file (str): 통계 파일명
        """
        self.stats_dir = stats_dir or LOG_DIR
        self.stats_file = stats_file or STATISTICS_FILE
        self.stats_path = os.path.join(self.stats_dir, self.stats_file)

        # 디렉토리 생성
        os.makedirs(self.stats_dir, exist_ok=True)

        # 통계 데이터
        self.data = self._load_statistics()

    def _load_statistics(self):
        """
        통계 파일 로드

        Returns:
            dict: 통계 데이터
        """
        if os.path.exists(self.stats_path):
            try:
                with open(self.stats_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[Statistics] 통계 로드 실패: {e}")

        # 기본 구조
        return {
            "daily": {},    # 일별 통계
            "monthly": {},  # 월별 통계
            "total": {      # 전체 통계
                "batches": 0,
                "production": 0
            }
        }

    def save_statistics(self):
        """
        통계 파일 저장

        Returns:
            bool: 성공 여부
        """
        try:
            with open(self.stats_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[Statistics] 통계 저장 실패: {e}")
            return False

    def add_batch(self, count, date=None):
        """
        팬 추가 (통계 업데이트)

        Args:
            count (int): 누룽지 개수
            date (datetime): 날짜 (None이면 오늘)
        """
        if date is None:
            date = datetime.now()

        date_str = date.strftime("%Y-%m-%d")
        month_str = date.strftime("%Y-%m")

        # 일별 통계
        if date_str not in self.data["daily"]:
            self.data["daily"][date_str] = {
                "batches": 0,
                "production": 0
            }

        self.data["daily"][date_str]["batches"] += 1
        self.data["daily"][date_str]["production"] += count

        # 월별 통계
        if month_str not in self.data["monthly"]:
            self.data["monthly"][month_str] = {
                "batches": 0,
                "production": 0
            }

        self.data["monthly"][month_str]["batches"] += 1
        self.data["monthly"][month_str]["production"] += count

        # 전체 통계
        self.data["total"]["batches"] += 1
        self.data["total"]["production"] += count

        # 저장
        self.save_statistics()

    def get_daily_stats(self, date=None):
        """
        일별 통계 조회

        Args:
            date (datetime): 날짜 (None이면 오늘)

        Returns:
            dict: 통계 정보
        """
        if date is None:
            date = datetime.now()

        date_str = date.strftime("%Y-%m-%d")

        return self.data["daily"].get(date_str, {
            "batches": 0,
            "production": 0
        })

    def get_weekly_stats(self, end_date=None):
        """
        주간 통계 (최근 7일)

        Args:
            end_date (datetime): 종료 날짜 (None이면 오늘)

        Returns:
            dict: 통계 정보
        """
        if end_date is None:
            end_date = datetime.now()

        total_batches = 0
        total_production = 0

        for i in range(7):
            date = end_date - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")

            day_stats = self.data["daily"].get(date_str, {})
            total_batches += day_stats.get("batches", 0)
            total_production += day_stats.get("production", 0)

        return {
            "period": "최근 7일",
            "batches": total_batches,
            "production": total_production,
            "avg_per_day": round(total_production / 7, 1)
        }

    def get_monthly_stats(self, month=None):
        """
        월별 통계 조회

        Args:
            month (datetime): 월 (None이면 이번 달)

        Returns:
            dict: 통계 정보
        """
        if month is None:
            month = datetime.now()

        month_str = month.strftime("%Y-%m")

        return self.data["monthly"].get(month_str, {
            "batches": 0,
            "production": 0
        })

    def get_total_stats(self):
        """
        전체 통계

        Returns:
            dict: 전체 통계
        """
        return self.data["total"].copy()


# 테스트 코드
if __name__ == "__main__":
    print("통계 관리자 테스트 시작...\n")

    stats = Statistics(stats_dir="/tmp/nurungji_test")

    # 팬 추가
    print("팬 추가 중...")
    stats.add_batch(12)
    stats.add_batch(15)
    stats.add_batch(10)

    # 통계 조회
    print("\n오늘 통계:")
    daily = stats.get_daily_stats()
    print(f"  {daily}")

    print("\n주간 통계:")
    weekly = stats.get_weekly_stats()
    print(f"  {weekly}")

    print("\n전체 통계:")
    total = stats.get_total_stats()
    print(f"  {total}")

    print("\n통계 관리자 테스트 완료")
