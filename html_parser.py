from pathlib import Path
from bs4 import BeautifulSoup

def get_all_html(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8")

def extract_title_and_body(html_text: str):
    soup = BeautifulSoup(html_text, "html.parser")

    # 1) 첫 번째 h1 태그 찾기
    first_h1 = soup.find("h1")
    if first_h1 is None:
        raise ValueError("HTML 안에 <h1> 태그가 없습니다.")

    # 제목 텍스트
    title = first_h1.get_text(strip=True)

    # 2) 첫 번째 h1 태그 제거
    first_h1.extract()

    # 3) 나머지 HTML 전체 (문자열)
    body_html = str(soup).strip()

    return title, body_html
