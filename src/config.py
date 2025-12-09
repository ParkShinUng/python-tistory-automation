import os
import platform

from dataclasses import dataclass

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
    num_tabs: int = 1
    MAX_FILES = 15
    MAX_TAGS = 10

    # TISTORY
    TISTORY_LOGIN_URL: str = "https://www.tistory.com/auth/login"
    
    # Playwright 브라우저 설정
    headless: bool = False
    
    # 타임아웃 및 딜레이
    queries_wait_timeout: float = 30.0
    