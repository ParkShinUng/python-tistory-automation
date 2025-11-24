import os
import asyncio

from pathlib import Path
from typing import List, Tuple
from config import Config
from workers import worker_job
from helper import log
from chatgpt_session import ChatGPTSession
from tistory_library import Tistory

from playwright.async_api import async_playwright, Page


async def main():
    cfg = Config()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            cfg.user_data_account_dir,
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
        await page0.goto(cfg.tistory_login_url, wait_until="load")
        
        # 로그인 처리(첫 1회만)
        await page0.wait_for_selector('a.btn_login', timeout=10000)
        login_btn = page0.locator('a.btn_login')
        if await login_btn.count() > 0:
            await login_btn.click()
            await page0.locator('input[name="loginId"]').fill(cfg.USER_ID)
            await page0.locator('input[name="password"]').fill(cfg.USER_PW)
            await page0.locator('button[type="submit"]').click()
            await page0.wait_for_load_state("networkidle")
            await page0.goto(cfg.tistory_upload_url, wait_until="load")

        # 나머지 탭 생성
        pages: List[Page] = [page0]
        for _ in range(cfg.num_tabs - 1):
            new_page = await browser.new_page()
            await new_page.goto(cfg.tistory_upload_url, wait_until="commit")
            pages.append(new_page)
        
        new_post_dir_path = os.path.join(os.getcwd(), cfg.POST_DIR)
        file_list: list = os.listdir(new_post_dir_path)
        if file_list < 1:
            log(f"{new_post_dir_path} Directory 내부에 파일이 존재하지 않습니다.")
            await browser.close()
            return
        
        post_jobs = [(file, os.path.join(new_post_dir_path, file)) for file in file_list]
            
        # ----- 작업 분배 (라운드 로빈) -----
        # 10개 Tab에 작업 균등 분배 - 48 : [5, 5, 5, 5, 5, 5, 5, 5, 4, 4]
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

        # 결과 flatten
        all_results: List[Tuple[int, str]] = [
            item for worker_res in all_results_nested for item in worker_res
        ]
            
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
