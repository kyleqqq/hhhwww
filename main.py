import argparse
import asyncio
import logging
from importlib import import_module

from pyppeteer import launch


async def _run(m, **kwargs):
    browser = await launch(ignorehttpserrrors=True, headless=True,
                           args=['--disable-infobars', '--no-sandbox', '--start-maximized'])
    page = await browser.newPage()
    try:
        await page.setViewport({'width': 1200, 'height': 768})
        await page.goto('https://www.textnow.com/login', {'waitUntil': 'load'})

        await page.waitForSelector('#txt-username', {'visible': True})

        await page.evaluate(
            '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')

        await m.run(page, kwargs.get('username'), kwargs.get('password'))
    except Exception as e:
        print(e)
    finally:
        await page.close()
        await browser.close()


def script_main(params):
    client = params.get('client')
    m = import_module('.'.join(['clients', client]))
    asyncio.get_event_loop().run_until_complete(_run(m, **params))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--client', required=True)
    parser.add_argument('-u', '--username')
    parser.add_argument('-p', '--password')
    parser.add_argument('--cookie')
    args = parser.parse_args()
    return script_main(vars(args))


if __name__ == '__main__':
    main()
