import asyncio
import os
import time

import requests

from libs.base import BaseClient


class HuaWei(BaseClient):

    def __init__(self):
        super().__init__()
        self.url = 'https://devcloud.huaweicloud.com/bonususer/home/makebonus'
        self.bonus_url = 'https://devcloud.huaweicloud.com/bonususer/v2/bonus_flows?page_no=1&page_size=4'
        self.me_url = 'https://devcloud.huaweicloud.com/bonususer/rest/me?_1596849192871'
        self.http = requests.sessions

    async def handler(self, username, password, **kwargs):
        self.logger.info(f'{username} start login.')
        await self.page.waitForSelector('#personalAccountInputId .tiny-input-text', {'visible': True})
        await self.page.type('#personalAccountInputId .tiny-input-text', username)
        await self.page.type('#personalPasswordInputId .tiny-input-text', password)
        await self.page.click('#btn_submit')
        await asyncio.sleep(5)

        credit = await self.get_credit()
        message = f'#### {username} {credit}'
        self.logger.info(f'码豆: {credit}')

        await self.sign_task()
        await asyncio.sleep(2)

        await self.open_code_task()
        await asyncio.sleep(2)

        await self.open_ide_task()
        await asyncio.sleep(2)

        await self.push_code_task(kwargs.get('git_url'))
        await asyncio.sleep(2)

        await self.check_code()
        await self.deploy_run()
        await self.run_api_test()
        await self.run_pipeline()

        new_credit = await self.get_credit()
        self.logger.info(f'码豆: {new_credit}')
        message = f'{message} -> {new_credit}'
        self.logger.info(self.send_message(message, '华为云码豆'))

        await asyncio.sleep(1)

    async def get_credit(self):
        if self.page.url != self.url:
            await self.page.goto(self.url, {'waitUntil': 'load'})

        await self.page.waitForSelector('#homeheader-coins', {'visible': True})
        return str(await self.page.Jeval('#homeheader-coins', 'el => el.textContent')).strip()

    async def sign_task(self):
        try:
            await self.page.waitForSelector('#homeheader-signin, #homeheader-signined', {'visible': True})

            info = await self.page.Jeval(
                '#homeheader-signin span.button-content, #homeheader-signined  span.button-content',
                'el => el.textContent')
            sign_txt = str(info).strip()
            self.logger.info(sign_txt)
            if sign_txt.find('已签到') == -1:
                await self.page.click('#homeheader-signin')
                await asyncio.sleep(3)
        except Exception as e:
            self.logger.warning(e)

    async def get_new_page(self, a=1, b=1, task=None):
        if self.page.url != self.url:
            await self.page.goto(self.url, {'waitUntil': 'load'})

        self.logger.info(f'{task} -> {self.page.url}')
        await self.page.waitForSelector('#daily-mission-wrapper', {'visible': True})

        await self.page.click(
            f'#daily-mission-wrapper div.ng-star-inserted:nth-child(1) ul li.ng-star-inserted:nth-child({a})')
        await asyncio.sleep(1)

        node = f'#daily-mission-wrapper div.ng-star-inserted:nth-child(1) .devui-tab-content #experience-missions-{b}'
        is_done = None
        try:
            is_done = await self.page.querySelector(f"{node} .complate-img")
        except Exception as e:
            self.logger.debug(e)

        if is_done:
            raise Exception(f'{task} -> 任务已完成.')

        await self.page.click(node)
        await asyncio.sleep(1)

        await self.page.click('.modal.in .button-content'),
        await asyncio.sleep(5)

        # await asyncio.gather(
        #     self.page.waitForNavigation({'waitUntil': 'load'}),
        #     self.page.click('.modal.in .button-content'),
        # )

        page_list = await self.browser.pages()
        return page_list[-1]

    async def close_page(self):
        page_list = await self.browser.pages()
        if len(page_list) > 1:
            page = page_list[-1]
            if page.url != self.url:
                await page.close()

    async def open_code_task(self):
        try:
            new_page = await self.get_new_page(1, 1, task='CloudIDE打开代码')
            await new_page.waitForSelector('.btn_cloudide', {'visible': True})
            await new_page.click('.btn_cloudide')
            await asyncio.sleep(20)
            # await asyncio.wait([
            #     new_page.click('.btn_cloudide'),
            #     new_page.waitForNavigation(),
            # ])
            # await asyncio.gather(
            #     new_page.waitForNavigation({'waitUntil': 'load'}),
            #     new_page.click('.modal.in .button-content'),
            # )
            await new_page.close()
        except Exception as e:
            self.logger.warning(e)
        finally:
            await self.close_page()
        await asyncio.sleep(1)

    async def open_ide_task(self):
        try:
            new_page = await self.get_new_page(8, 0, task='启动CloudIDE实例')
            await new_page.waitForSelector('.trial-stack-info', {'visible': True})
            await new_page.click('.trial-stack-info .stack-content .stack-position .devui-btn')
            await asyncio.sleep(20)
            await new_page.close()
        except Exception as e:
            self.logger.warning(e)
        finally:
            await self.close_page()

    async def push_code_task(self, git_url):
        if git_url:
            try:
                await self.get_new_page(1, 2, task='提交代码')

                now_time = time.strftime('%Y-%m-%d %H:%M:%S')
                cmd = [
                    'cd /tmp',
                    'git config --global user.name "caoyufei" && git config --global user.email "atcaoyufei@gmail.com"',
                    f'git clone {git_url}',
                    'cd /tmp/crawler',
                    f'echo "{now_time}" >> time.txt',
                    "git add .",
                    "git commit -am 'time'",
                    "git push origin master",
                ]
                os.system(' && '.join(cmd))
                os.system('rm -rf /tmp/crawler')
                await asyncio.sleep(1)
            except Exception as e:
                self.logger.warning(e)
            finally:
                await self.close_page()

    async def check_code(self):
        try:
            new_page = await self.get_new_page(2, 1, task='执行代码检查')
            await new_page.waitForSelector('div.g-dropdown', {'visible': True})
            await new_page.click('div.g-dropdown:nth-child(1)')
            await asyncio.sleep(3)
            await new_page.click('#task_execute_crawler')
            await asyncio.sleep(5)
            await new_page.close()
        except Exception as e:
            self.logger.warning(e)
        finally:
            await self.close_page()

    async def deploy_run(self):
        try:
            new_page = await self.get_new_page(4, 1, task='执行部署')
            await new_page.waitForSelector('#rf-task-execute', {'visible': True})
            await new_page.click('#rf-task-execute')
            await asyncio.sleep(3)
            await new_page.close()
        except Exception as e:
            self.logger.warning(e)
        finally:
            await self.close_page()

    async def run_test(self):
        try:
            new_page = await self.get_new_page(5, 1, task='执行手工测试用例')
            await asyncio.sleep(2)
            await new_page.click('#global-guidelines .icon-close')
            await asyncio.sleep(1)
            await new_page.click('.guide-container .icon-close')
            await asyncio.sleep(1)
            await new_page.waitForSelector('div.devui-table-view', {'visible': True})
            string = await new_page.Jeval('div.devui-table-view tbody tr:nth-child(1) td:nth-child(12)',
                                          'el => el.outerHTML')
            print(string)

            await new_page.evaluate(
                '''() =>{ document.querySelector('div.devui-table-view tbody tr:nth-child(1) td:nth-child(12) i.icon-run').click(); }''')
            # await new_page.click('div.devui-table-view tbody tr:nth-child(1) td:nth-child(12) i.icon-run')

            await asyncio.sleep(5)
            await new_page.close()
        except Exception as e:
            self.logger.exception(e)
        finally:
            await self.close_page()

    async def run_api_test(self):
        try:
            new_page = await self.get_new_page(6, 1, task='执行接口测试用例')
            await asyncio.sleep(2)
            await new_page.click('#global-guidelines .icon-close')
            await asyncio.sleep(1)
            await new_page.click('.guide-container .icon-close')
            await asyncio.sleep(1)
            await new_page.click('#testtype_1')
            await asyncio.sleep(1)
            await new_page.evaluate(
                '''() =>{ document.querySelector('div.devui-table-view tbody tr:nth-child(1) i.icon-run').click(); }''')
            await asyncio.sleep(5)
            await new_page.close()
        except Exception as e:
            self.logger.warning(e)
        finally:
            await self.close_page()

    async def run_pipeline(self):
        try:
            new_page = await self.get_new_page(7, 1, task='执行流水线')
            await asyncio.sleep(1)
            await new_page.evaluate(
                '''() =>{ document.querySelector('div.devui-table-view tbody tr:nth-child(1) .icon-run').click(); }''')
            await asyncio.sleep(2)
            await new_page.click('.modal.in .devui-btn-stress')
            await asyncio.sleep(5)
            await new_page.close()
        except Exception as e:
            self.logger.warning(e)
        finally:
            await self.close_page()
