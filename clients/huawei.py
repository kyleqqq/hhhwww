import asyncio
import json
import os

import redis

from libs.base_huawei import BaseHuaWei


class HuaWei(BaseHuaWei):

    def __init__(self):
        super().__init__()

    async def handler(self, username, password, git, parent=None, iam=False):
        self.logger.info(f'{username} start login.')
        await self.page.waitForSelector('#personalAccountInputId .tiny-input-text', {'visible': True})
        if iam:
            await self.iam_login(username, password, parent)
        else:
            await self.login(username, password)

        # cookies = await self.get_cookies()

        # await self.sign_task()
        # await self.delete_function()
        #
        # await self.delete_project()
        # await self.delete_api()
        # await self.delete_api_group()
        #
        # await self.start()
        #
        # await self.regular()

        # await self.print_credit(username)

        redis_password = os.environ.get('REDIS_PASSWORD', password)
        k = f'{username}_reply'
        r = redis.Redis(host='redis-10036.c1.asia-northeast1-1.gce.cloud.redislabs.com', port=10036,
                        password=redis_password)
        reply_count = r.get(k)
        if not reply_count:
            reply_count = 0

        if int(reply_count) < 5:
            r.set(k, int(reply_count) + 1, 3600 * 6)
            await self.post_reply()

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
