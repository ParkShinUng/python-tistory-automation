import os
import platform
from secret import user_id, user_pw

from dataclasses import dataclass


@dataclass
class Config:
    # System
    platform_info: str = platform.system()
    
    # 병렬 처리
    num_tabs: int = 1
    
    # Excel
    POST_DIR = "new_post"

    # ChatGPT
    __user_id = user_id
    __user_pw = user_pw
    tistory_login_url: str = "https://www.tistory.com/auth/login"
    tistory_upload_url: str = "https://korea-beauty-editor-best.tistory.com/manage/newpost"
    user_data_dir: str = "user_data"
    user_data_account_dir: str = os.path.join(user_data_dir, "user_data_tistory_psw")
    
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
    