# CLAUDE.md

This file provides guidance to Claude Code when working with the Nurungji Production Counter project.

## 프로젝트 개요

**누룽지 생산량 자동 카운팅 시스템** - IoT 기반 실시간 생산량 모니터링 시스템

천정에 설치된 라즈베리 파이 카메라로 팬 위 누룽지를 자동 인식하여 실시간 생산량을 카운팅하고, PC GUI로 모니터링 및 통계 관리하는 시스템입니다.

**Language**: Python 3.8+
**Status**: Phase 1 완성 (MVP, 즉시 사용 가능)
**Version**: 1.0.0
**Last Updated**: 2025-02-23

### 핵심 문제 해결
- ❌ **기존**: 팬이 가득 차면 수작업으로 개수를 세야 함 → 실수 가능, 비효율적
- ✅ **해결**: 카메라 자동 인식 → 실시간 카운팅 → 정확한 생산량 통계

### 주요 기능
1. **라즈베리 파이 엣지 디바이스**
   - 실시간 객체 감지 (OpenCV 윤곽선 기반)
   - 무선 작동 (WiFi + 배터리 8시간)
   - MQTT 통신으로 데이터 전송

2. **PC GUI 프로그램**
   - 실시간 팬 위 개수 표시
   - 안정화 알고리즘 (중앙값 필터)
   - 자동/수동 팬 확정
   - 생산량 통계 (일/주/월)

3. **캘리브레이션 도구**
   - 파라미터 조정으로 정확도 최적화
   - AI 학습 불필요

---

## 기술 스택

### 라즈베리 파이 (엣지 디바이스)
- **언어**: Python 3.8+
- **컴퓨터 비전**: OpenCV 4.8+ (윤곽선 감지, AI 학습 불필요)
- **카메라**: picamera2 (Raspberry Pi Camera Module V2)
- **통신**: paho-mqtt 1.6+ (MQTT 프로토콜)
- **기타**: numpy 1.24+

### PC 프로그램
- **언어**: Python 3.8+
- **GUI**: Tkinter (Python 기본 포함)
- **통신**: paho-mqtt 1.6+
- **데이터 처리**: pandas 2.0+, numpy 1.24+
- **이미지**: pillow 10.0+

### 인프라
- **MQTT 브로커**: Mosquitto (로컬 또는 클라우드)
- **통신 프로토콜**: MQTT over WiFi
- **데이터 저장**: CSV 파일 (로그), JSON (통계)
- **배포**: 라즈베리 파이 OS Lite, Windows/Linux PC

### 하드웨어
- Raspberry Pi 4 (4GB) + Camera Module V2
- 보조배터리 20,000mAh (8시간 작동)
- 총 비용: 약 15만원

---

## 개발 환경 설정

### 1. 라즈베리 파이 설정

```bash
# 1) 코드 전송 (PC에서)
scp -r edge_device pi@<라즈베리파이IP>:/home/pi/

# 2) SSH 접속
ssh pi@<라즈베리파이IP>

# 3) 의존성 설치
cd ~/edge_device
pip3 install -r requirements_edge.txt

# 4) 설정 파일 수정
nano config.py
# MQTT_BROKER_ADDRESS를 PC IP로 변경

# 5) 카메라 테스트
python3 test_camera.py

# 6) 메인 프로그램 실행
python3 main.py
```

### 2. PC 프로그램 설정

```bash
# 1) MQTT 브로커 설치 (한 번만)
# Windows: choco install mosquitto
# Linux: sudo apt install mosquitto
# macOS: brew install mosquitto

# 2) 의존성 설치
cd pc_program
pip install -r requirements.txt

# 3) MQTT 브로커 실행 (터미널 1)
mosquitto -v

# 4) GUI 프로그램 실행 (터미널 2)
python main_gui.py
```

### 3. 캘리브레이션 (필수!)

```bash
# 라즈베리 파이에서
cd ~/edge_device
python3 test_camera.py  # 옵션 3 선택

# 누룽지 1개 → 5개 → 10개 순서로 테스트
# config.py 파라미터 조정:
# - MIN_AREA, MAX_AREA (크기 필터)
# - BINARY_THRESHOLD (배경 분리)
```

---

## 프로젝트 구조

