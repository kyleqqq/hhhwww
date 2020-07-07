import asyncio
import base64
import hashlib
import hmac
import os
import time

import requests
from pyppeteer import launch


async def close_dialog(dialog):
    await dialog.dismiss()


async def accept_dialog(dialog):
    await dialog.accept()


async def get_browser(url):
    browser = await launch(ignorehttpserrrors=True, headless=True,
                           args=['--disable-infobars', '--no-sandbox', '--start-maximized'])
    page = await browser.newPage()
    page.on('dialog', lambda dialog: asyncio.ensure_future(close_dialog(dialog)))

    await page.setViewport({'width': 1200, 'height': 768})
    await page.goto(url, {'waitUntil': 'load'})
    return page, browser


def send_ding_task(text, **kwargs):
    access_token = os.environ.get('access_token', kwargs.get('access_token',
                                                             'a23392f0117f982995bec61a178dce5d8f96a69faf452d00442a0045d772d0e2'))
    secret = os.environ.get('secret',
                            kwargs.get('secret', 'SEC25b6b9851cc21443c8b020dc03562a199e3cfecd502062861fc3d2c1ae226a8d'))
    ding_url = 'https://oapi.dingtalk.com/robot/send'
    _timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign_enc = '{}\n{}'.format(_timestamp, secret).encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = base64.b64encode(hmac_code)
    json_data = {'msgtype': 'text', 'text': {'content': text}}
    params = {'access_token': access_token, 'timestamp': _timestamp, 'sign': sign}
    return requests.post(ding_url, params=params, json=json_data).json()
