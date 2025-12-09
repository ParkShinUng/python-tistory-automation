import json

from src.config import Config


def load_login_data_from_json(LOGIN_DATA_FILE_PATH):
    with open(LOGIN_DATA_FILE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data

def find_user_data_by_id(user_id: str):
    login_data = load_login_data_from_json(Config.AUTH_FILE_PATH)
    data_list = [data for data in login_data if data['ID'] == user_id]
    if data_list:
        return data_list[0]

def log(msg: str) -> None:
    print(msg, flush=True)
    return
