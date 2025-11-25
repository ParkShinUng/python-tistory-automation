import os
import asyncio

from pathlib import Path
from typing import List, Tuple
from config import Config
from workers import worker_job
from helper import log, get_user_info_from_text
from tistory_library import Tistory

from playwright.async_api import async_playwright, Page


async def main():
    cfg = Config()
    
    # 계정
    user_data_dir_list = os.listdir(cfg.USER_DATA_DIR_PATH)
    for user_data_dir_name in user_data_dir_list:
        user_info_dir_path = os.path.join(
            cfg.USER_DATA_DIR_PATH,
            user_data_dir_name
        )
        user_info_file_path = os.path.join(
            user_info_dir_path,
            cfg.USER_INFO_FILE_NAME
        )
        
        user_id, user_pw = get_user_info_from_text(user_info_file_path)
            
        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
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

            # 첫 페이지 준비
            page0 = browser.pages[0] if browser.pages else await browser.new_page()
            await page0.goto(cfg.TISTORY_LOGIN_URL, wait_until="load")
            
            # 로그인 처리(첫 1회만)
            await page0.wait_for_selector('a.btn_login', timeout=10000)
            login_btn = page0.locator('a.btn_login')
            if await login_btn.count() > 0:
                await login_btn.click()
                await page0.locator('input[name="loginId"]').fill(user_id)
                await page0.locator('input[name="password"]').fill(user_pw)
                await page0.locator('button[type="submit"]').click()
                await page0.wait_for_load_state("networkidle")
                await page0.goto(cfg.TISTORY_NEW_POST_URL, wait_until="load")

            # 나머지 탭 생성
            pages: List[Page] = [page0]
            for _ in range(cfg.num_tabs - 1):
                new_page = await browser.new_page()
                await new_page.goto(cfg.TISTORY_NEW_POST_URL, wait_until="commit")
                pages.append(new_page)
            
            new_post_dir_path = os.path.join(cfg.BASE_DIR, cfg.NEW_POST_DIR)
            file_list: list = os.listdir(new_post_dir_path)[:cfg.MAX_NEW_POST_PER_USER]
            if len(file_list) < 1:
                log(f"{new_post_dir_path} Directory 내부에 파일이 존재하지 않습니다.")
                await browser.close()
                return
            
            post_jobs = [(file, os.path.join(new_post_dir_path, file)) for file in file_list]
                
            # ----- 작업 분배 (라운드 로빈) -----
            # 5개 Tab에 작업 균등 분배 - 15 : [3, 3, 3, 3, 3]
            worker_jobs: List[List[Tuple[int, str]]] = [[] for _ in range(cfg.num_tabs)]
            for i, job in enumerate(post_jobs):
                worker_index = i % cfg.num_tabs
                worker_jobs[worker_index].append(job)
                    
            # ----- 워커 세션 생성 & 병렬 실행 -----
            tasks = []
            for idx, jobs in enumerate(worker_jobs):
                if not jobs:
                    continue
                tistory = Tistory(pages[idx], cfg)
                tasks.append(asyncio.create_task(worker_job(tistory, jobs)))

            all_results_nested: List[List[Tuple[int, str]]] = await asyncio.gather(*tasks)

            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
