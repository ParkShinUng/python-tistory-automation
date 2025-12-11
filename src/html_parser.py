from pathlib import Path
from bs4 import BeautifulSoup

def get_all_html(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8")

def get_title(first_h1) -> str:
    return first_h1.get_text(strip=True)

def get_body_html(soup: BeautifulSoup) -> str:
    return str(soup).strip()

def extract_title_and_body(html_text: str):
    soup = BeautifulSoup(html_text, "html.parser")

    first_h1 = soup.find("h1")
    if first_h1 is None:
        raise ValueError("HTML 안에 <h1> 태그가 없습니다.")
    
    title = get_title(first_h1)

    first_h1.extract()
    body_html = get_body_html(soup)

    return title, body_html