```
gamgi/
├── edge_device/              # 라즈베리 파이 코드 (엣지 디바이스)
│   ├── config.py             # ⚙️ 설정 (MQTT, 카메라, 감지 파라미터)
│   ├── camera_capture.py     # 📷 카메라 제어 (picamera2)
│   ├── detector.py           # 🔍 객체 감지 (OpenCV 윤곽선)
│   ├── mqtt_client.py        # 📡 MQTT 통신 (데이터 전송)
│   ├── main.py               # 🚀 메인 루프 (캡처→감지→전송)
│   ├── test_camera.py        # 🧪 테스트 도구 (캘리브레이션 도우미)
│   └── requirements_edge.txt # 의존성 목록
│
├── pc_program/               # PC GUI 프로그램
│   ├── main_gui.py           # 🖥️ Tkinter GUI (메인)
│   ├── requirements.txt      # 의존성 목록
│   └── nurungjiCounter/      # 패키지
│       ├── config.py         # 설정 (MQTT, GUI, 카운팅)
│       ├── settings.py       # 사용자 설정
│       │
│       ├── receiver/         # 📡 MQTT 수신
│       │   ├── mqtt_receiver.py  # MQTT 클라이언트
│       │   └── data_parser.py    # 데이터 파싱
│       │
│       ├── counter/          # 🔢 카운팅 로직 (핵심)
│       │   ├── production_counter.py  # 안정화, 확정 로직
│       │   └── batch_tracker.py       # 팬 단위 추적
│       │
│       ├── logger/           # 📝 로그 및 통계
│       │   ├── production_logger.py   # CSV 로그 기록
│       │   └── statistics.py          # 통계 집계
│       │
│       └── utils/            # 🔔 유틸리티
│           └── notification.py        # 알림 (소리/팝업)
│
├── calibration/              # 🎯 캘리브레이션 도구
│   └── calibration_tool.py   # 파라미터 조정 도구
│
├── docs/                     # 📚 문서
│   ├── HARDWARE_SETUP.md     # 하드웨어 설치 가이드
│   └── CALIBRATION.md        # 캘리브레이션 가이드
│
├── README.md                 # 프로젝트 개요
├── CLAUDE.md                 # Claude Code 가이드 (이 파일)
├── .gitignore                # Git 제외 파일
└── requirements.txt          # 공통 의존성
```

---

## 아키텍처

### 전체 시스템 구조

```
[천정 - 라즈베리 파이]
     ↓
1. 카메라로 팬 촬영 (1초 간격)
     ↓
2. OpenCV 객체 감지 (윤곽선 → 크기 필터)
     ↓
3. MQTT로 개수 전송 (WiFi)
     ↓
[PC - MQTT 브로커]
     ↓
4. MQTT 수신
     ↓
5. 안정화 (중앙값 필터, 5개 프레임)
     ↓
6. GUI에 실시간 표시
     ↓
7. 팬 확정 (자동/수동)
     ↓
8. CSV 로그 기록 + 통계 업데이트
```

### 주요 컴포넌트

#### 1. 엣지 디바이스 (edge_device/)
- **역할**: 카메라 촬영, 객체 감지, 데이터 전송
- **처리**: 로컬에서 OpenCV 감지 실행 (영상 전송 안함 → 대역폭 절약)
- **전원**: 배터리 구동 (8시간)

#### 2. MQTT 통신
- **프로토콜**: MQTT (경량, IoT 최적화)
- **토픽**:
  - `nurungji/count`: 실시간 카운트
  - `nurungji/batch_complete`: 팬 확정 신호
  - `nurungji/status`: 디바이스 상태

#### 3. PC 카운팅 로직 (production_counter.py)
- **안정화**: 최근 5개 프레임의 중앙값 사용 (노이즈 제거)
- **자동 확정**: 개수가 0이 되면 자동으로 팬 확정
- **수동 확정**: 사용자가 "팬 확정" 버튼 클릭

#### 4. GUI (main_gui.py)
- **표시**: 현재 개수, 안정화된 개수, 오늘 생산량
- **기능**: 팬 확정, 초기화, 통계 조회, 로그 확인

### 데이터 흐름

