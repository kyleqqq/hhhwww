import asyncio
import os
import random
import string

from libs.base_huawei import BaseHuaWei


class HuaWeiIam(BaseHuaWei):

    def __init__(self):
        super().__init__()

    # async def handler(self, username, password, git, **kwargs):
    #     self.logger.info(f'{username} start login.')
    #     await self.page.waitForSelector('#personalAccountInputId .tiny-input-text', {'visible': True})
    #     await self.page.click('#subUserLogin')
    #     await asyncio.sleep(1)
    #
    #     await self.page.waitForSelector('#IAMAccountInputId .tiny-input-text', {'visible': True})
    #
    #     self.parent_user = os.environ.get('PARENT_USER', '')
    #     await self.page.type('#IAMAccountInputId .tiny-input-text', self.parent_user)
    #     await self.page.type('#IAMUsernameInputId .tiny-input-text', username)
    #     await asyncio.sleep(0.5)
    #     await self.page.type('#IAMPasswordInputId .tiny-input-text', password)
    #     await self.page.click('#loginBtn #btn_submit')
    #     await asyncio.sleep(5)
    #
    #     # await self.init_account()
    #
    #     await self.sign_task()
    #
    #     await self.delete_project()
    #     await self.delete_api()
    #     await self.delete_api_group()
    #
    #     await self.start()
    #
    #     await self.regular()
    #
    #     # await self.print_credit(username)
    #
    #     return await self.get_credit()
