import os
import shutil

from config import Config

def log(msg: str) -> None:
    print(msg, flush=True)
    return

def get_user_info_from_text(user_info_file_path: str) -> tuple:
    if not os.path.exists(user_info_file_path):
        raise FileNotFoundError
    with open(user_info_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    if len(lines) < 1:
        raise Exception("User 정보가 존재하지 않습니다.")
    
    user_id = lines[0].strip()
    user_pw = lines[1].strip()
    
    return (user_id, user_pw)

def move_post_file(html_file_path: str) -> None:
    src_file_path = html_file_path
    dst_file_path = html_file_path.replace(Config.NEW_POST_DIR, Config.COMPLETE_POST_DIR)
    
    shutil.move(src_file_path, dst_file_path)