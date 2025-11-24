from pathlib import Path

def parse_html_file(file_path: str):
    """
    첫 번째 '내용 있는 줄'을 제목으로 사용하고,
    그 이후 전체를 HTML 본문으로 사용.
    """
    text = Path(file_path).read_text(encoding="utf-8")
    lines = text.splitlines()

    if not lines:
        raise ValueError("HTML 파일이 비어 있습니다.")

    title_idx = None
    for idx, line in enumerate(lines):
        if line.strip():
            title_idx = idx
            break

    if title_idx is None:
        raise ValueError("파일에 제목으로 사용할 줄(내용 있는 줄)이 없습니다.")

    title = lines[title_idx].strip()
    body_html = "\n".join(lines[title_idx + 1 :]).strip()

    if not body_html:
        raise ValueError("제목 이후에 본문(HTML)이 없습니다.")

    return title, body_html