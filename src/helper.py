import os
import shutil

from config import Config
from dotenv import load_dotenv, find_dotenv

def log(msg: str) -> None:
    print(msg, flush=True)
    return

def get_user_info_from_env(user_data_file_path: str):
    user_initial = os.path.basename(user_data_file_path).replace("user_data_tistory_", "")
    id_key = f"{user_initial}_user_id"
    pw_key = f"{user_initial}_user_pw"
    
    dotenv_file = find_dotenv()
    load_dotenv(dotenv_file)
    
    user_id = os.environ[id_key]
    user_pw = os.environ[pw_key]
    
    return user_id, user_pw

def move_post_file(html_file_path: str) -> None:
    src_file_path = html_file_path
    dst_file_path = html_file_path.replace(Config.INPUT_POST_DIR, Config.PUBLISHED_POST_DIR)
    
    shutil.move(src_file_path, dst_file_path)