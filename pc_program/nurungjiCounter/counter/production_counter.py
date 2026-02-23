"""
누룽지 생산량 카운팅 시스템 - 생산량 카운팅 로직
안정화 알고리즘 및 팬 확정 처리
"""

import numpy as np
from datetime import datetime
from ..config import STABILIZATION_WINDOW, AUTO_CONFIRM_ENABLED, AUTO_CONFIRM_THRESHOLD


class ProductionCounter:
    """
    생산량 카운팅 및 안정화 클래스
    """

    def __init__(self):
        """카운터 초기화"""
        # 현재 상태
        self.current_count = 0          # 현재 프레임 카운트
        self.stable_count = 0           # 안정화된 카운트
        self.count_history = []         # 최근 카운트 이력 (안정화용)

        # 확정된 팬 목록
        self.confirmed_batches = []     # [{"count": int, "timestamp": datetime}, ...]

        # 통계
        self.total_production = 0       # 총 생산량
        self.total_batches = 0          # 총 팬 수

        # 이전 안정화 값 (자동 확정 감지용)
        self.previous_stable_count = 0

    def update_count(self, new_count):
        """
        카운트 업데이트 및 안정화

        Args:
            new_count (int): 새로운 카운트

        Returns:
            dict: 업데이트 결과
        """
        # 현재 카운트 저장
        self.current_count = new_count

        # 이력에 추가
        self.count_history.append(new_count)

        # 윈도우 크기 유지
        if len(self.count_history) > STABILIZATION_WINDOW:
            self.count_history.pop(0)

        # 이전 안정화 값 저장
        self.previous_stable_count = self.stable_count

        # 안정화된 카운트 계산 (중앙값 사용)
        if len(self.count_history) >= 3:
            self.stable_count = int(np.median(self.count_history))
        else:
            self.stable_count = new_count

        # 자동 팬 확정 감지
        auto_confirmed = False
        if AUTO_CONFIRM_ENABLED:
            auto_confirmed = self._check_auto_confirm()

        return {
            "current_count": self.current_count,
            "stable_count": self.stable_count,
            "auto_confirmed": auto_confirmed
        }

    def _check_auto_confirm(self):
        """
        자동 팬 확정 조건 확인

        Returns:
            bool: 자동 확정 여부
        """
        # 조건: 이전에 개수가 있었는데 현재 0이 됨
        if (self.previous_stable_count > 0 and
            self.stable_count == AUTO_CONFIRM_THRESHOLD):

            # 자동 확정 실행
            self.confirm_batch()
            return True

        return False

    def confirm_batch(self, manual_count=None):
        """
        팬 확정 (개수 기록 및 초기화)

        Args:
            manual_count (int): 수동 입력 개수 (None이면 stable_count 사용)

        Returns:
            dict: 확정된 팬 정보
        """
        # 확정 개수 결정
        final_count = manual_count if manual_count is not None else self.stable_count

        # 개수가 0이면 확정하지 않음
        if final_count <= 0:
            return None

        # 팬 정보 생성
        batch = {
            "count": final_count,
            "timestamp": datetime.now()
        }

        # 목록에 추가
        self.confirmed_batches.append(batch)

        # 통계 업데이트
        self.total_production += final_count
        self.total_batches += 1

        # 현재 상태 초기화
        self.current_count = 0
        self.stable_count = 0
        self.previous_stable_count = 0
        self.count_history.clear()

        return batch

    def get_today_statistics(self):
        """
        오늘 생산량 통계

        Returns:
            dict: 통계 정보
        """
        today = datetime.now().date()

        # 오늘 확정된 팬들
        today_batches = [
            b for b in self.confirmed_batches
            if b["timestamp"].date() == today
        ]

        # 통계 계산
        today_production = sum(b["count"] for b in today_batches)
        today_batch_count = len(today_batches)

        # 평균
        avg_per_batch = (
            today_production / today_batch_count
            if today_batch_count > 0 else 0
        )

        return {
            "date": today.isoformat(),
            "total_production": today_production,
            "total_batches": today_batch_count,
            "avg_per_batch": round(avg_per_batch, 1)
        }

    def get_week_statistics(self):
        """
        주간 생산량 통계

        Returns:
            dict: 통계 정보
        """
        from datetime import timedelta

        today = datetime.now().date()
        week_ago = today - timedelta(days=7)

        # 최근 7일 팬들
        week_batches = [
            b for b in self.confirmed_batches
            if week_ago <= b["timestamp"].date() <= today
        ]

        # 통계 계산
        week_production = sum(b["count"] for b in week_batches)
        week_batch_count = len(week_batches)

        # 일평균
        avg_per_day = week_production / 7

        return {
            "period": f"{week_ago} ~ {today}",
            "total_production": week_production,
            "total_batches": week_batch_count,
            "avg_per_day": round(avg_per_day, 1)
        }

    def get_all_statistics(self):
        """
        전체 통계

        Returns:
            dict: 전체 통계 정보
        """
        return {
            "total_production": self.total_production,
            "total_batches": self.total_batches,
            "avg_per_batch": (
                round(self.total_production / self.total_batches, 1)
                if self.total_batches > 0 else 0
            )
        }

    def get_current_state(self):
        """
        현재 상태 반환

        Returns:
            dict: 현재 상태
        """
        return {
            "current_count": self.current_count,
            "stable_count": self.stable_count,
            "count_history": self.count_history.copy()
        }

    def reset_all(self):
        """
        모든 데이터 초기화 (주의: 확정된 팬 포함)
        """
        self.current_count = 0
        self.stable_count = 0
        self.previous_stable_count = 0
        self.count_history.clear()
        self.confirmed_batches.clear()
        self.total_production = 0
        self.total_batches = 0

    def reset_current(self):
        """
        현재 팬만 초기화 (확정된 팬은 유지)
        """
        self.current_count = 0
        self.stable_count = 0
        self.previous_stable_count = 0
        self.count_history.clear()


# 테스트 코드
if __name__ == "__main__":
    print("생산량 카운터 테스트 시작...\n")

    counter = ProductionCounter()

    # 시뮬레이션: 누룽지 추가
    print("=== 시나리오 1: 누룽지 추가 (1개씩) ===")
    for i in range(1, 6):
        result = counter.update_count(i)
        print(f"추가 {i}개 → 현재: {result['current_count']}, "
              f"안정화: {result['stable_count']}")

    # 팬 확정
    print("\n팬 확정...")
    batch = counter.confirm_batch()
    print(f"✓ 확정: {batch['count']}개 @ {batch['timestamp']}")

    # 새 팬 시작
    print("\n=== 시나리오 2: 새 팬 ===")
    for i in range(1, 11):
        result = counter.update_count(i)
        print(f"추가 {i}개 → 안정화: {result['stable_count']}")

    batch = counter.confirm_batch()
    print(f"✓ 확정: {batch['count']}개")

    # 통계
    print("\n=== 통계 ===")
    today_stats = counter.get_today_statistics()
    print(f"오늘: {today_stats}")

    all_stats = counter.get_all_statistics()
    print(f"전체: {all_stats}")

    print("\n생산량 카운터 테스트 완료")
