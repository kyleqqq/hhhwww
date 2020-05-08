import asyncio
import base64
import codecs
import json
import os
import platform
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


def generate(subscribe_link, port, config_file):
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
    node = random.choice(nodes)
    config = get_default_config()
    config['inbounds'][0]['port'] = port
    config['outbounds'][0]['settings']['vnext'][0]['address'] = node['add']
    config['outbounds'][0]['settings']['vnext'][0]['port'] = node['port']
    config['outbounds'][0]['settings']['vnext'][0]['users'][0]['id'] = node['id']
    with codecs.open(config_file, 'w', 'utf-8') as f:
        f.write(json.dumps(config))


def get_default_config():
    with codecs.open(os.path.join(DATA_PATH, 'client.json')) as f:
        return json.loads(f.read())


async def start_v2ray(config_file):
    _bin = '/usr/bin/v2ray/v2ray -config {}'.format(config_file)
    print(_bin)


def main(user_name, port):
    config_file = os.path.join(DATA_PATH, '{}.json'.format(user_name))
    now_date = to_date(time.time())
    if os.path.exists(config_file):
        t = os.path.getctime(config_file)
        if to_date(t) == now_date:
            start_v2ray(config_file)
            return

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(get_link(user_name))
    # future.add_done_callback(callback)
    loop.run_until_complete(future)
    subscribe_link = future.result()
    generate(subscribe_link, port, config_file)
    start_v2ray(config_file)


async def get_link(user_name):
    subscribe_link = ''
    headless = False if platform.system() == 'Windows' else True
    browser = await launch(ignorehttpserrrors=True, headless=headless,
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

        with codecs.open(os.path.join(DATA_PATH, '{}.cookie'.format(user_name)), 'w', 'utf-8') as f:
            f.write(json.dumps(await page.cookies()))

        subscribe_link = await page.Jeval('#all_v2ray_windows input', 'el => el.value')
    except Exception as e:
        print(e)

    await page.close()
    await browser.close()

    return subscribe_link


def test():
    generate('https://rss.cnrss.xyz/link/mQq0c3R9qfD7n16F?mu=2', 'haha@dmeo666.cn', 1081)


if __name__ == '__main__':
    # test()
    for _user_name, _port in ACCOUNT_LIST.items():
        main(_user_name, _port)
    # tasks = [main(user_name, port) for user_name, port in ACCOUNT_LIST.items()]
    # asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
