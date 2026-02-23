"""
누룽지 생산량 카운팅 시스템 - 생산 로그 기록
CSV 파일로 생산 이력 저장
"""

import csv
import os
from datetime import datetime
from ..config import LOG_DIR, LOG_FILE


class ProductionLogger:
    """
    생산 로그 기록 클래스
    """

    def __init__(self, log_dir=None, log_file=None):
        """
        로거 초기화

        Args:
            log_dir (str): 로그 디렉토리
            log_file (str): 로그 파일명
        """
        self.log_dir = log_dir or LOG_DIR
        self.log_file = log_file or LOG_FILE
        self.log_path = os.path.join(self.log_dir, self.log_file)

        # 로그 디렉토리 생성
        os.makedirs(self.log_dir, exist_ok=True)

        # CSV 헤더 확인 및 생성
        self._ensure_csv_header()

    def _ensure_csv_header(self):
        """
        CSV 파일 헤더 확인 및 생성
        """
        if not os.path.exists(self.log_path):
            with open(self.log_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "날짜",
                    "시간",
                    "팬 번호",
                    "누룽지 개수",
                    "메모"
                ])
            print(f"[Logger] 로그 파일 생성: {self.log_path}")

    def log_batch(self, batch_id, count, notes=""):
        """
        팬 확정 로그 기록

        Args:
            batch_id (int): 팬 번호
            count (int): 누룽지 개수
            notes (str): 메모

        Returns:
            bool: 성공 여부
        """
        try:
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")

            with open(self.log_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    date_str,
                    time_str,
                    batch_id,
                    count,
                    notes
                ])

            return True

        except Exception as e:
            print(f"[Logger] 로그 기록 실패: {e}")
            return False

    def read_logs(self, date=None):
        """
        로그 읽기

        Args:
            date (str): 날짜 (YYYY-MM-DD), None이면 전체

        Returns:
            list: 로그 목록 (dict 리스트)
        """
        if not os.path.exists(self.log_path):
            return []

        logs = []

        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    # 날짜 필터
                    if date and row["날짜"] != date:
                        continue

                    logs.append({
                        "date": row["날짜"],
                        "time": row["시간"],
                        "batch_id": int(row["팬 번호"]),
                        "count": int(row["누룽지 개수"]),
                        "notes": row["메모"]
                    })

        except Exception as e:
            print(f"[Logger] 로그 읽기 실패: {e}")

        return logs

    def get_date_summary(self, date):
        """
        특정 날짜 요약

        Args:
            date (str): 날짜 (YYYY-MM-DD)

        Returns:
            dict: 요약 정보
        """
        logs = self.read_logs(date)

        if not logs:
            return {
                "date": date,
                "total_batches": 0,
                "total_production": 0,
                "avg_per_batch": 0
            }

        total_batches = len(logs)
        total_production = sum(log["count"] for log in logs)

        return {
            "date": date,
            "total_batches": total_batches,
            "total_production": total_production,
            "avg_per_batch": round(total_production / total_batches, 1)
        }

    def export_to_file(self, output_path):
        """
        로그를 다른 파일로 내보내기

        Args:
            output_path (str): 출력 파일 경로

        Returns:
            bool: 성공 여부
        """
        try:
            import shutil
            shutil.copy2(self.log_path, output_path)
            return True
        except Exception as e:
            print(f"[Logger] 내보내기 실패: {e}")
            return False


# 테스트 코드
if __name__ == "__main__":
    print("생산 로거 테스트 시작...\n")

    logger = ProductionLogger(log_dir="/tmp/nurungji_test")

    # 로그 기록
    print("로그 기록 중...")
    logger.log_batch(1, 12, "테스트 팬 1")
    logger.log_batch(2, 15, "테스트 팬 2")
    logger.log_batch(3, 10, "")

    # 로그 읽기
    print("\n로그 읽기...")
    logs = logger.read_logs()
    for log in logs:
        print(f"  {log['date']} {log['time']} - "
              f"팬 #{log['batch_id']}: {log['count']}개")

    # 요약
    today = datetime.now().strftime("%Y-%m-%d")
    summary = logger.get_date_summary(today)
    print(f"\n오늘 요약: {summary}")

    print("\n생산 로거 테스트 완료")
