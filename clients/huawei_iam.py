import asyncio
import random
import string

from libs.base_huawei import BaseHuaWei


class HuaWeiIam(BaseHuaWei):

    def __init__(self):
        super().__init__()

    async def handler(self, username, password, **kwargs):
        self.logger.info(f'{username} start login.')
        await self.page.waitForSelector('#personalAccountInputId .tiny-input-text', {'visible': True})
        await self.page.click('#subUserLogin')
        await asyncio.sleep(1)

        await self.page.waitForSelector('#IAMAccountInputId .tiny-input-text', {'visible': True})

        parent_user = 'caoyufei' if username.find('yufei') != -1 else 'atzouhua'
        await self.page.type('#IAMAccountInputId .tiny-input-text', parent_user)
        await self.page.type('#IAMUsernameInputId .tiny-input-text', username)
        await self.page.type('#IAMPasswordInputId .tiny-input-text', password)
        await self.page.click('#loginBtn #btn_submit')
        await asyncio.sleep(6)

        await self.sign_task()

        await self.start(**kwargs)

        await self.print_credit(username)

        await asyncio.sleep(1)