```python
# MQTT 메시지 포맷 (JSON)
{
  "timestamp": 1708422615,
  "count": 12,
  "stable_count": 12,
  "boxes": [
    {"x": 100, "y": 150, "w": 50, "h": 50, "area": 2500},
    ...
  ]
}
```

### 데이터 저장

#### CSV 로그 (production_log.csv)
```csv
timestamp,batch_id,count
2025-02-23T14:30:15,1,12
2025-02-23T14:35:20,2,15
```

#### 통계 JSON (statistics.json)
```json
{
  "daily": {
    "2025-02-23": {"production": 234, "batches": 19}
  },
  "total": {"production": 5420, "batches": 387}
}
```

---

## 핵심 알고리즘 설명

### 1. 객체 감지 (detector.py)

**OpenCV 윤곽선 기반 - AI 학습 불필요**

```python
# 작동 방식
1. 그레이스케일 변환 (컬러 → 흑백)
2. 이진화 (BINARY_THRESHOLD 기준으로 배경 분리)
3. 윤곽선 찾기 (검은색 덩어리 검출)
4. 필터링:
   - 크기: MIN_AREA ≤ 면적 ≤ MAX_AREA
   - 종횡비: 0.5 ≤ 가로/세로 ≤ 2.0
5. 유효한 객체 개수 반환
```

**캘리브레이션 파라미터 (config.py):**
```python
BINARY_THRESHOLD = 127    # 배경 분리 임계값 (0~255)
MIN_AREA = 500            # 최소 면적 (픽셀²)
MAX_AREA = 5000           # 최대 면적 (픽셀²)
MIN_ASPECT_RATIO = 0.5    # 최소 가로/세로 비율
MAX_ASPECT_RATIO = 2.0    # 최대 가로/세로 비율
```

### 2. 안정화 알고리즘 (production_counter.py)

**노이즈 제거를 위한 중앙값 필터**

```python
# 최근 5개 프레임: [12, 13, 12, 12, 13]
# 중앙값: 12
# → GUI에 "안정화: 12개" 표시

def update_count(new_count):
    count_history.append(new_count)
    if len(count_history) > 5:
        count_history.pop(0)

    stable_count = median(count_history)  # 중앙값 사용
    return stable_count
```

**왜 중앙값?**
- 평균보다 이상값(outlier)에 강함
- 일시적인 오감지 무시
- 실시간 처리에 적합

### 3. 자동 팬 확정

```python
# 조건: 이전에 개수가 있었는데 현재 0이 됨
if previous_stable_count > 0 and stable_count == 0:
    confirm_batch()  # 자동 확정
```

---

## 개발 작업

### 테스트 실행

#### 엣지 디바이스 테스트
```bash
cd edge_device

# 카메라 테스트
python3 test_camera.py
# 옵션 1: 기본 동작 확인
# 옵션 2: 감지 테스트 (10개 프레임)
# 옵션 3: 캘리브레이션 도우미 (실시간)

# 개별 모듈 테스트
python3 camera_capture.py    # 카메라
python3 detector.py          # 감지기
python3 mqtt_client.py       # MQTT (브로커 필요)
```

#### PC 프로그램 테스트
```bash
cd pc_program/nurungjiCounter

# 개별 모듈 테스트
python -m counter.production_counter  # 카운터
python -m receiver.mqtt_receiver      # MQTT 수신
```

### 디버깅

#### 엣지 디바이스
```python
# edge_device/config.py
DEBUG_MODE = True              # 상세 로그 출력
SAVE_DEBUG_IMAGES = True       # 감지 결과 이미지 저장
DEBUG_IMAGE_PATH = "/tmp/nurungji_debug"
```

#### PC 프로그램
```python
# pc_program/nurungjiCounter/config.py
DEBUG_MODE = True              # 상세 로그
```

#### 로그 확인
```bash
# 라즈베리 파이
tail -f /tmp/nurungji_debug/*.jpg  # 디버그 이미지

# PC
tail -f logs/production_log.csv    # 생산 로그
```

### 일반적인 문제 해결

#### 문제 1: 감지 안됨
```python
# config.py 수정
MIN_AREA = 500 → 300  # 더 작은 객체도 인식
```

#### 문제 2: 너무 많이 감지됨
```python
# config.py 수정
MIN_AREA = 500 → 1000  # 더 큰 객체만 인식
BINARY_THRESHOLD = 127 → 150  # 더 어두운 것만 인식
```

