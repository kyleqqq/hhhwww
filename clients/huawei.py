import asyncio
import os
from datetime import datetime, timezone, timedelta

from libs.base_huawei import BaseHuaWei


class HuaWei(BaseHuaWei):

    def __init__(self):
        super().__init__()

    async def handler(self, **kwargs):
        self.logger.info(f'{self.username} start login.')
        await self.page.waitForSelector('#personalAccountInputId .tiny-input-text', {'visible': True})
        if kwargs.get('iam'):
            await self.iam_login(self.username, self.password, kwargs.get('parent'))
        else:
            await self.login(self.username, self.password)

        utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
        h = int(utc_dt.astimezone(timezone(timedelta(hours=8))).strftime('%H'))
        self.logger.info(f'not hours: {h}')

        if h <= 12:
            await self.check_project()
            await self.sign_task()
            await self.start()

        if h >= 12:
            await self.delete_project()
            await self.delete_function()
            await self.delete_api()
            await self.delete_api_group()

        # await self.init_account()

        return await self.get_credit()

    async def login(self, username, password):
        await self.page.type('#personalAccountInputId .tiny-input-text', username)
        await asyncio.sleep(0.5)
        await self.page.type('#personalPasswordInputId .tiny-input-text', password)
        await self.page.click('#btn_submit')
        await asyncio.sleep(5)

    async def iam_login(self, username, password, parent):
        await self.page.click('#subUserLogin')
        await asyncio.sleep(1)

        await self.page.waitForSelector('#IAMAccountInputId .tiny-input-text', {'visible': True})

        self.parent_user = os.environ.get('PARENT_USER', parent)
        await self.page.type('#IAMAccountInputId .tiny-input-text', self.parent_user)
        await self.page.type('#IAMUsernameInputId .tiny-input-text', username)
        await asyncio.sleep(0.5)
        await self.page.type('#IAMPasswordInputId .tiny-input-text', password)
        await self.page.click('#loginBtn #btn_submit')
        await asyncio.sleep(5)

    async def get_cookies(self):
        cookies = await self.page.cookies()
        new_cookies = {}
        for cookie in cookies:
            new_cookies[cookie['name']] = cookie['value']
        return new_cookies
