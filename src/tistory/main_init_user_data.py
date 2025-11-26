import os

from src.config import Config
from src.helper import EnvHelper
from playwright.sync_api import sync_playwright
from chainshift_playwright_extension import get_sync_browser

account_initial_name = "psw"

user_id, user_pw = EnvHelper().get_user_info(account_initial_name)

user_data_dir_name = f"user_data_tistory_{account_initial_name}"
user_info_dir_path = os.path.join(
    Config.USER_DATA_DIR_PATH,
    user_data_dir_name
)

if not os.path.isdir(user_info_dir_path):
    os.mkdir(user_info_dir_path)

with sync_playwright() as p:
    browser = get_sync_browser(p, user_info_dir_path, Config.headless)

    page = browser.pages[0] if browser.pages else browser.new_page()
    page.goto(Config.TISTORY_LOGIN_URL, wait_until="load")
    
    page.wait_for_selector('a.btn_login', timeout=10000)
    login_btn = page.locator('a.btn_login')
    if login_btn.count() > 0:
        login_btn.click()
        page.locator('input[name="loginId"]').fill(user_id)
        page.locator('input[name="password"]').fill(user_pw)
        page.locator('button[type="submit"]').click()
        page.wait_for_load_state("networkidle")
        page.wait_for_url("https://www.tistory.com/", timeout=30000)
    