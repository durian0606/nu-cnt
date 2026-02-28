"""
누룽지 생산량 카운팅 시스템 - 사용자 설정 관리
설정 저장/로드 기능
"""

import json
import os


class Settings:
    """
    사용자 설정 관리 클래스
    """

    def __init__(self, config_file="config.json"):
        """
        설정 초기화

        Args:
            config_file (str): 설정 파일 경로
        """
        self.config_file = config_file
        self.settings = self._load_default_settings()
        self.load()

    def _load_default_settings(self):
        """
        기본 설정 로드

        Returns:
            dict: 기본 설정
        """
        return {
            "mqtt": {
                "broker_address": "localhost",
                "broker_port": 1883
            },
            "raspberry_pi": {
                "ip": "",
                "mjpeg_port": 8080
            },
            "counter": {
                "auto_confirm": True,
                "stabilization_window": 5
            },
            "gui": {
                "theme": "light",
                "show_debug_info": False
            },
            "notification": {
                "sound_enabled": True,
                "popup_enabled": False
            }
        }

    def load(self):
        """
        설정 파일에서 로드
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
                print(f"[Settings] 설정 로드 완료: {self.config_file}")
            except Exception as e:
                print(f"[Settings] 설정 로드 실패: {e}")
        else:
            print(f"[Settings] 설정 파일 없음, 기본값 사용")

    def save(self):
        """
        설정 파일에 저장
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            print(f"[Settings] 설정 저장 완료: {self.config_file}")
        except Exception as e:
            print(f"[Settings] 설정 저장 실패: {e}")

    def get(self, key, default=None):
        """
        설정 값 가져오기

        Args:
            key (str): 설정 키 (점 표기법 지원, 예: "mqtt.broker_address")
            default: 기본값

        Returns:
            설정 값 또는 기본값
        """
        keys = key.split('.')
        value = self.settings

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key, value):
        """
        설정 값 설정

        Args:
            key (str): 설정 키 (점 표기법 지원)
            value: 설정 값
        """
        keys = key.split('.')
        target = self.settings

        # 중첩된 딕셔너리 탐색
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]

        # 마지막 키에 값 설정
        target[keys[-1]] = value
