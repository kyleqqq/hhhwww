import asyncio

from libs.base import BaseClient


class HuaWei(BaseClient):

    def __init__(self):
        super().__init__()
        self.url = 'https://devcloud.huaweicloud.com/bonususer/mobile/home'

    async def handler(self, username, password, **kwargs):
        self.logger.info(f'{username} start login.')
        await self.page.waitForSelector('#personalAccountInputId .tiny-input-text', {'visible': True})
        await self.page.type('#personalAccountInputId .tiny-input-text', username)
        await self.page.type('#personalPasswordInputId .tiny-input-text', password)
        await self.page.click('#btn_submit')
        await asyncio.sleep(5)

        page_url = self.page.url
        self.logger.info(page_url)
        await self.page.waitForSelector('.mobile-loading-btn-body', {'visible': True})
        await asyncio.sleep(3)

        sign_txt = str(await self.page.Jeval('.mobile-loading-btn-body', 'el => el.textContent')).strip()
        credit = str(await self.page.Jeval('.count', 'el => el.textContent')).strip()
        self.logger.info(sign_txt, credit)

        if sign_txt.find('今日已签到') == -1:
            await self.page.click('.mobile-loading-btn-body')
            await asyncio.sleep(3)
            new_credit = str(await self.page.Jeval('.count', 'el => el.textContent')).strip()
            self.logger.info(new_credit)

        await asyncio.sleep(1)
