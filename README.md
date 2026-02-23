# 누룽지 생산량 자동 카운팅 시스템

천정에 설치된 카메라로 누룽지 제품을 자동 인식하여 실시간 생산량을 카운팅하는 IoT 시스템입니다.

## 📋 개요

### 문제점
- 누룽지 제작 후 스테인레스 사각 팬에 1개씩 쌓음
- 팬이 가득 차면 (4~30개, 가변적) 수작업으로 개수를 세야 함
- **결과**: 실수 가능, 비효율적, 생산량 통계 부정확

### 해결책
**라즈베리 파이 엣지 디바이스 + PC GUI 시스템**으로 자동 카운팅 및 통계 관리

## ✨ 주요 기능

### 엣지 디바이스 (라즈베리 파이)
- ✅ **실시간 자동 카운팅**: OpenCV 기반 객체 감지
- ✅ **무선 작동**: WiFi + 배터리 (8시간)
- ✅ **천정 설치**: 케이블 없이 깔끔한 설치

### PC 프로그램
- ✅ **실시간 모니터링**: 팬 위 누룽지 개수 표시
- ✅ **안정화 알고리즘**: 노이즈 제거 (중앙값 필터)
- ✅ **자동/수동 팬 확정**: 개수 확정 및 로그 기록
- ✅ **생산량 통계**: 일/주/월 단위 통계 및 평균
- ✅ **사용자 친화적 GUI**: Tkinter 기반 직관적 인터페이스

## 🛠️ 시스템 구성

```
[천정]
라즈베리 파이 4 + 카메라 모듈 (배터리 구동)
  ↓ (실시간 영상 캡처 및 객체 감지)
  ↓ (감지 결과만 전송 - 네트워크 대역폭 절약)
  ↓ WiFi (MQTT Protocol)
  ↓
[PC]
Python GUI 프로그램 (데이터 수신, 표시, 로그 기록)
```

### 하드웨어
| 품목 | 모델 | 가격 |
|------|------|------|
| 싱글보드 컴퓨터 | Raspberry Pi 4 (4GB) | 6만원 |
| 카메라 모듈 | Pi Camera Module V2 | 3만원 |
| 보조배터리 | 20,000mAh (5V/3A) | 3만원 |
| 케이스 + 마운트 | - | 2만원 |
| MicroSD 카드 | 32GB | 1만원 |
| **합계** | | **약 15만원** |

### 소프트웨어
- **엣지**: Python 3.8+, OpenCV, picamera2, paho-mqtt
- **PC**: Python 3.8+, Tkinter, paho-mqtt, pandas
- **통신**: MQTT (Mosquitto)

## 🚀 빠른 시작

### 1. 라즈베리 파이 설정

```bash
# 의존성 설치
cd edge_device
pip3 install -r requirements_edge.txt

# 설정 파일 수정 (PC IP 주소)
nano config.py  # MQTT_BROKER_ADDRESS 변경

# 실행
python3 main.py
```

### 2. PC 프로그램 설정

```bash
# MQTT 브로커 설치 (한 번만)
# Windows: choco install mosquitto
# Linux: sudo apt install mosquitto
# macOS: brew install mosquitto

# 의존성 설치
cd pc_program
pip install -r requirements.txt

# 실행
python main_gui.py
```

## 📖 상세 문서

- **[하드웨어 설치 가이드](docs/HARDWARE_SETUP.md)**: 부품 조립, 천정 설치, 네트워크 설정
- **[캘리브레이션 가이드](docs/CALIBRATION.md)**: 파라미터 조정, 정확도 최적화

## 📁 프로젝트 구조

```
nurungji_production_counter/
├── edge_device/              # 라즈베리 파이 코드
│   ├── config.py             # 설정
│   ├── camera_capture.py     # 카메라
│   ├── detector.py           # 객체 감지 (OpenCV)
│   ├── mqtt_client.py        # MQTT 통신
│   ├── main.py               # 메인 루프
│   ├── test_camera.py        # 테스트 도구
│   └── requirements_edge.txt
│
├── pc_program/               # PC 프로그램
│   ├── nurungjiCounter/
│   │   ├── config.py
│   │   ├── receiver/         # MQTT 수신
│   │   ├── counter/          # 카운팅 로직
│   │   ├── logger/           # 로그 및 통계
│   │   └── utils/            # 알림
│   ├── main_gui.py           # GUI
│   └── requirements.txt
│
├── calibration/              # 캘리브레이션 도구
│   └── calibration_tool.py
│
├── docs/                     # 문서
│   ├── HARDWARE_SETUP.md
│   └── CALIBRATION.md
│
└── README.md
```

## 🎯 사용 방법

### 1. 시스템 시작

1. **PC에서 MQTT 브로커 실행** (자동 실행되지 않는 경우)
2. **라즈베리 파이 전원 켜기** (배터리 연결)
3. **PC GUI 프로그램 실행**

### 2. 작업 흐름

1. 누룽지 생산 → 팬에 쌓기
2. **실시간으로 개수 표시** (GUI에서 확인)
3. 팬 가득 참 → **"팬 확정"** 버튼 클릭
4. 로그 기록 및 통계 업데이트
5. 다음 팬 시작

## 🔧 캘리브레이션

정확도를 90~95%로 최적화하기 위해 캘리브레이션 필요:

```bash
cd calibration
python calibration_tool.py
```

1. 테스트 이미지 로드
2. 파라미터 조정 (이진화 임계값, 최소/최대 면적 등)
3. 저장 후 `edge_device/config.py`에 적용

자세한 내용: [캘리브레이션 가이드](docs/CALIBRATION.md)

## 📊 예상 성능

- **정확도**: 90~95% (OpenCV 윤곽선 감지)
- **작동 시간**: 8시간 (20,000mAh 배터리)
- **처리 속도**: 1초당 1프레임
- **통신 지연**: < 100ms (로컬 WiFi)

## 🛡️ 문제 해결

### MQTT 연결 실패
- MQTT 브로커 실행 확인: `mosquitto -v`
- 방화벽 확인 (1883 포트)
- IP 주소 확인 및 설정 파일 수정

### 카메라 인식 안됨
- 리본 케이블 재연결
- 카메라 활성화: `sudo raspi-config` → Interface Options → Camera

### 감지 정확도 낮음
- 캘리브레이션 도구로 파라미터 재조정
- 조명 개선 (일정한 조명)
- 카메라 각도 조정

더 많은 문제 해결: [하드웨어 가이드](docs/HARDWARE_SETUP.md#문제-해결)

## 🗺️ 개발 로드맵

### Phase 1: MVP (완료) ✅
- 라즈베리 파이 감지 시스템
- PC GUI 프로그램
- MQTT 통신
- 캘리브레이션 도구

### Phase 2: 고도화 (선택)
- 자동 팬 확정 감지 (화면에서 사라짐 감지)
- 설정 UI 추가
- 통계 차트 시각화

### Phase 3: AI 고정확도 (선택)
- YOLOv8-Nano TFLite 모델
- 정확도 95~98%
- 겹친 누룽지 정확 분리

## 💰 총 비용 및 기간

- **하드웨어**: 약 15만원
- **개발 기간**: 10일
- **소프트웨어**: 무료 (오픈소스)

## 📄 라이선스

MIT License

## 📞 기술 지원

- **GitHub Issues**: 문제 보고 및 기능 요청
- **이메일**: [연락처]

---

**Version**: 1.0.0
**Last Updated**: 2025-02-23
**Status**: Phase 1 완성 (MVP)
