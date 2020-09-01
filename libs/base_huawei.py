import asyncio
import os
import random
import string
import time

from libs.base import BaseClient

name_map = {
    '项目管理': [['week_new_project', 0]],
    '代码托管': [['week_new_git', 0], ['open_code_task', 1], ['push_code_task', 2]],
    'CloudIDE': [['open_ide_task', 0]],
    '代码检查': [['week_new_code_check', 0], ['check_code_task', 1]],
    '部署': [['deploy_task', 1]],
    '发布': [['week_upload_task', 0]],
    '流水线': [['pipeline_task', 1]],
    '接口测试': [['week_new_api_test_task', 0], ['api_test_task', 1]],
    '测试管理': [['week_new_test_task', 0]],
    'APIG网关': [['week_new_api_task', 0], ['week_run_api_task', 1]],
    '函数工作流': [['week_new_fun_task', 0]],
    '使用API Explorer在线调试': 'api_explorer_task',
    '使用Devstar生成代码工程': 'dev_star_task',
    '浏览Codelabs代码示例': 'view_code_task'
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

        id_list = ['experience-missions', 'middleware-missions']  # 'middleware-missions', 'experience-missions'
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
                        self.logger.warning(f'{task_name} -> DONE.')
                        continue

                    # print(await self.page.Jeval(f'{node}', 'el => el.outerHTML'))
                    await self.run_task(node, task_name, item[0], **kwargs)

            await asyncio.sleep(2)

    async def regular(self):
        _id = 'regular-missions'
        await self.page.waitForSelector(f'#{_id}', {'visible': True})
        elements = await self.page.querySelectorAll(f'#{_id} .daily-list li')
        for i, element in enumerate(elements):
            node = f'#{_id} #feedback-{i}'
            task_name = await self.page.Jeval(f'{node} h5', 'el => el.textContent')
            if not name_map.get(task_name):
                continue

            if await self.is_done(node):
                self.logger.warning(f'{task_name} -> DONE.')
                continue

            await self.run_task(node, task_name, name_map.get(task_name))
            await asyncio.sleep(1)

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
        await asyncio.sleep(2)
        self.logger.info(f'{task_name}')
        self.task_page = await self.get_new_page()
        try:
            if task_fun == 'push_code_task':
                self.git_url = kwargs.get('git_url')
            await getattr(self, task_fun)()
            await asyncio.sleep(1)
            self.logger.warning(f'{task_name} -> DONE.')
        except Exception as e:
            self.logger.warning(e)
        finally:
            await self.close_page()
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
            raise Exception(f'{task} -> DONE.')

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
        await self.page.click('.modal.in .modal-footer .devui-btn')
        await asyncio.sleep(2)
        page_list = await self.browser.pages()
        await page_list[-1].setViewport({'width': 1200, 'height': 768})
        return page_list[-1]

    async def close_page(self):
        page_list = await self.browser.pages()
        if len(page_list) > 1:
            page = page_list[-1]
            if page.url != self.url:
                await page.close()

    async def api_explorer_task(self):
        _url = 'https://apiexplorer.developer.huaweicloud.com/apiexplorer/doc?product=APIExplorer&api=ListProductsV3'
        await self.task_page.goto(_url, {'waitUntil': 'load'})
        await self.task_page.waitForSelector('#debug', {'visible': True})
        await self.task_page.click('#debug')
        await asyncio.sleep(3)

    async def dev_star_task(self):
        await self.task_page.waitForSelector('#confirm-download-btn', {'visible': True})
        await self.task_page.click('#confirm-download-btn')
        await asyncio.sleep(5)

    async def view_code_task(self):
        await self.task_page.waitForSelector('#code-template-list', {'visible': True})
        await self.task_page.click('#code-template-card0')
        await asyncio.sleep(5)

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
        try:
            await self.task_page.click('.region-modal-button-content .region-modal-button-common')
            await asyncio.sleep(1)
        except Exception as e:
            self.logger.debug(e)

        await self.task_page.click(
            '.trial-stack-info .trial-stack:nth-child(1) .stack-content .stack-position .devui-btn')
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

    async def week_new_project(self):
        await self.task_page.waitForSelector('.modal.in', {'visible': True})
        await self.task_page.click('.modal.in .devui-btn:nth-child(1)')
        await asyncio.sleep(5)

    async def week_new_git(self):
        await self.task_page.waitForSelector('.pull-right', {'visible': True})
        await self.task_page.click('.pull-right .devui-btn-primary')
        await asyncio.sleep(2)
        await self.task_page.type('#rname', ''.join(random.choices(string.ascii_letters, k=6)))
        await self.task_page.click('#newAddRepoBtn')
        await asyncio.sleep(5)

    async def week_new_code_check(self):
        await self.task_page.waitForSelector('.pull-right', {'visible': True})
        await self.task_page.click('.pull-right .devui-btn-primary')
        await asyncio.sleep(5)

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
        await asyncio.sleep(3)

    async def week_new_test_task(self):
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

    async def week_new_api_test_task(self):
        await self._close_test()
        await self._tab_api_test()
        await self.task_page.waitForSelector('div.create-case', {'visible': True})
        await self.task_page.click('div.create-case')
        await asyncio.sleep(2)
        await self.task_page.type('#caseName', ''.join(random.choices(string.ascii_letters, k=6)))
        await self.task_page.click('div.footer .devui-btn-stress')
        await asyncio.sleep(3)

    async def week_new_api_task(self):
        await asyncio.sleep(2)
        await self.task_page.waitForSelector('div.ti-intro-modal', {'visible': True})
        await asyncio.sleep(10)

    async def week_run_api_task(self):
        await asyncio.sleep(2)
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
        url = self.task_page.url
        if url.find('serverless/dashboard') == -1:
            url = f'{url}#/serverless/dashboard'
            await self.task_page.goto(url, {'waitUntil': 'load'})

        self.logger.info(self.task_page.url)
        await asyncio.sleep(2)
        await self.task_page.waitForSelector('#rightWrap', {'visible': True})
        await self.task_page.click('#rightWrap .ant-row .ant-btn')
        await asyncio.sleep(1)
        await self.task_page.type('#name', ''.join(random.choices(string.ascii_letters, k=6)))
        await self.task_page.waitForSelector('.preview', {'visible': True})
        await self.task_page.click('.preview .ant-btn-primary')
        await asyncio.sleep(5)

    async def delete_project(self):
        page = await self.browser.newPage()
        domains = ['https://devcloud.huaweicloud.com', 'https://devcloud.cn-north-4.huaweicloud.com',
                   'https://devcloud.cn-east-3.huaweicloud.com']

        try:
            for domain in domains:
                url = f'{domain}/projects/v2/project/list?sort=&search=&page_no=1&page_size=40&project_type=&archive=1'
                res = await page.goto(url, {'waitUntil': 'load'})
                data = await res.json()
                if data.get('error'):
                    continue

                for item in data['result']['project_info_list']:
                    if item['name'].find('DevOps') != -1:
                        self.logger.warning(f"delete {item['name']}")
                        delete_url = f"{domain}/projects/project/{item['project_id']}/config/info"
                        await page.goto(delete_url, {'waitUntil': 'load'})
                        await asyncio.sleep(2)
                        await page.click('.form-container .margin-right-s .devui-btn:nth-child(1)')
                        await asyncio.sleep(2)
                        await page.type('#deleteProject .projectInput', item['name'])
                        await asyncio.sleep(0.5)
                        await page.click('.dialog-footer .devui-btn-primary')
                        await asyncio.sleep(1)
                        break
                return domain
        finally:
            await page.close()

    async def delete_api(self):
        page = await self.browser.newPage()
        try:
            await page.goto('https://console.huaweicloud.com/apig/?region=cn-north-4#/apig/multiLogical/openapi/list',
                            {'waitUntil': 'load'})
            await page.setViewport({'width': 1200, 'height': 768})
            await page.waitForSelector('#openapi_list')
            await asyncio.sleep(10)
            elements = await page.querySelectorAll('#openapi_list tr')
            if len(elements) < 2:
                return

            # 下线
            await page.click('#openapi_list tr:nth-child(1) th:nth-child(1)')
            await asyncio.sleep(0.5)
            await page.click('.apiList-groups .cti-button:nth-child(3) .cti-btn-container')
            await asyncio.sleep(1)
            await page.click('.ti-modal-dialog .cti-button:nth-child(1) .cti-btn-container')
            await asyncio.sleep(2)

            # 删除
            await page.click('#openapi_list tr:nth-child(1) th:nth-child(1)')
            await asyncio.sleep(0.5)
            await page.click('.apiList-groups .cti-button:nth-child(4) .cti-btn-container')
            await asyncio.sleep(3)
            await page.type('#deleteContent-text', 'DELETE')
            await asyncio.sleep(0.5)
            await page.click('.ti-modal-dialog .cti-button:nth-child(1) .cti-btn-container')
            await asyncio.sleep(2)
        finally:
            await page.close()

    async def delete_api_group(self):
        page = await self.browser.newPage()
        try:
            await page.goto('https://console.huaweicloud.com/apig/?region=cn-north-4#/apig/multiLogical/openapi/group',
                            {'waitUntil': 'load'})
            await page.setViewport({'width': 1200, 'height': 768})
            await page.waitForSelector('#openapi_group')
            await asyncio.sleep(5)
            elements = await page.querySelectorAll('#openapi_group tbody tr')
            if len(elements) < 1:
                return

            await page.click('#openapi_group tbody tr:nth-child(1) td:nth-child(1) a')
            await asyncio.sleep(2)
            await page.click('.cti-fl-right .cti-button:nth-child(4) .cti-btn-container')
            await asyncio.sleep(1)
            await page.type('#tiny-text', 'DELETE')
            await asyncio.sleep(0.5)
            await page.click('#delG')
            await asyncio.sleep(2)
        finally:
            await page.close()

    async def _close_test(self):
        try:
            await asyncio.sleep(1)
            await self.task_page.click('#global-guidelines .icon-close')
            await asyncio.sleep(2)
            await self.task_page.click('.guide-container .icon-close')
            await asyncio.sleep(1)
        except Exception as e:
            self.logger.debug(e)

    async def _tab_api_test(self):
        await self.task_page.click('#testtype_1')
        await asyncio.sleep(1)