#### 문제 3: MQTT 연결 실패
```bash
# PC에서 브로커 실행 확인
mosquitto -v

# 방화벽 확인 (1883 포트)
# config.py에서 IP 주소 확인
```

---

## 중요 구현 사항

### 코딩 컨벤션
- **들여쓰기**: 스페이스 4개
- **변수명**: snake_case (Python PEP 8)
- **클래스명**: PascalCase
- **파일명**: snake_case.py
- **주석**: 독스트링 (함수/클래스 설명)

### 보안 고려사항
- **MQTT 인증**: 현재 인증 없음 (로컬 네트워크 전용)
- **민감 정보**: IP 주소는 config.py에 하드코딩 (로컬 네트워크만 사용)
- **향후 개선**: MQTT TLS/SSL 인증 추가 고려

### 성능 최적화
- **촬영 간격**: 1초 (배터리 절약 시 2~3초로 조정 가능)
- **영상 전송 안함**: 감지 결과만 전송 (대역폭 절약)
- **로컬 처리**: 엣지에서 OpenCV 실행 (서버 부하 없음)

### 알려진 제약사항

#### 1. 조명 의존성
- **문제**: 조명이 계속 변하면 정확도 낮아짐
- **해결**: 일정한 조명 환경 유지 또는 적응형 이진화 사용

#### 2. 겹침 처리
- **문제**: 누룽지가 심하게 겹치면 1개로 인식될 수 있음
- **해결**: Phase 3 (AI 학습) 고려

#### 3. 배터리 수명
- **문제**: 8시간 후 배터리 교체 필요
- **해결**: 여분 배터리 준비 또는 충전식 사용

---

## Git 작업 흐름

### 브랜치 전략
- `master` - 메인 브랜치 (안정 버전)
- `feature/*` - 기능 개발 (예: feature/ai-detection)
- `fix/*` - 버그 수정

