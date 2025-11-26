import os
import asyncio

from typing import List, Tuple
from workers import worker_job
from helper import log, EnvHelper
from tistory import TistoryClient
from config import Config
from playwright.async_api import async_playwright, Page
from chainshift_playwright_extension import get_async_browser

async def main():
    # 계정
    user_data_dir_list = os.listdir(Config.USER_DATA_DIR_PATH)
    for user_data_dir_name in user_data_dir_list:
        user_info_dir_path = os.path.join(
            Config.USER_DATA_DIR_PATH,
            user_data_dir_name
        )
        
        user_id, user_pw = EnvHelper().get_user_info(user_data_dir_name)
        new_post_url = EnvHelper().get_new_post_url(user_data_dir_name)
            
        async with async_playwright() as p:
            browser = await get_async_browser(p, user_info_dir_path, Config.headless)

            # 첫 페이지 준비
            page0 = browser.pages[0] if browser.pages else await browser.new_page()
            await page0.goto(Config.TISTORY_LOGIN_URL, wait_until="load")
            
            # 로그인 처리(첫 1회만)
            if await page0.locator('a.btn_login').is_visible():
                await page0.locator('a.btn_login').click()
                await page0.locator('input[name="loginId"]').fill(user_id)
                await page0.locator('input[name="password"]').fill(user_pw)
                await page0.locator('button[type="submit"]').click()
                await page0.wait_for_load_state("networkidle")
            
            await page0.goto(new_post_url, wait_until="load")

            # 나머지 탭 생성
            pages: List[Page] = [page0]
            for _ in range(Config.num_tabs - 1):
                new_page = await browser.new_page()
                await new_page.goto(new_post_url, wait_until="commit")
                pages.append(new_page)
            
            input_post_dir_path = os.path.join(Config.DATA_DIR_PATH, Config.INPUT_POST_DIR_NAME)
            file_list: list = os.listdir(input_post_dir_path)[:Config.MAX_NEW_POST_PER_USER]
            if len(file_list) < 1:
                log(f"{input_post_dir_path} Directory 내부에 파일이 존재하지 않습니다.")
                await browser.close()
                return
            
            post_jobs = [(file, os.path.join(input_post_dir_path, file)) for file in file_list]
                
            # ----- 작업 분배 (라운드 로빈) -----
            # 5개 Tab에 작업 균등 분배 - 15 : [3, 3, 3, 3, 3]
            worker_jobs: List[List[Tuple[str, str]]] = [[] for _ in range(Config.num_tabs)]
            for i, job in enumerate(post_jobs):
                worker_index = i % Config.num_tabs
                worker_jobs[worker_index].append(job)
                    
            # ----- 워커 세션 생성 & 병렬 실행 -----
            tasks = []
            for idx, jobs in enumerate(worker_jobs):
                if not jobs:
                    continue
                tistory_client = TistoryClient(pages[idx])
                tasks.append(asyncio.create_task(worker_job(tistory_client, jobs)))

            all_results_nested: List[List[Tuple[int, str]]] = await asyncio.gather(*tasks)

            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
