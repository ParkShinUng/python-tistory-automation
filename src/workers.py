from helper import log, move_post_file
from typing import List, Tuple
from tistory.html_parser import get_all_html
from tistory import TistoryClient


async def worker_job(
    tistory_client: TistoryClient,
    jobs: List[Tuple[str, str]],
) -> None:
    """
    각 탭에서 자기에게 할당된 (file_name, file_path) 리스트를 순차 처리.
    """
    for _, file_path in jobs:
        html = get_all_html(file_path)
        
        await tistory_client.post(html)
        move_post_file(file_path)