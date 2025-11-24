from config import Config
from playwright.async_api import Page

class Tistory:
    def __init__(self, page: Page, cfg: Config):
        self.page = page
        self.cfg = cfg
        
    async def async_set_title(self, title: str) -> None:
        await self.page.wait_for_selector("textarea#post-title-inp")
        title_locator = self.page.locator("textarea#post-title-inp")
        await title_locator.fill(title)
        
    async def async_set_body(self, body_html: str) -> None:
        content_locator = self.page.locator("textarea#editor-tistory").last
        await content_locator.fill(body_html)
    
    async def async_set_html(self, html: str) -> None:
        await self.page.wait_for_load_state('networkidle', timeout=10000)
        await self.page.locator("button#more-plugin-btn-open").click()
        await self.page.locator("div#plugin-html-block").click()
        
        await self.page.wait_for_load_state('networkidle', timeout=10000)
        html_locator = self.page.locator("div.mce-codeblock-content").locator("textarea").last
        await html_locator.fill(html)
        await self.page.locator("div.mce-codeblock-btn-submit").click()
    
    async def async_publish(self):
        await self.page.locator().click()