import asyncio
import random
import string

from clients.huawei import HuaWei


class HuaWeiIam(HuaWei):

    def __init__(self):
        super().__init__()

    async def handler(self, username, password, **kwargs):
        self.logger.info(f'{username} start login.')
        await self.page.waitForSelector('#personalAccountInputId .tiny-input-text', {'visible': True})
        await self.page.click('#subUserLogin')
        await asyncio.sleep(1)

        await self.page.type('#IAMAccountInputId .tiny-input-text', 'caoyufei')
        await self.page.type('#IAMUsernameInputId .tiny-input-text', username)
        await self.page.type('#IAMPasswordInputId .tiny-input-text', password)
        await self.page.click('#loginBtn #btn_submit')
        await asyncio.sleep(6)

        await self.new_api_test()

        await asyncio.sleep(1)

    async def new_project(self):
        try:
            new_page = await self.get_new_page(9, 0, task='体验DevOps全流程样例项目')
            await new_page.waitForSelector('.modal.in', {'visible': True})
            await new_page.click('.modal.in .devui-btn:nth-child(1)')
            await asyncio.sleep(5)
            await new_page.close()
        except Exception as e:
            self.logger.warning(e)
        finally:
            await self.close_page()

    async def new_test(self):
        try:
            new_page = await self.get_new_page(5, 0, task='创建测试用例')
            await asyncio.sleep(2)
            await new_page.click('#global-guidelines .icon-close')
            await asyncio.sleep(1)
            await new_page.click('.guide-container .icon-close')
            await asyncio.sleep(1)
            await new_page.waitForSelector('div.create-case', {'visible': True})
            await new_page.click('div.create-case')
            await asyncio.sleep(5)
            await new_page.type('#caseName', ''.join(random.choices(string.ascii_letters, k=6)))
            await new_page.click('div.footer .devui-btn-stress')
            await asyncio.sleep(5)
            await new_page.close()
        except Exception as e:
            self.logger.warning(e)
        finally:
            await self.close_page()

    async def new_api_test(self):
        try:
            new_page = await self.get_new_page(6, 0, task='创建接口测试用例')
            await asyncio.sleep(2)
            await new_page.click('#global-guidelines .icon-close')
            await asyncio.sleep(1)
            await new_page.click('.guide-container .icon-close')
            await asyncio.sleep(1)
            await new_page.click('#testtype_1')
            await new_page.waitForSelector('div.create-case', {'visible': True})
            await new_page.click('div.create-case')
            await asyncio.sleep(5)
            await new_page.type('#caseName', ''.join(random.choices(string.ascii_letters, k=6)))
            await new_page.click('div.footer .devui-btn-stress')
            await asyncio.sleep(5)
            await new_page.close()
        except Exception as e:
            self.logger.warning(e)
        finally:
            await self.close_page()
