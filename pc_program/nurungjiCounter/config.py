"""
누룽지 생산량 카운팅 시스템 - PC 프로그램 전역 설정
"""

# ============================================
# MQTT 브로커 설정
# ============================================
MQTT_BROKER_ADDRESS = "localhost"  # 또는 "192.168.1.100"
MQTT_BROKER_PORT = 1883
MQTT_TOPICS = {
    "count": "nurungji/count",
    "batch_complete": "nurungji/batch_complete",
    "status": "nurungji/status",
    "calibration_image": "nurungji/calibration/image"  # 캘리브레이션 이미지 수신
}

# ============================================
# 카운팅 설정
# ============================================
# 안정화 윈도우 크기 (최근 N개 측정값 평균)
STABILIZATION_WINDOW = 5

# 자동 팬 확정 임계값
AUTO_CONFIRM_THRESHOLD = 0  # 개수가 0이 되면 자동 확정
AUTO_CONFIRM_ENABLED = True  # 자동 확정 활성화

# ============================================
# 로그 설정
# ============================================
LOG_DIR = "logs"  # 로그 저장 디렉토리
LOG_FILE = "production_log.csv"  # CSV 로그 파일
STATISTICS_FILE = "statistics.json"  # 통계 JSON 파일

# ============================================
# GUI 설정
# ============================================
GUI_UPDATE_INTERVAL = 100  # 밀리초 (GUI 업데이트 주기)
WINDOW_TITLE = "🍚 누룽지 생산량 자동 카운팅 시스템"
WINDOW_SIZE = "800x600"

# 색상 테마
COLORS = {
    "primary": "#2196F3",
    "success": "#4CAF50",
    "warning": "#FF9800",
    "danger": "#F44336",
    "bg_light": "#F5F5F5",
    "bg_dark": "#212121",
    "text": "#212121"
}

# ============================================
# 알림 설정
# ============================================
ENABLE_SOUND = True  # 소리 알림
ENABLE_POPUP = False  # 팝업 알림

# ============================================
# 디버그 설정
# ============================================
DEBUG_MODE = True
