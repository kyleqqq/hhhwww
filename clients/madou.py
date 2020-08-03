import asyncio
import os
import time
from pathlib import Path

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

        if self.page.url != self.url:
            await self.page.goto(self.url, {'waitUntil': 'load'})

        if self.page.url != self.url:
            self.logger.warning(self.page.url)
            return

        # await self.page.goto(self.url, {'waitUntil': 'load'})
        # element = await self.page.querySelector(
        #     '#daily-mission-wrapper > div.ng-star-inserted:nth-child(1) .devui-tab-content li:nth-child(2)')
        # self.logger.info(element)
        # self.logger.info(await (await element.getProperty('textContent')).jsonValue())

        await self.open_code_task()
        await asyncio.sleep(3)
        await self.open_ide_task()
        # await self.push_code_task()

        # print(len(page_list))
        # for page in page_list:
        #     print(page.url)

        await asyncio.sleep(2)

    async def get_new_page(self, a=2, b=1):
        await self.page.waitForSelector('#daily-mission-wrapper', {'visible': True})

        await self.page.click(
            f'#daily-mission-wrapper > div.ng-star-inserted:nth-child(1) ul li.ng-star-inserted:nth-child({a})')
        await asyncio.sleep(1)

        await self.page.click(
            f'#daily-mission-wrapper div.ng-star-inserted:nth-child(1) .devui-tab-content #experience-missions-{b}')
        await asyncio.sleep(1)

        await self.page.click('.modal.in .button-content')
        await asyncio.sleep(5)

        page_list = await self.browser.pages()
        return page_list[-1]

    async def open_code_task(self):
        try:
            new_page = await self.get_new_page()
            await new_page.waitForSelector('.btn_cloudide', {'visible': True})
            await new_page.click('.btn_cloudide')
            await asyncio.sleep(20)
            await new_page.close()
        except Exception as e:
            self.logger.warning(e)

    async def open_ide_task(self):
        try:
            new_page = await self.get_new_page(3, 0)
            await new_page.waitForSelector('.trial-stack-info', {'visible': True})
            await new_page.click('.trial-stack-info .stack-content .stack-position .devui-btn')
            await asyncio.sleep(20)
            await new_page.close()
        except Exception as e:
            self.logger.warning(e)

    async def push_code_task(self):
        await self.get_new_page(2, 2)

        now_time = time.strftime('%Y-%m-%d %H:%M:%S')
        cmd = [
            'cd /tmp',
            'git config --global user.name "caoyufei" && git config --global user.email "atcaoyufei@gmail.com"',
            'git clone git@codehub.devcloud.cn-north-4.huaweicloud.com:scylla00001/crawler.git',
            'cd /tmp/crawler',
            f'echo "{now_time}" >> time.txt',
            "git add .",
            "git commit -am 'time'",
            "git push origin master",
            "rm -rf /tmp/crawler",
            "rm -rf ~/.ssh"
        ]
        id_rsa = os.environ.get('id_rsa')
        ssh_dir = Path.home() / '.ssh'
        ssh_dir.mkdir()
        file = ssh_dir / 'id_rsa'
        file.write_text(id_rsa)

        os.system(' && '.join(cmd))
        os.system('rm -rf /tmp/crawler && rm -rf ~/.ssh')

        await asyncio.sleep(3)
