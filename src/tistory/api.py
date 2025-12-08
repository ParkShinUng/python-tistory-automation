import asyncio

from playwright.async_api import Page
from .html_parser import extract_title_and_body


class TistoryClient:
    locator_textarea_title = "textarea#post-title-inp"
    locator_plugin_btn_open = "button#more-plugin-btn-open"
    locator_plugin_html_block = "div#plugin-html-block"
    locator_post_codeblock_content = "div.mce-codeblock-content"
    locator_post_codeblock_submit_btn = "div.mce-codeblock-btn-submit"
    locator_post_complete_btn = "button#publish-layer-btn"
    locator_post_public_input = "input#open20"
    locator_post_publish_btn = "button#publish-btn"
    locator_post_tag_input = "input#tagText"
    add_content_javascript = """
        (html) => {
            const editor = window.tinymce && window.tinymce.get('editor-tistory');
            if (!editor) {
                console.warn('TinyMCE editor not found');
                return;
            }
            const current = editor.getContent() || "";
            editor.setContent(current + html);
            editor.fire('change');
        }
    """

    def __init__(self, page: Page, new_post_url: str):
        self.page = page
        self.new_post_url = new_post_url
        
    async def async_set_title(self, title: str) -> None:
        await self.page.wait_for_selector(self.locator_textarea_title)
        title_locator = self.page.locator(self.locator_textarea_title)
        await title_locator.fill(title)
        
    async def async_set_body(self, body_html: str) -> None:
        await self.append_html_with_tinymce(body_html)
    
    async def async_set_html(self, html: str) -> None:
        await self.page.wait_for_load_state('networkidle', timeout=10000)
        await self.page.locator(self.locator_plugin_btn_open).click()
        await self.page.locator(self.locator_plugin_html_block).click()
        
        await self.page.wait_for_load_state('networkidle', timeout=10000)
        html_locator = self.page.locator(self.locator_post_codeblock_content).locator("textarea").last
        await html_locator.fill(html)
        await self.page.locator(self.locator_post_codeblock_submit_btn).click()
        await self.page.wait_for_load_state('networkidle', timeout=10000)
    
    async def async_publish(self):
        # 완료버튼 클릭 -> 공개 클릭 -> 발행버튼 클릭
        await self.page.locator(self.locator_post_complete_btn).click()
        await self.page.wait_for_load_state('networkidle', timeout=10000)
        await self.page.locator(self.locator_post_public_input).click()
        await self.page.wait_for_load_state('networkidle', timeout=10000)
        await self.page.locator(self.locator_post_publish_btn).click()
        await asyncio.sleep(3)

    async def async_set_tag(self, tags: str):
        # 태그 입력은 최대 10개까지만 가능
        # await self.page.locator(self.locator_post_tag_input)
        return
        
    async def append_html_with_tinymce(self, html: str):
        await self.page.evaluate(self.add_content_javascript, html)

    async def async_move_new_post_url(self):
        await self.page.goto(self.new_post_url, wait_until="commit")

    async def asnyc_post(self, html: str, tags: str):
        await self.async_move_new_post_url()

        title, body_html = extract_title_and_body(html)

        await self.async_set_html(html)
        await self.async_set_title(title)
        await self.async_set_body(body_html)
        await self.async_set_tag(tags)
        await self.async_publish()