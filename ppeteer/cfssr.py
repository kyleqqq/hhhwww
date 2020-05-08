import asyncio
import base64
import codecs
import json
import os
import platform
import random
import time
from os.path import dirname, realpath

import pyquery
import requests
from pyppeteer import launch
from requests.cookies import cookiejar_from_dict

BIN_URL = 'https://ioflood.com/100mbtest.bin'
USER_URL = 'https://cfssr.xyz/user'
ROOT_PATH = dirname(dirname(realpath(__file__)))
DATA_PATH = os.path.join(ROOT_PATH, 'data')
ACCOUNT_LIST = {'haha@dmeo666.cn': 1081}
sess = requests.session()


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


def download(port):
    _PROXIES = {
        'http': 'socks5://127.0.0.1:%s' % port,
        'https': 'socks5://127.0.0.1:%s' % port,
    }
    n = 0
    t = (random.randint(2048, 8192)) * 10000
    with requests.get(BIN_URL, stream=True, proxies=_PROXIES, timeout=10) as res:
        for chunk in res.iter_content(1024):
            n += len(chunk)
            if n > t:
                break
    return n


def start_v2ray(config_file, port):
    _cmd = 'nohup /usr/bin/v2ray/v2ray -config {} > /dev/null 2>&1 &'.format(config_file)
    os.popen(_cmd)
    time.sleep(2)

    print(download(port))

    cmd = "kill -9 $(ps -ef |grep '%s' |grep -v grep | awk '{print $2}')" % config_file
    os.system(cmd)


def user_info(username):
    html = sess.get(USER_URL).text
    doc = pyquery.PyQuery(html)
    elements = doc('.la-top')
    element_user = doc('.user-info-main').eq(0)
    element_user_money = doc('.user-info-main').eq(1)

    data = [username, element_user('.nodetype dd').text(), element_user_money('.nodetype').text()]
    for element in elements.items():
        name = element('.traffic-info').text().strip()
        val = element('.card-tag').text().strip()
        data.append('%s:%s' % (name, val))

    user_level = doc('#days-level-expire').parents('.dl-horizontal')
    a = user_level('dt').eq(0).text().strip()
    b = user_level('dd').eq(0).text().strip().replace('event', '').strip()

    data.append(a)
    data.append(b)
    return data


def main(user_name, port):
    cookie_file = os.path.join(DATA_PATH, '{}.cookie'.format(user_name))
    if os.path.exists(cookie_file):
        with codecs.open(cookie_file, 'r', 'utf-8') as f:
            cookies = f.read()
        sess.cookies = cookiejar_from_dict(json.loads(cookies))
        print(user_info(user_name))
        exit()

    config_file = os.path.join(DATA_PATH, '{}.json'.format(user_name))
    now_date = to_date(time.time())
    if os.path.exists(config_file):
        t = os.path.getctime(config_file)
        if to_date(t) == now_date:
            start_v2ray(config_file, port)
            return

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(get_link(user_name))
    # future.add_done_callback(callback)
    loop.run_until_complete(future)
    subscribe_link = future.result()
    loop.close()
    generate(subscribe_link, port, config_file)
    start_v2ray(config_file, port)


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
        print('{}: {}'.format(user_name, user_level))
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
            print('{}: {}'.format(user_name, user_level))

        traffic = ','.join(await page.JJeval('.progressbar', '(elements => elements.map(e => e.innerText))'))
        print('{}: {}'.format(user_name, traffic.replace('\n', '')))

        check_in = await page.querySelector('#checkin')
        if check_in:
            await page.click('#checkin')
            await asyncio.sleep(3)
            await page.click('#result_ok')

        cookies = await page.cookies()
        new_cookies = {}
        for cookie in cookies:
            new_cookies[cookie['name']] = cookie['value']

        with codecs.open(os.path.join(DATA_PATH, '{}.cookie'.format(user_name)), 'w', 'utf-8') as f:
            f.write(json.dumps(new_cookies))

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
