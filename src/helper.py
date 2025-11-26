import os
import shutil

from config import Config
from dotenv import load_dotenv, find_dotenv

class EnvHelper(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.env = self._set_env()
        self.id_key_str = "_user_id"
        self.pw_key_str = "_user_pw"
        self.new_post_key_str = "_new_post_url"
        self.user_data_tistory_str = "user_data_tistory_"
        
    def _set_env(self):
        dotenv_file = find_dotenv()
        load_dotenv(dotenv_file)
        self.env = os.environ
        
    def get_value_by_key(self, key: str) -> str:
        return self.env[key]
    
    def get_user_info(self, user_data_file_path: str) -> tuple:
        user_initial = self.get_user_initial_from_file(user_data_file_path)
        id_key = f"{user_initial}{self.id_key_str}"
        pw_key = f"{user_initial}{self.pw_key_str}"
        
        return self.env[id_key], self.env[pw_key]
    
    def get_new_post_url(self, user_data_file_path: str) -> str:
        user_initial = self.get_user_initial_from_file(user_data_file_path)
        url_key = f"{user_initial}{self.new_post_key_str}"
        return self.env[url_key]
    
    def get_user_initial_from_file(self, user_data_file_path: str) -> str:
        return os.path.basename(user_data_file_path).replace(self.user_data_tistory_str, "")


class FileHelper:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def move_post_file(self, html_file_path: str) -> None:
        src_file_path = html_file_path
        dst_file_path = html_file_path.replace(Config.INPUT_POST_DIR, Config.PUBLISHED_POST_DIR)
        shutil.move(src_file_path, dst_file_path)
        
    
def log(msg: str) -> None:
    print(msg, flush=True)
    return
