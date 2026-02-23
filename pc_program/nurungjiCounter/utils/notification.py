"""
누룽지 생산량 카운팅 시스템 - 알림 모듈
소리 및 팝업 알림
"""

import sys
from ..config import ENABLE_SOUND, ENABLE_POPUP


class Notification:
    """
    알림 관리 클래스
    """

    @staticmethod
    def play_sound(sound_type="default"):
        """
        소리 재생

        Args:
            sound_type (str): 소리 유형 ("default", "success", "warning")
        """
        if not ENABLE_SOUND:
            return

        try:
            # 플랫폼별 소리 재생
            if sys.platform == "win32":
                import winsound
                if sound_type == "success":
                    winsound.MessageBeep(winsound.MB_OK)
                elif sound_type == "warning":
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                else:
                    winsound.MessageBeep()

            elif sys.platform == "darwin":  # macOS
                import os
                os.system("afplay /System/Library/Sounds/Glass.aiff &")

            else:  # Linux
                import os
                os.system("paplay /usr/share/sounds/freedesktop/stereo/complete.oga &")

        except Exception as e:
            print(f"[Notification] 소리 재생 실패: {e}")

    @staticmethod
    def show_popup(title, message, icon="info"):
        """
        팝업 알림

        Args:
            title (str): 제목
            message (str): 메시지
            icon (str): 아이콘 유형 ("info", "warning", "error")
        """
        if not ENABLE_POPUP:
            return

        try:
            from tkinter import messagebox

            if icon == "warning":
                messagebox.showwarning(title, message)
            elif icon == "error":
                messagebox.showerror(title, message)
            else:
                messagebox.showinfo(title, message)

        except Exception as e:
            print(f"[Notification] 팝업 표시 실패: {e}")

    @staticmethod
    def notify_batch_confirmed(count):
        """
        팬 확정 알림

        Args:
            count (int): 누룽지 개수
        """
        Notification.play_sound("success")

        if ENABLE_POPUP:
            Notification.show_popup(
                "팬 확정",
                f"{count}개 생산 완료!",
                "info"
            )
