import os
import sys

from dataclasses import dataclass

def resource_path(relative_path):
    """PyInstaller 실행 환경에서 리소스로 접근할 수 있는 경로를 반환합니다."""
    # PyInstaller가 생성한 임시 디렉터리(_MEIPASS)를 확인합니다.
    try:
        base_path = sys._MEIPASS
    except Exception:
        # 개발 환경에서는 스크립트의 현재 경로를 사용합니다.
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

@dataclass
class Config():
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    # Directory Path, Name
    CONFIG_EXECUTE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT_DIR = os.path.abspath(os.path.join(CONFIG_EXECUTE_DIR, '..'))
    USER_DATA_DIR_PATH: str = os.path.join(PROJECT_ROOT_DIR, "user_data")
    AUTH_FILE_PATH: str = os.path.join(PROJECT_ROOT_DIR, 'auth/tistory_auth.json')

    # 병렬 처리
    num_tabs: int = 5
    MAX_FILES = 15
    MAX_TAGS = 10

    # TISTORY
    TISTORY_LOGIN_URL: str = "https://www.tistory.com/auth/login"
    TISTORY_MAIN_URL: str = "https://www.tistory.com/"
    
    # Playwright 브라우저 설정
    headless: bool = False
    
    # 타임아웃 및 딜레이
    queries_wait_timeout: float = 30.0
    