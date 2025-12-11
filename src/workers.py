from typing import List, Tuple
from html_parser import get_all_html
from api import TistoryClient


async def worker_job(tistory_client: TistoryClient, jobs: List[Tuple[str, list]]) -> None:
    for file_path, tags in jobs:
        html = get_all_html(file_path)
        await tistory_client.asnyc_post(html, tags)
