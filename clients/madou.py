import asyncio

from libs.base import BaseClient


class MaDou(BaseClient):

    def __init__(self):
        super().__init__()
        self.url = 'https://devcloud.huaweicloud.com/bonususer/home/makebonus'

    async def handler(self, username, password, **kwargs):
        await self.page.waitForSelector('#personalAccountInputId .tiny-input-text', {'visible': True})
        await self.page.type('#personalAccountInputId .tiny-input-text', username)
        await self.page.type('#personalPasswordInputId .tiny-input-text', password)
        await self.page.click('#btn_submit')
        await asyncio.sleep(3)

        self.logger.info(self.page.url)
        # await self.page.goto(self.url, {'waitUntil': 'load'})

        await self.page.waitForSelector('#daily-mission-wrapper', {'visible': True})

        await self.page.click(
            '#daily-mission-wrapper > div.ng-star-inserted:nth-child(1) ul li.ng-star-inserted:nth-child(2)')
        await asyncio.sleep(1)

        # element = await self.page.querySelector(
        #     '#daily-mission-wrapper > div.ng-star-inserted:nth-child(1) .devui-tab-content li:nth-child(2)')
        # self.logger.info(element)
        # self.logger.info(await (await element.getProperty('textContent')).jsonValue())

        await self.page.click(
            '#daily-mission-wrapper div.ng-star-inserted:nth-child(1) .devui-tab-content #experience-missions-1')
        await asyncio.sleep(1)

        await self.page.click('.modal.in .button-content')
        await asyncio.sleep(5)

        page_list = await self.browser.pages()
        new_page = page_list[-1]
        await new_page.waitForSelector('.btn_cloudide', {'visible': True})
        await new_page.click('.btn_cloudide')

        await asyncio.sleep(20)

        print(len(page_list))
        for page in page_list:
            print(page.url)

        await asyncio.sleep(10)
