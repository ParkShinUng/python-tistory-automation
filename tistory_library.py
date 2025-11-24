from config import Config
from playwright.async_api import Page

locator_textarea_title = "textarea#post-title-inp"
locator_plugin_btn_open = "button#more-plugin-btn-open"
locator_plugin_html_block = "div#plugin-html-block"

class Tistory:
    def __init__(self, page: Page, cfg: Config):
        self.page = page
        self.cfg = cfg
        
    async def async_set_title(self, title: str) -> None:
        await self.page.wait_for_selector(locator_textarea_title)
        title_locator = self.page.locator(locator_textarea_title)
        await title_locator.fill(title)
        
    async def async_set_body(self, body_html: str) -> None:
        await self.append_html_with_tinymce(body_html)
    
    async def async_set_html(self, html: str) -> None:
        await self.page.wait_for_load_state('networkidle', timeout=10000)
        await self.page.locator(locator_plugin_btn_open).click()
        await self.page.locator(locator_plugin_html_block).click()
        
        await self.page.wait_for_load_state('networkidle', timeout=10000)
        html_locator = self.page.locator("div.mce-codeblock-content").locator("textarea").last
        await html_locator.fill(html)
        await self.page.locator("div.mce-codeblock-btn-submit").click()
        await self.page.wait_for_load_state('networkidle', timeout=10000)
    
    async def async_publish(self):
        await self.page.locator("button#publish-layer-btn").click()
        await self.set_public()
        await self.page.locator("button#publish-btn").click()
        
    async def append_html_with_tinymce(self, html: str):
        await self.page.evaluate(
            """
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
            """,
            html
        )
        
    async def set_public(self):
        await self.page.wait_for_load_state('networkidle', timeout=10000)
        await self.page.locator('input#open20').click()
        await self.page.wait_for_load_state('networkidle', timeout=10000)
        