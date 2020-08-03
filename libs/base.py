import logging
from typing import Optional

from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.page import Page


class BaseClient:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.url = None

    async def run(self, **kwargs):
        self.browser = await launch(ignorehttpserrrors=True, headless=kwargs.get('headless', True),
                                    args=['--disable-infobars', '--no-sandbox', '--start-maximized'])
        self.page = await self.browser.newPage()
        await self.page.setUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36')
        await self.page.setViewport({'width': 1200, 'height': 768})
        await self.page.goto(self.url, {'waitUntil': 'load'})
        try:
            await self.handler(**kwargs)
        except Exception as e:
            self.logger.warning(e)
        finally:
            await self.close()

    async def handler(self, **kwargs):
        raise RuntimeError

    async def close(self):
        await self.page.close()
        await self.browser.close()

    @staticmethod
    async def close_dialog(dialog):
        await dialog.dismiss()

    @staticmethod
    async def accept_dialog(dialog):
        await dialog.accept()
