from config import Config
from playwright.async_api import Page

class Tistory:
    def __init__(self, page: Page, cfg: Config):
        self.page = page
        self.cfg = cfg
        
    async def async_set_title(self, title: str) -> None:
        title_locator = self.get_locator("textarea#post-title-inp")
        await title_locator.fill(title)
        
    async def async_set_body(self, content: str) -> None:
        content_locator = self.get_locator("")
        await content_locator.fill(content)
        
    async def async_set_html(self, html: str) -> None:
        html_locator = self.get_locator("")
        await html_locator.fill(html)
    
    async def get_locator(self, locator_param: str):
        await self.page.wait_for_load_state(locator_param)
        return self.page.locator(locator_param)        
    