### 커밋 메시지 형식
```
<type>: <description>

[optional body]

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Type:**
- `feat`: 새 기능 (예: feat: 자동 팬 확정 감지 추가)
- `fix`: 버그 수정 (예: fix: MQTT 재연결 오류 수정)
- `docs`: 문서 수정
- `refactor`: 리팩토링
- `test`: 테스트 추가
- `chore`: 설정 변경

### 현재 커밋 이력
```
60a2d86 fix: PC GUI 프로그램 메인 파일 추가
b985edc feat: 누룽지 생산량 자동 카운팅 시스템 초기 구현
```

---

## 자주 묻는 질문 (FAQ)

### Q1: AI 학습이 필요한가요?
**A**: 아니요, 현재 구현은 OpenCV 윤곽선 감지를 사용하므로 **AI 학습이 불필요**합니다. 파라미터 캘리브레이션(10분)만 하면 됩니다. 정확도가 80% 이하일 경우에만 Phase 3 (AI 학습)을 고려하세요.

### Q2: 정확도는 얼마나 되나요?
**A**:
- **OpenCV (현재)**: 85~95% (단순 배경, 일정 조명)
- **AI (Phase 3)**: 95~98% (복잡한 환경, 겹침 처리)

### Q3: 배터리는 얼마나 가나요?
**A**: 20,000mAh 배터리로 약 8시간 작동합니다. 촬영 간격을 2~3초로 늘리면 더 오래 사용 가능합니다.

### Q4: 인터넷이 필요한가요?
**A**: 아니요, 로컬 WiFi만 있으면 됩니다. 라즈베리 파이와 PC가 같은 네트워크에 있으면 됩니다.

### Q5: 여러 팬을 동시에 모니터링할 수 있나요?
**A**: 현재는 1개 팬만 지원합니다. 여러 팬을 모니터링하려면 라즈베리 파이를 추가로 설치하고 각각 다른 DEVICE_ID를 설정하면 됩니다.

### Q6: PC가 꺼지면 데이터가 사라지나요?
**A**: 아니요, CSV 로그와 JSON 통계 파일에 저장되므로 PC를 재시작해도 데이터가 유지됩니다.

---

## 다음 개발 계획 (로드맵)

### Phase 2: 고도화 (선택사항)
- [ ] 자동 팬 확정 감지 개선 (화면에서 사라짐 감지)
- [ ] 설정 UI 추가 (GUI에서 파라미터 조정)
- [ ] 통계 차트 시각화 (matplotlib)
- [ ] 알림 기능 강화 (이메일, Slack 연동)

### Phase 3: AI 고정확도 (선택사항)
- [ ] YOLOv8-Nano 모델 학습
- [ ] TFLite 변환 및 라즈베리 파이 배포
- [ ] 정확도 95~98% 달성
- [ ] 겹친 누룽지 정확 분리

### 기타 개선사항
- [ ] 모바일 앱 (React Native)
- [ ] 클라우드 연동 (Firebase)
- [ ] 다중 카메라 지원
- [ ] 실시간 영상 스트리밍

---

## 참고 자료

### 공식 문서
- [OpenCV Documentation](https://docs.opencv.org/)
- [Picamera2 Documentation](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
- [MQTT Protocol](https://mqtt.org/)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)

### 내부 문서
- [하드웨어 설치 가이드](docs/HARDWARE_SETUP.md)
- [캘리브레이션 가이드](docs/CALIBRATION.md)
- [README](README.md)

### 관련 프로젝트
- [Raspberry Pi Projects](https://projects.raspberrypi.org/)
- [OpenCV Contour Detection Tutorial](https://docs.opencv.org/4.x/d4/d73/tutorial_py_contours_begin.html)

---

## 중요 파일 위치 (빠른 참조)

### 설정 파일
- `edge_device/config.py` - 라즈베리 파이 설정 (MQTT, 카메라, 감지)
- `pc_program/nurungjiCounter/config.py` - PC 프로그램 설정

### 핵심 로직
- `edge_device/detector.py` - 객체 감지 알고리즘 (OpenCV)
- `pc_program/nurungjiCounter/counter/production_counter.py` - 카운팅 로직

### 테스트 도구
- `edge_device/test_camera.py` - 카메라 테스트 및 캘리브레이션
- `calibration/calibration_tool.py` - 파라미터 조정 도구

### 문서
- `README.md` - 프로젝트 개요
- `docs/HARDWARE_SETUP.md` - 하드웨어 설치
- `docs/CALIBRATION.md` - 캘리브레이션

---

## 빠른 명령어 치트시트

```bash
# === 라즈베리 파이 ===
# 코드 전송
scp -r edge_device pi@<IP>:/home/pi/

# SSH 접속
ssh pi@<IP>

# 프로그램 실행
cd ~/edge_device && python3 main.py

# 카메라 테스트
python3 test_camera.py

# === PC ===
# MQTT 브로커 실행
mosquitto -v

# GUI 실행
cd pc_program && python main_gui.py

# === Git ===
# 상태 확인
git status

# 커밋
git add . && git commit -m "feat: 새 기능"

# 로그 확인
git log --oneline
```

---

**마지막 업데이트**: 2025-02-23
**버전**: 1.0.0
**상태**: Phase 1 완성 (MVP, 프로덕션 레디)

---

## Claude Code 작업 시 주의사항

1. **파일 수정 전 확인**
   - `edge_device/config.py` 수정 시 라즈베리 파이에 반영 필요
   - `pc_program/nurungjiCounter/config.py` 수정 시 GUI 재시작 필요

2. **테스트 필수 파일**
   - 감지 로직 수정 시: `detector.py` → `test_camera.py`로 검증
   - 카운팅 로직 수정 시: `production_counter.py` → 단위 테스트 실행

3. **커밋 전 확인사항**
   - 디버그 모드 비활성화 (`DEBUG_MODE = False`)
   - 디버그 이미지 저장 비활성화 (`SAVE_DEBUG_IMAGES = False`)
   - 불필요한 로그 제거

4. **문서 업데이트**
   - 주요 기능 추가/수정 시 README.md 업데이트
   - 새 파라미터 추가 시 CALIBRATION.md 업데이트
   - 이 파일(CLAUDE.md)도 함께 업데이트

5. **의존성 관리**
   - 새 라이브러리 추가 시 requirements.txt 업데이트
   - 라즈베리 파이 전용 라이브러리는 requirements_edge.txt에만 추가
