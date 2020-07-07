import argparse
import asyncio
import time

from pyppeteer import launch


async def main(username, password):
    browser = await launch(ignorehttpserrrors=True, headless=True,
                           args=['--disable-infobars', '--no-sandbox', '--start-maximized'])
    page = await browser.newPage()
    try:
        await page.setViewport({'width': 1200, 'height': 768})
        await page.goto('https://www.textnow.com/login', {'waitUntil': 'load'})

        await page.waitForSelector('#txt-username', {'visible': True})

        await page.evaluate(
            '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
        await page.type('#txt-username', username)
        await asyncio.sleep(1)
        await page.type('#txt-password', password)
        await asyncio.sleep(1)
        await page.click('#btn-login')
        await asyncio.sleep(5)

        page_url = page.url
        print(page_url)
        await asyncio.sleep(15)

        try:
            await page.waitForSelector('.toast-container', {'visible': True})
            await page.click('img.js-dismissButton')
        except Exception as e:
            print(e)

        await page.waitForSelector('#newText', {'visible': True})
        await page.click('#newText')
        await asyncio.sleep(1)

        await page.type('.newConversationTextField ', '3205001183')
        await asyncio.sleep(1)
        await page.click('#text-input')
        await page.type('#text-input', time.strftime('%Y-%m-%d %H:%M:%S'))
        await asyncio.sleep(1)
        await page.click('#send_button')
    except Exception as e:
        print(e)
    finally:
        await page.close()
        await browser.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--username')
    parser.add_argument('--password')
    args = parser.parse_args()
    params = vars(args)

    asyncio.get_event_loop().run_until_complete(main(params.get('username'), params.get('password')))
