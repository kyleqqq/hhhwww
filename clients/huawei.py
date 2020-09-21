import asyncio
import os
import time

import redis

from libs.base_huawei import BaseHuaWei


class HuaWei(BaseHuaWei):

    def __init__(self):
        super().__init__()

    async def handler(self, username, password, **kwargs):
        self.logger.info(f'{username} start login.')
        await self.page.waitForSelector('#personalAccountInputId .tiny-input-text', {'visible': True})
        await self.page.type('#personalAccountInputId .tiny-input-text', username)
        await asyncio.sleep(0.5)
        await self.page.type('#personalPasswordInputId .tiny-input-text', password)
        await self.page.click('#btn_submit')
        await asyncio.sleep(5)

        await self.sign_task()

        await self.delete_project()
        await self.delete_api()
        await self.delete_api_group()

        await self.start(**kwargs)

        await self.regular()

        await self.print_credit(username)

        await asyncio.sleep(1)
