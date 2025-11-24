import asyncio

from helper import log
from chatgpt_session import ChatGPTSession
from typing import List, Tuple, Optional
from html_parser import extract_title_and_body, get_all_html
from tistory_library import Tistory


async def worker_job(
    tistory: Tistory,
    jobs: List[Tuple[str, str]],
) -> None:
    """
    각 탭에서 자기에게 할당된 (file_name, file_path) 리스트를 순차 처리.
    결과로 () 리스트 반환.
    """
    for file, file_path in jobs:
        html = get_all_html(file_path)
        title, body_html = extract_title_and_body(html)
        
        await tistory.async_set_html(html)
        
        await tistory.async_set_title(title)
        await tistory.async_set_body(body_html)
        await tistory.async_publish()
        
