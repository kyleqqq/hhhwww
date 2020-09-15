import base64
import hashlib
import hmac
import logging
import os
import time
from typing import Optional

import requests
from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.page import Page


class BaseClient:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.url = None
        self.ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'

    async def run(self, **kwargs):
        self.browser = await launch(ignorehttpserrrors=True, headless=kwargs.get('headless', True),
                                    args=['--disable-infobars', '--no-sandbox', '--start-maximized'])
        self.page = await self.browser.newPage()
        await self.page.setUserAgent(self.ua)
        await self.page.setViewport({'width': 1200, 'height': 768})
        await self.page.goto(self.url, {'waitUntil': 'load'})

        username_list = kwargs.get('username').split(',')
        git_list = kwargs.get('git').split(',')
        password_list = kwargs.get('password').split(',')

        self.logger.warning(username_list)
        for i, username in enumerate(username_list):
            git = git_list[i]
            password = password_list[0] if len(password_list) == 1 else password_list[i]
            try:
                await self.handler(username=username, password=password, git=git)
            except Exception as e:
                self.logger.warning(e)

        await self.close()

    async def handler(self, **kwargs):
        raise RuntimeError

    async def close(self):
        await self.page.close()
        await self.browser.close()

    @staticmethod
    async def close_dialog(dialog):
        await dialog.dismiss()

    @staticmethod
    async def accept_dialog(dialog):
        await dialog.accept()

    @staticmethod
    def send_message(text, title='Notice'):
        ding_url = 'https://oapi.dingtalk.com/robot/send'
        access_token = os.environ.get('DING_TOKEN')
        _timestamp = str(round(time.time() * 1000))
        secret = 'SEC25b6b9851cc21443c8b020dc03562a199e3cfecd502062861fc3d2c1ae226a8d'
        secret_enc = secret.encode('utf-8')
        string_to_sign_enc = '{}\n{}'.format(_timestamp, secret).encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code)
        json_data = {'msgtype': 'markdown', 'markdown': {'text': text, 'title': title}}
        params = {'access_token': access_token, 'timestamp': _timestamp, 'sign': sign}
        return requests.post(ding_url, params=params, json=json_data).json()
