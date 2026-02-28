"""
누룽지 생산량 카운팅 시스템 - PC GUI 프로그램
Tkinter 기반 사용자 인터페이스
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import threading
import sys
import os
import base64
import io
import urllib.request

# 모듈 경로 추가
sys.path.insert(0, os.path.dirname(__file__))

from nurungjiCounter.config import (
    WINDOW_TITLE, WINDOW_SIZE, GUI_UPDATE_INTERVAL, COLORS
)
from nurungjiCounter.receiver.mqtt_receiver import MQTTReceiver
from nurungjiCounter.counter.production_counter import ProductionCounter
from nurungjiCounter.logger.production_logger import ProductionLogger
from nurungjiCounter.logger.statistics import Statistics
from nurungjiCounter.utils.notification import Notification
from nurungjiCounter.settings import Settings


class NurungjiCounterGUI:
    """
    누룽지 카운팅 시스템 GUI 메인 클래스
    """

    def __init__(self, root):
        """
        GUI 초기화

        Args:
            root (tk.Tk): Tkinter 루트 윈도우
        """
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)

        # 설정
        self.settings = Settings()

        # 컴포넌트 초기화
        self.counter = ProductionCounter()
        self.logger = ProductionLogger()
        self.statistics = Statistics()

        # MQTT 수신기 (나중에 연결)
        self.mqtt_receiver = None

        # UI 변수
        self.current_count_var = tk.StringVar(value="0")
        self.stable_count_var = tk.StringVar(value="0")
        self.today_production_var = tk.StringVar(value="0")
        self.today_batches_var = tk.StringVar(value="0")
        self.connection_status_var = tk.StringVar(value="🔴 연결 안됨")

        # 캘리브레이션 상태
        self._calibration_window = None
        self._calibration_image_label = None
        self._calib_photo = None  # PhotoImage 참조 유지 (GC 방지)

        # 카메라 뷰어 상태
        self._camera_window = None
        self._camera_image_label = None
        self._camera_photo = None
        self._camera_streaming = False
        self._camera_status_var = None

        # UI 구성
        self._create_widgets()

        # MQTT 연결 시도
        self._connect_mqtt()

        # GUI 업데이트 루프
        self._update_gui()

    def _create_widgets(self):
        """
        UI 위젯 생성
        """
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # 1. 헤더
        self._create_header(main_frame)

        # 2. 현재 상태
        self._create_status_section(main_frame)

        # 3. 버튼들
        self._create_button_section(main_frame)

        # 4. 로그 영역
        self._create_log_section(main_frame)

        # 5. 하단 상태바
        self._create_statusbar(main_frame)

    def _create_header(self, parent):
        """
        헤더 생성
        """
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        title_label = ttk.Label(
            header_frame,
            text="🍚 누룽지 생산량 자동 카운팅 시스템",
            font=("맑은 고딕", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)

        settings_btn = ttk.Button(
            header_frame,
            text="⚙️ 설정",
            command=self._show_settings
        )
        settings_btn.pack(side=tk.RIGHT)

    def _create_status_section(self, parent):
        """
        현재 상태 섹션 생성
        """
        status_frame = ttk.LabelFrame(parent, text="📊 현재 상태", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # 좌측: 팬 위 개수
        left_frame = ttk.Frame(status_frame)
        left_frame.grid(row=0, column=0, padx=10)

        ttk.Label(left_frame, text="팬 위 개수", font=("맑은 고딕", 10)).pack()
        count_label = ttk.Label(
            left_frame,
            textvariable=self.current_count_var,
            font=("맑은 고딕", 36, "bold"),
            foreground=COLORS["primary"]
        )
        count_label.pack()

        stable_label = ttk.Label(
            left_frame,
            textvariable=self.stable_count_var,
            font=("맑은 고딕", 10)
        )
        stable_label.pack()

        # 우측: 오늘 생산량
        right_frame = ttk.Frame(status_frame)
        right_frame.grid(row=0, column=1, padx=10)

        ttk.Label(right_frame, text="오늘 생산량", font=("맑은 고딕", 10)).pack()
        production_label = ttk.Label(
            right_frame,
            textvariable=self.today_production_var,
            font=("맑은 고딕", 36, "bold"),
            foreground=COLORS["success"]
        )
        production_label.pack()

        batches_label = ttk.Label(
            right_frame,
            textvariable=self.today_batches_var,
            font=("맑은 고딕", 10)
        )
        batches_label.pack()

    def _create_button_section(self, parent):
        """
        버튼 섹션 생성
        """
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        # 팬 확정 버튼
        confirm_btn = ttk.Button(
            button_frame,
            text="🔄 팬 확정",
            command=self._confirm_batch,
            width=15
        )
        confirm_btn.grid(row=0, column=0, padx=5)

        # 초기화 버튼
        reset_btn = ttk.Button(
            button_frame,
            text="🗑️ 초기화",
            command=self._reset_current,
            width=15
        )
        reset_btn.grid(row=0, column=1, padx=5)

        # 통계 버튼
        stats_btn = ttk.Button(
            button_frame,
            text="📊 통계",
            command=self._show_statistics,
            width=15
        )
        stats_btn.grid(row=0, column=2, padx=5)

        # 로그 버튼
        log_btn = ttk.Button(
            button_frame,
            text="📋 로그",
            command=self._show_log_file,
            width=15
        )
        log_btn.grid(row=0, column=3, padx=5)

        # 두 번째 행: 캘리브레이션 버튼
        self._calib_start_btn = ttk.Button(
            button_frame,
            text="🎯 캘리브레이션 시작",
            command=self._start_calibration,
            width=20
        )
        self._calib_start_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=(8, 0))

        self._calib_stop_btn = ttk.Button(
            button_frame,
            text="⏹ 중지",
            command=self._stop_calibration,
            width=20,
            state=tk.DISABLED
        )
        self._calib_stop_btn.grid(row=1, column=2, columnspan=2, padx=5, pady=(8, 0))

        # 세 번째 행: 카메라 뷰어 버튼
        camera_btn = ttk.Button(
            button_frame,
            text="📷 카메라 보기",
            command=self._open_camera_viewer,
            width=20
        )
        camera_btn.grid(row=2, column=0, columnspan=4, padx=5, pady=(8, 0))

    def _create_log_section(self, parent):
        """
        로그 영역 생성
        """
        log_frame = ttk.LabelFrame(parent, text="📝 최근 로그", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        parent.rowconfigure(3, weight=1)

        # 로그 텍스트 영역
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            width=80,
            font=("Consolas", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 초기 메시지
        self._add_log("시스템 시작")

    def _create_statusbar(self, parent):
        """
        하단 상태바 생성
        """
        statusbar = ttk.Frame(parent)
        statusbar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))

        ttk.Label(statusbar, text="연결 상태:").pack(side=tk.LEFT)

        status_label = ttk.Label(
            statusbar,
            textvariable=self.connection_status_var,
            font=("맑은 고딕", 9)
        )
        status_label.pack(side=tk.LEFT, padx=5)

    def _connect_mqtt(self):
        """
        MQTT 브로커 연결
        """
        def connect_thread():
            try:
                self._add_log("MQTT 브로커 연결 시도 중...")

                self.mqtt_receiver = MQTTReceiver(
                    on_count_update=self._on_count_update,
                    on_batch_complete=self._on_batch_complete,
                    on_status_update=self._on_status_update,
                    on_calibration_image=self._on_calibration_image
                )

                broker = self.settings.get("mqtt.broker_address", "localhost")
                port = self.settings.get("mqtt.broker_port", 1883)

                self.mqtt_receiver.connect(broker, port)

                # 연결 확인 대기
                import time
                time.sleep(2)

                if self.mqtt_receiver.is_connected():
                    self._add_log("✓ MQTT 브로커 연결 성공")
                    self.connection_status_var.set("🟢 라즈베리 파이 연결됨")
                else:
                    self._add_log("✗ MQTT 브로커 연결 실패")
                    self.connection_status_var.set("🔴 연결 실패")

            except Exception as e:
                self._add_log(f"✗ 연결 오류: {e}")
                self.connection_status_var.set("🔴 연결 오류")

        thread = threading.Thread(target=connect_thread, daemon=True)
        thread.start()

    def _on_count_update(self, count, boxes):
        """
        카운트 업데이트 콜백

        Args:
            count (int): 현재 카운트
            boxes (list): 바운딩 박스 리스트
        """
        # 카운터 업데이트
        result = self.counter.update_count(count)

        # UI 업데이트 (메인 스레드에서)
        self.root.after(0, self._update_count_display, result)

    def _on_batch_complete(self, final_count):
        """
        팬 확정 콜백

        Args:
            final_count (int): 확정 개수
        """
        self.root.after(0, self._confirm_batch, final_count)

    def _on_status_update(self, status_data):
        """
        상태 업데이트 콜백

        Args:
            status_data (dict): 상태 정보
        """
        # 배터리 경고
        battery = status_data.get("battery_level")
        if battery is not None and battery < 20:
            self._add_log(f"⚠️ 배터리 낮음: {battery}%")

    def _update_count_display(self, result):
        """
        카운트 표시 업데이트

        Args:
            result (dict): 카운터 업데이트 결과
        """
        self.current_count_var.set(f"{result['current_count']}개")
        self.stable_count_var.set(f"(안정화: {result['stable_count']}개)")

        # 자동 확정 메시지
        if result.get('auto_confirmed'):
            self._add_log("🔄 자동 팬 확정")

    def _confirm_batch(self, manual_count=None):
        """
        팬 확정

        Args:
            manual_count (int): 수동 입력 개수 (None이면 stable_count 사용)
        """
        batch = self.counter.confirm_batch(manual_count)

        if batch is None:
            messagebox.showwarning("경고", "확정할 개수가 없습니다.")
            return

        # 로그 기록
        batch_id = self.statistics.get_total_stats()["batches"] + 1
        self.logger.log_batch(batch_id, batch["count"])

        # 통계 업데이트
        self.statistics.add_batch(batch["count"])

        # UI 업데이트
        self._update_today_stats()

        # 로그 추가
        time_str = batch["timestamp"].strftime("%H:%M:%S")
        self._add_log(f"[{time_str}] 팬 확정 - {batch['count']}개 생산 완료")

        # 알림
        Notification.notify_batch_confirmed(batch["count"])

        # 카운트 표시 초기화
        self.current_count_var.set("0개")
        self.stable_count_var.set("(안정화: 0개)")

    def _reset_current(self):
        """
        현재 카운트 초기화
        """
        if messagebox.askyesno("확인", "현재 카운트를 초기화하시겠습니까?"):
            self.counter.reset_current()
            self.current_count_var.set("0개")
            self.stable_count_var.set("(안정화: 0개)")
            self._add_log("현재 카운트 초기화")

    def _update_today_stats(self):
        """
        오늘 생산량 통계 업데이트
        """
        stats = self.counter.get_today_statistics()
        self.today_production_var.set(f"{stats['total_production']}개")
        self.today_batches_var.set(f"({stats['total_batches']}팬)")

    def _add_log(self, message):
        """
        로그 추가

        Args:
            message (str): 로그 메시지
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)  # 스크롤을 맨 아래로

        # 로그가 너무 많으면 위에서부터 삭제
        lines = int(self.log_text.index('end-1c').split('.')[0])
        if lines > 100:
            self.log_text.delete('1.0', '2.0')

    def _show_statistics(self):
        """
        통계 창 표시
        """
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 생산량 통계")
        stats_window.geometry("500x400")

        # 통계 조회
        today_stats = self.statistics.get_daily_stats()
        weekly_stats = self.statistics.get_weekly_stats()
        monthly_stats = self.statistics.get_monthly_stats()
        total_stats = self.statistics.get_total_stats()

        # 표시
        stats_text = scrolledtext.ScrolledText(stats_window, font=("맑은 고딕", 10))
        stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        content = f"""
📅 오늘 ({datetime.now().strftime("%Y-%m-%d")})
  - 총 생산량: {today_stats.get('production', 0)}개
  - 팬 개수: {today_stats.get('batches', 0)}개

📆 최근 7일
  - 총 생산량: {weekly_stats.get('production', 0)}개
  - 팬 개수: {weekly_stats.get('batches', 0)}개
  - 일평균: {weekly_stats.get('avg_per_day', 0)}개

📅 이번 달 ({datetime.now().strftime("%Y-%m")})
  - 총 생산량: {monthly_stats.get('production', 0)}개
  - 팬 개수: {monthly_stats.get('batches', 0)}개

📊 전체
  - 총 생산량: {total_stats.get('production', 0)}개
  - 팬 개수: {total_stats.get('batches', 0)}개
        """

        stats_text.insert(tk.END, content)
        stats_text.config(state=tk.DISABLED)

    def _show_log_file(self):
        """
        로그 파일 열기
        """
        import subprocess

        log_path = self.logger.log_path

        if not os.path.exists(log_path):
            messagebox.showinfo("정보", "로그 파일이 없습니다.")
            return

        try:
            if sys.platform == "win32":
                os.startfile(log_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", log_path])
            else:
                subprocess.run(["xdg-open", log_path])
        except Exception as e:
            messagebox.showerror("오류", f"로그 파일 열기 실패:\n{e}")

    def _start_calibration(self):
        """
        캘리브레이션 시작: 이미지 창 열고 라즈베리파이에 명령 전송
        """
        if not self.mqtt_receiver or not self.mqtt_receiver.is_connected():
            messagebox.showwarning("경고", "라즈베리파이가 연결되어 있지 않습니다.")
            return

        # 이미지 창 열기
        self._open_calibration_window()

        # 라즈베리파이에 캘리브레이션 시작 명령 전송
        self.mqtt_receiver.publish_command("calibration_start")

        # 버튼 상태 전환
        self._calib_start_btn.config(state=tk.DISABLED)
        self._calib_stop_btn.config(state=tk.NORMAL)
        self._add_log("🎯 캘리브레이션 시작 - 라즈베리파이 영상 수신 대기 중...")

    def _stop_calibration(self):
        """
        캘리브레이션 중지: 이미지 창 닫고 라즈베리파이에 명령 전송
        """
        if self.mqtt_receiver and self.mqtt_receiver.is_connected():
            self.mqtt_receiver.publish_command("calibration_stop")

        if self._calibration_window and self._calibration_window.winfo_exists():
            self._calibration_window.destroy()
        self._calibration_window = None

        # 버튼 상태 복원
        self._calib_start_btn.config(state=tk.NORMAL)
        self._calib_stop_btn.config(state=tk.DISABLED)
        self._add_log("⏹ 캘리브레이션 중지")

    def _open_calibration_window(self):
        """
        캘리브레이션 이미지 표시 창 생성
        """
        if self._calibration_window and self._calibration_window.winfo_exists():
            self._calibration_window.lift()
            return

        win = tk.Toplevel(self.root)
        win.title("🎯 캘리브레이션 - 실시간 감지 영상")
        win.geometry("660x400")

        # 창 닫기 시 캘리브레이션 중지
        win.protocol("WM_DELETE_WINDOW", self._stop_calibration)

        # 이미지 표시 레이블
        placeholder = ttk.Label(win, text="라즈베리파이 영상을 수신 중...\n(최대 3초 소요)", font=("맑은 고딕", 12))
        placeholder.pack(expand=True)

        self._calibration_image_label = placeholder
        self._calibration_window = win

    def _on_calibration_image(self, payload):
        """
        캘리브레이션 이미지 수신 콜백 (MQTT 스레드에서 호출)
        """
        self.root.after(0, self._update_calibration_image, payload)

    def _update_calibration_image(self, payload):
        """
        캘리브레이션 창의 이미지 업데이트 (메인 스레드)
        """
        if not self._calibration_window or not self._calibration_window.winfo_exists():
            return

        try:
            from PIL import Image, ImageTk

            # base64 디코딩 → PIL Image
            image_b64 = payload.get("image", "")
            image_bytes = base64.b64decode(image_b64)
            pil_image = Image.open(io.BytesIO(image_bytes))

            # Tkinter PhotoImage 변환
            photo = ImageTk.PhotoImage(pil_image)

            # 레이블 갱신
            self._calibration_image_label.config(image=photo, text="")
            self._calib_photo = photo  # 참조 유지 (GC 방지)

            # 창 제목에 카운트 표시
            count = payload.get("count", 0)
            self._calibration_window.title(f"🎯 캘리브레이션 - 감지: {count}개")

        except ImportError:
            self._calibration_image_label.config(
                text="이미지 표시를 위해 Pillow 설치 필요\npip install pillow"
            )
        except Exception as e:
            self._add_log(f"캘리브레이션 이미지 오류: {e}")

    def _show_settings(self):
        """
        설정 창 표시
        """
        win = tk.Toplevel(self.root)
        win.title("⚙️ 설정")
        win.geometry("420x280")
        win.resizable(False, False)

        frame = ttk.Frame(win, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # --- 라즈베리 파이 ---
        ttk.Label(frame, text="라즈베리 파이", font=("맑은 고딕", 10, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        ttk.Label(frame, text="IP 주소:").grid(row=1, column=0, sticky=tk.W, pady=2)
        pi_ip_var = tk.StringVar(value=self.settings.get("raspberry_pi.ip", ""))
        ttk.Entry(frame, textvariable=pi_ip_var, width=28).grid(row=1, column=1, sticky=tk.W, padx=(8, 0))

        ttk.Label(frame, text="MJPEG 포트:").grid(row=2, column=0, sticky=tk.W, pady=2)
        pi_port_var = tk.StringVar(value=str(self.settings.get("raspberry_pi.mjpeg_port", 8080)))
        ttk.Entry(frame, textvariable=pi_port_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=(8, 0))

        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(
            row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=12)

        # --- MQTT ---
        ttk.Label(frame, text="MQTT 브로커", font=("맑은 고딕", 10, "bold")).grid(
            row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        ttk.Label(frame, text="브로커 주소:").grid(row=5, column=0, sticky=tk.W, pady=2)
        mqtt_addr_var = tk.StringVar(value=self.settings.get("mqtt.broker_address", "localhost"))
        ttk.Entry(frame, textvariable=mqtt_addr_var, width=28).grid(row=5, column=1, sticky=tk.W, padx=(8, 0))

        ttk.Label(frame, text="브로커 포트:").grid(row=6, column=0, sticky=tk.W, pady=2)
        mqtt_port_var = tk.StringVar(value=str(self.settings.get("mqtt.broker_port", 1883)))
        ttk.Entry(frame, textvariable=mqtt_port_var, width=10).grid(row=6, column=1, sticky=tk.W, padx=(8, 0))

        # --- 저장 버튼 ---
        def _save():
            self.settings.set("raspberry_pi.ip", pi_ip_var.get().strip())
            try:
                self.settings.set("raspberry_pi.mjpeg_port", int(pi_port_var.get().strip()))
            except ValueError:
                pass
            self.settings.set("mqtt.broker_address", mqtt_addr_var.get().strip())
            try:
                self.settings.set("mqtt.broker_port", int(mqtt_port_var.get().strip()))
            except ValueError:
                pass
            self.settings.save()
            self._add_log("설정 저장 완료")
            win.destroy()

        ttk.Button(frame, text="저장", command=_save, width=12).grid(
            row=7, column=0, columnspan=2, pady=(16, 0))

    def _open_camera_viewer(self):
        """
        카메라 뷰어 창 열기: 라즈베리 파이 MJPEG 스트림 실시간 표시
        """
        # 이미 창이 열려있으면 앞으로
        if self._camera_window and self._camera_window.winfo_exists():
            self._camera_window.lift()
            return

        ip = self.settings.get("raspberry_pi.ip", "").strip()
        if not ip:
            messagebox.showwarning(
                "설정 필요",
                "라즈베리 파이 IP 주소가 설정되지 않았습니다.\n⚙️ 설정 버튼에서 IP를 입력하고 저장하세요."
            )
            return

        port = self.settings.get("raspberry_pi.mjpeg_port", 8080)

        win = tk.Toplevel(self.root)
        win.title(f"📷 카메라 뷰어 - {ip}:{port}")
        win.geometry("680x530")
        win.protocol("WM_DELETE_WINDOW", self._stop_camera_stream)

        self._camera_status_var = tk.StringVar(value="연결 중...")

        # 상태 레이블
        status_lbl = ttk.Label(win, textvariable=self._camera_status_var, font=("맑은 고딕", 9))
        status_lbl.pack(pady=(6, 0))

        # 이미지 레이블
        img_lbl = ttk.Label(win, text="연결 대기 중...", font=("맑은 고딕", 11))
        img_lbl.pack(expand=True)

        self._camera_image_label = img_lbl
        self._camera_window = win

        # 스트리밍 스레드 시작
        self._camera_streaming = True
        t = threading.Thread(
            target=self._start_camera_stream,
            args=(ip, port),
            daemon=True
        )
        t.start()

        self._add_log(f"📷 카메라 뷰어 시작 - {ip}:{port}")

    def _start_camera_stream(self, ip, port):
        """
        MJPEG HTTP 스트림을 읽어 프레임별로 UI 업데이트 (백그라운드 스레드)
        """
        url = f"http://{ip}:{port}/stream"
        try:
            self.root.after(0, lambda: self._camera_status_var.set(f"연결 중... {url}"))
            req = urllib.request.Request(url, headers={"User-Agent": "NurungjiViewer/1.0"})
            response = urllib.request.urlopen(req, timeout=10)
            self.root.after(0, lambda: self._camera_status_var.set(f"연결됨 - {url}"))

            buffer = b""
            while self._camera_streaming:
                chunk = response.read(8192)
                if not chunk:
                    break
                buffer += chunk

                # JPEG 프레임 추출
                start = buffer.find(b'\xff\xd8')
                end = buffer.find(b'\xff\xd9')
                if start != -1 and end != -1 and end > start:
                    jpeg = buffer[start:end + 2]
                    buffer = buffer[end + 2:]
                    self.root.after(0, self._update_camera_frame, jpeg)

                # 버퍼 과다 방지
                if len(buffer) > 500_000:
                    buffer = buffer[-100_000:]

        except urllib.error.URLError as e:
            msg = f"연결 실패: {e.reason}"
            self.root.after(0, lambda: self._camera_status_var.set(msg))
            self.root.after(0, lambda: self._add_log(f"📷 카메라 연결 실패: {e.reason}"))
        except OSError as e:
            if self._camera_streaming:
                msg = f"스트림 오류: {e}"
                self.root.after(0, lambda: self._camera_status_var.set(msg))
                self.root.after(0, lambda: self._add_log(f"📷 스트림 오류: {e}"))
        finally:
            if self._camera_streaming:
                self.root.after(0, lambda: self._camera_status_var.set("연결 끊김"))

    def _update_camera_frame(self, jpeg_bytes):
        """
        카메라 뷰어 창의 이미지 업데이트 (메인 스레드)
        """
        if not self._camera_window or not self._camera_window.winfo_exists():
            return
        try:
            from PIL import Image, ImageTk
            pil_img = Image.open(io.BytesIO(jpeg_bytes))
            # 창 크기에 맞게 축소 (최대 640×480)
            pil_img.thumbnail((640, 480), Image.LANCZOS)
            photo = ImageTk.PhotoImage(pil_img)
            self._camera_image_label.config(image=photo, text="")
            self._camera_photo = photo  # GC 방지
        except ImportError:
            self._camera_image_label.config(text="이미지 표시를 위해 Pillow 설치 필요\npip install pillow")
        except Exception:
            pass

    def _stop_camera_stream(self):
        """
        카메라 스트림 중지 및 창 닫기
        """
        self._camera_streaming = False
        if self._camera_window and self._camera_window.winfo_exists():
            self._camera_window.destroy()
        self._camera_window = None
        self._camera_image_label = None
        self._camera_photo = None
        self._add_log("📷 카메라 뷰어 종료")

    def _update_gui(self):
        """
        GUI 주기적 업데이트
        """
        # 오늘 통계 업데이트
        self._update_today_stats()

        # 다음 업데이트 예약
        self.root.after(GUI_UPDATE_INTERVAL, self._update_gui)

    def on_closing(self):
        """
        창 닫기 이벤트
        """
        if messagebox.askokcancel("종료", "프로그램을 종료하시겠습니까?"):
            # MQTT 연결 종료
            if self.mqtt_receiver:
                self.mqtt_receiver.disconnect()

            # 설정 저장
            self.settings.save()

            # 종료
            self.root.destroy()


def main():
    """
    메인 함수
    """
    # Tkinter 루트 생성
    root = tk.Tk()

    # GUI 생성
    app = NurungjiCounterGUI(root)

    # 창 닫기 이벤트
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # 메인 루프
    root.mainloop()


if __name__ == "__main__":
    main()
