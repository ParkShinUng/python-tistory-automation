import os
import time

from config import Config
from playwright.sync_api import sync_playwright

cfg = Config()

account_initial_name = "hyh"
user_data_dir_name = f"user_data_tistory_{account_initial_name}"

user_info_dir_path = os.path.join(
    cfg.USER_DATA_DIR_PATH,
    user_data_dir_name
)

if not os.path.isdir(user_info_dir_path):
    os.mkdir(user_info_dir_path)

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=user_info_dir_path,
        headless=cfg.headless,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars",
            "--disable-dev-shm-usage",
            "--start-maximized",
        ],
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        ),
        locale="ko-KR",
        timezone_id="Asia/Seoul",
    )

    page = browser.pages[0] if browser.pages else browser.new_page()
    page.goto(cfg.TISTORY_LOGIN_URL, wait_until="load")
    
    page.wait_for_selector('a.btn_login', timeout=10000)
    login_btn = page.locator('a.btn_login')
    if login_btn.count() > 0:
        login_btn.click()
        time.sleep(600)
    