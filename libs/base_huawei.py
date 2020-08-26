import asyncio
import os
import random
import string
import time

from libs.base import BaseClient

name_map = {
    # '发布': [['week_upload_task', 0]],
    'CloudIDE': [['open_ide_task', 0]],
    '接口测试': [['api_test_task', 1]],
    '部署': [['deploy_task', 1]],
    '流水线': [['pipeline_task', 1]],
    '代码检查': [['check_code_task', 1]],
    '代码托管': [['open_code_task', 1], ['push_code_task', 2]],
    # 'APIG网关': [['week_run_api_task', 1]],
    # '函数工作流': [['week_new_fun_task', 0]],
}


class BaseHuaWei(BaseClient):

    def __init__(self):
        super().__init__()
        self.url = 'https://devcloud.huaweicloud.com/bonususer/home/makebonus'
        self.git_url = None
        self.task_page = None

    async def start(self, **kwargs):
        if self.page.url != self.url:
            await self.page.goto(self.url, {'waitUntil': 'load'})

        id_list = ['experience-missions']  # 'middleware-missions', 'experience-missions'
        for _id in id_list:
            await self.page.waitForSelector(f'#{_id}', {'visible': True})
            elements = await self.page.querySelectorAll(f'#{_id} ul.devui-nav li.ng-star-inserted')
            for element in elements:
                name = str(await element.Jeval('a', 'el => el.textContent')).strip()
                items = name_map.get(name)
                if items is None:
                    continue

                for item in items:
                    await element.click()
                    await asyncio.sleep(1)

                    node = f'#{_id} #{_id}-{item[1]}'
                    task_name = await self.page.Jeval(f'{node} h5', 'el => el.textContent')
                    if await self.is_done(node):
                        self.logger.warning(f'{task_name} -> 任务已完成.')
                        continue

                    # print(await self.page.Jeval(f'{node}', 'el => el.outerHTML'))
                    await self.run_task(node, task_name, item[0], **kwargs)

            await asyncio.sleep(5)

    async def is_done(self, node):
        try:
            is_done = await self.page.querySelector(f"{node} .complate-img")
            if is_done:
                return True
        except Exception as e:
            self.logger.debug(e)
        return False

    async def run_task(self, node, task_name, task_fun, **kwargs):
        await self.page.click(node)
        await asyncio.sleep(5)
        self.logger.info(f'{task_name} -> 任务开始.')
        self.task_page = await self.get_new_page()

        try:
            if task_fun == 'push_code_task':
                self.git_url = kwargs.get('git_url')
            await getattr(self, task_fun)()
            await self.task_page.close()
        except Exception as e:
            self.logger.warning(e)
        finally:
            await self.close_page()

        await asyncio.sleep(1)
        self.logger.warning(f'{task_name} -> 任务结束.')
        await asyncio.sleep(1)

    async def get_credit(self):
        if self.page.url != self.url:
            await self.page.goto(self.url, {'waitUntil': 'load'})
        else:
            await self.page.reload({'waitUntil': 'load'})

        await asyncio.sleep(2)
        await self.page.waitForSelector('#homeheader-coins', {'visible': True})
        return str(await self.page.Jeval('#homeheader-coins', 'el => el.textContent')).strip()

    async def print_credit(self, user_name):
        new_credit = await self.get_credit()
        self.logger.info(f'码豆: {new_credit}')
        message = f'{user_name} -> {new_credit}'
        self.send_message(message, '华为云码豆')

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

    async def get_new_page1(self, a=1, b=1, task=None):
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

    async def get_new_page(self):
        await self.page.click('.modal.in .button-content')
        await asyncio.sleep(5)
        page_list = await self.browser.pages()
        return page_list[-1]

    async def close_page(self):
        page_list = await self.browser.pages()
        if len(page_list) > 1:
            page = page_list[-1]
            if page.url != self.url:
                await page.close()

    async def open_code_task(self):
        await self.task_page.waitForSelector('.btn_cloudide', {'visible': True})
        await self.task_page.click('.btn_cloudide')
        await asyncio.sleep(20)
        # await asyncio.wait([
        #     self.task_page.click('.btn_cloudide'),
        #     self.task_page.waitForNavigation(),
        # ])
        # await asyncio.gather(
        #     self.task_page.waitForNavigation({'waitUntil': 'load'}),
        #     self.task_page.click('.modal.in .button-content'),
        # )

    async def open_ide_task(self):
        await self.task_page.waitForSelector('.trial-stack-info', {'visible': True})
        await self.task_page.click('.trial-stack-info .stack-content .stack-position .devui-btn')
        await asyncio.sleep(20)

    async def push_code_task(self):
        if self.git_url:
            now_time = time.strftime('%Y-%m-%d %H:%M:%S')
            cmd = [
                'cd /tmp',
                'git config --global user.name "caoyufei" && git config --global user.email "atcaoyufei@gmail.com"',
                f'git clone {self.git_url}',
                'cd /tmp/crawler',
                f'echo "{now_time}" >> time.txt',
                "git add .",
                "git commit -am 'time'",
                "git push origin master",
            ]
            os.system(' && '.join(cmd))
            os.system('rm -rf /tmp/crawler')
            await asyncio.sleep(1)

    async def check_code_task(self):
        await self.task_page.waitForSelector('div.g-dropdown', {'visible': True})
        await self.task_page.click('div.g-dropdown:nth-child(1)')
        await asyncio.sleep(2)
        await self.task_page.click('#task_execute_crawler')
        await asyncio.sleep(3)

    async def deploy_task(self):
        await self.task_page.waitForSelector('#rf-task-execute', {'visible': True})
        await self.task_page.click('#rf-task-execute')
        await asyncio.sleep(3)

    async def run_test(self):
        await self._close_test()
        await self.task_page.waitForSelector('div.devui-table-view', {'visible': True})
        string = await self.task_page.Jeval('div.devui-table-view tbody tr:nth-child(1) td:nth-child(12)',
                                            'el => el.outerHTML')
        print(string)

        await self.task_page.evaluate(
            '''() =>{ document.querySelector('div.devui-table-view tbody tr:nth-child(1) td:nth-child(12) i.icon-run').click(); }''')
        # await self.task_page.click('div.devui-table-view tbody tr:nth-child(1) td:nth-child(12) i.icon-run')

        await asyncio.sleep(5)

    async def api_test_task(self):
        await self._close_test()
        await self._tab_api_test()
        await self.task_page.evaluate(
            '''() =>{ document.querySelector('div.devui-table-view tbody tr:nth-child(1) i.icon-run').click(); }''')
        await asyncio.sleep(5)

    async def pipeline_task(self):
        await asyncio.sleep(1)
        await self.task_page.evaluate(
            '''() =>{ document.querySelector('div.devui-table-view tbody tr:nth-child(1) .icon-run').click(); }''')
        await asyncio.sleep(2)
        await self.task_page.click('.modal.in .devui-btn-stress')
        await asyncio.sleep(5)

    async def week_project(self):
        try:
            await self.task_page.waitForSelector('.modal.in', {'visible': True})
            await self.task_page.click('.modal.in .devui-btn:nth-child(1)')
            await asyncio.sleep(5)
            await self.task_page.close()
        except Exception as e:
            self.logger.warning(e)
        finally:
            await self.close_page()

    async def week_upload_task(self):
        await self.task_page.waitForSelector('#releasemanUploadDrop', {'visible': True})
        # html = await self.task_page.Jeval('div.devui-table-view tbody tr:nth-child(1) td',
        #                                   'el => el.outerHTML')
        # print(html)

        await self.task_page.click('#releasemanUploadDrop tbody tr:nth-child(1) td a.column-link')
        await asyncio.sleep(3)
        await self.task_page.waitForSelector('#upload_file', {'visible': True})
        f = await self.task_page.querySelector('#releaseman-file-select')
        await f.uploadFile(__file__)

    async def week_test(self):
        try:
            await asyncio.sleep(2)
            await self.task_page.click('#global-guidelines .icon-close')
            await asyncio.sleep(1)
            await self.task_page.click('.guide-container .icon-close')
            await asyncio.sleep(1)
            await self.task_page.waitForSelector('div.create-case', {'visible': True})
            await self.task_page.click('div.create-case')
            await asyncio.sleep(5)
            await self.task_page.type('#caseName', ''.join(random.choices(string.ascii_letters, k=6)))
            await self.task_page.click('div.footer .devui-btn-stress')
            await asyncio.sleep(5)
            await self.task_page.close()
        except Exception as e:
            self.logger.warning(e)
        finally:
            await self.close_page()

    async def week_api_test(self):
        await self._close_test()
        await self._tab_api_test()
        await self.task_page.waitForSelector('div.create-case', {'visible': True})
        await self.task_page.click('div.create-case')
        await asyncio.sleep(2)
        await self.task_page.type('#caseName', ''.join(random.choices(string.ascii_letters, k=6)))
        await self.task_page.click('div.footer .devui-btn-stress')
        await asyncio.sleep(3)

    async def week_new_api_task(self):
        await asyncio.sleep(5)
        await self.task_page.waitForSelector('div.ti-intro-modal', {'visible': True})
        await asyncio.sleep(10)

    async def week_run_api_task(self):
        await asyncio.sleep(5)
        await self.task_page.waitForSelector('div.ti-intro-modal', {'visible': True})
        await self.task_page.click('div.ti-intro-modal .ti-btn-danger')
        await asyncio.sleep(2)
        await self.task_page.waitForSelector('#send', {'visible': True})
        await self.task_page.click('#send')
        await asyncio.sleep(2)
        await self.task_page.click('.pull-left .cti-button')
        await asyncio.sleep(5)
        await self.task_page.click('.pull-right.mr10.cti-button')
        await asyncio.sleep(5)
        await self.task_page.click('.ti-btn-danger.ml10.ng-binding')

    async def week_new_fun_task(self):
        await asyncio.sleep(3)
        await self.task_page.waitForSelector('#rightWrap', {'visible': True})
        await self.task_page.click('#rightWrap .ant-row .ant-btn')
        await asyncio.sleep(2)
        await self.task_page.type('#name', ''.join(random.choices(string.ascii_letters, k=6)))
        await self.task_page.click('.preview .ant-btn-primary')
        await asyncio.sleep(15)

    async def _close_test(self):
        await asyncio.sleep(2)
        await self.task_page.click('#global-guidelines .icon-close')
        await asyncio.sleep(1)
        await self.task_page.click('.guide-container .icon-close')
        await asyncio.sleep(1)

    async def _tab_api_test(self):
        await self.task_page.click('#testtype_1')
        await asyncio.sleep(1)
