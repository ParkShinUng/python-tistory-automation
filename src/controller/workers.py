from typing import List, Tuple, Any, Optional
from src.tistory.html_parser import get_all_html
from src.tistory import TistoryClient


async def worker_job(tistory_client: TistoryClient, jobs: List[Tuple[str, str]]) -> None:
    for file_path, tags in jobs:
        html = get_all_html(file_path)
        await tistory_client.asnyc_post(html, tags)
