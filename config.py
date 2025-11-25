import os
import platform

from dataclasses import dataclass


@dataclass
class Config:
    # System
    platform_info: str = platform.system()
    
    # 병렬 처리
    num_tabs: int = 1
    MAX_NEW_POST_PER_USER = 15

    # TISTORY
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    NEW_POST_DIR = "new_post"
    COMPLETE_POST_DIR = "complete_post"
    TISTORY_LOGIN_URL: str = "https://www.tistory.com/auth/login"
    TISTORY_NEW_POST_URL: str = "https://korea-beauty-editor-best.tistory.com/manage/newpost"
    USER_DATA_DIR_PATH: str = os.path.join(BASE_DIR, "user_data")
    USER_INFO_FILE_NAME = "user_info.txt"
    
    # Playwright 브라우저 설정
    headless: bool = False
    
    # 타임아웃 및 딜레이
    queries_wait_timeout: float = 30.0
    
    @property
    def USER_ID(self):
        return self.__user_id
    
    @property
    def USER_PW(self):
        return self.__user_pw
    