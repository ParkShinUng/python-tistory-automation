import shutil

from helper import log
from typing import List, Tuple
from tistory.html_parser import get_all_html
from tistory import TistoryClient
from config import Config


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
        
        src_file_path = file_path
        dst_file_path = file_path.replace(Config.INPUT_POST_DIR_NAME, Config.PUBLISHED_POST_DIR_NAME)
        shutil.move(src_file_path, dst_file_path)