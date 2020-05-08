import asyncio
import base64
import codecs
import json
import os
import random
import time
from os.path import dirname, realpath
import requests
from pyppeteer import launch

BIN_URL = 'https://ioflood.com/100mbtest.bin'
ROOT_PATH = dirname(dirname(realpath(__file__)))
DATA_PATH = os.path.join(ROOT_PATH, 'data')
ACCOUNT_LIST = {'haha@dmeo666.cn': 1081}


async def close_dialog(dialog):
    await dialog.dismiss()


async def accept_dialog(dialog):
    await dialog.accept()


def decode(string):
    if len(string) % 4 != 0:
        string = string + (4 - len(string) % 4) * '='
    return str(base64.urlsafe_b64decode(string.encode()), 'UTF-8')


def to_date(timestamp):
    time_struct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d', time_struct)


def generate(subscribe_link, user_name, port):
    file = os.path.join(DATA_PATH, '{}.json'.format(user_name))
    if os.path.exists(file):
        t = os.path.getctime(file)
        print(to_date(t))

    html = requests.get(subscribe_link, timeout=5).text
    string = decode(html)
    lines = string.split('\n')
    nodes = []
    for line in lines:
        line = line.replace('vmess://', '')
        vmess = decode(line)
        if not vmess:
            continue
        nodes.append(json.loads(vmess))
    return random.choice(nodes)


def get_default_config():
    with codecs.open(os.path.join(DATA_PATH, 'client.json')) as f:
        return json.loads(f.read())


async def main(user_name, port):
    browser = await launch(ignorehttpserrrors=True, headless=False,
                           args=['--disable-infobars', '--no-sandbox'])
    page = await browser.newPage()
    try:
        page.on('dialog', lambda dialog: asyncio.ensure_future(close_dialog(dialog)))
        await page.goto('https://cfssr.xyz/auth/login', {'waitUntil': 'load'})
        await page.type('#email', user_name)
        await page.type('#passwd', 'hack3321')
        await page.click('#login')

        await page.waitForSelector('.user-info-main', {'visible': True})

        # print(await page.JJeval('.nodetype', '(elements => elements.map(e => e.innerText))'))

        user_level = await page.Jeval('.nodetype', 'el => el.innerText')
        user_level = str(user_level).strip()
        print(user_level)
        if user_level.find('普通') != -1:
            await page.goto('https://cfssr.xyz/user/shop', {'waitUntil': 'load'})
            shop_btn = await page.xpath('//a[@class="btn btn-brand-accent shop-btn"]')
            await shop_btn[1].click()
            await asyncio.sleep(1)
            await page.click('#coupon_input')
            await asyncio.sleep(1)
            await page.click('#order_input')
            await asyncio.sleep(3)
            await page.goto('https://cfssr.xyz/user', {'waitUntil': 'load'})
            user_level = await page.Jeval('.nodetype', 'el => el.innerText')
            user_level = str(user_level).strip()
            print(user_level)

        traffic = ','.join(await page.JJeval('.progressbar', '(elements => elements.map(e => e.innerText))'))
        print(traffic.replace('\n', ''))

        check_in = await page.querySelector('#checkin')
        if check_in:
            await page.click('#checkin')
            await asyncio.sleep(3)
            await page.click('#result_ok')

        subscribe_link = await page.Jeval('#all_v2ray_windows input', 'el => el.value')
        print(subscribe_link)

        print(generate(subscribe_link, user_name, port))

        await asyncio.sleep(200)
    except Exception as e:
        print(e)

    await page.close()
    await browser.close()


if __name__ == '__main__':
    tasks = [main(user_name, port) for user_name, port in ACCOUNT_LIST.items()]
    asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
