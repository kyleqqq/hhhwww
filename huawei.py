import argparse
import asyncio
import time

from pyppeteer import launch


async def main(username, password):
    browser = await launch(ignorehttpserrrors=True, headless=True,
                           args=['--disable-infobars', '--no-sandbox', '--start-maximized'])
    page = await browser.newPage()
    print(time.strftime('%Y-%m-%d %H:%M:%S'))
    for i in range(3):
        try:
            await page.setViewport({'width': 1200, 'height': 768})
            await page.goto('https://devcloud.huaweicloud.com/bonususer/mobile/home', {'waitUntil': 'load'})

            await page.waitForSelector('#personalAccountInputId .tiny-input-text', {'visible': True})

            await page.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
            await page.type('#personalAccountInputId .tiny-input-text', username)
            await page.type('#personalPasswordInputId .tiny-input-text', password)
            await page.click('#btn_submit')
            await asyncio.sleep(5)

            page_url = page.url
            print(page_url)
            await page.waitForSelector('.mobile-loading-btn-body', {'visible': True})
            await asyncio.sleep(5)

            sign_txt = await page.Jeval('.mobile-loading-btn-body', 'el => el.textContent')
            credit = await page.Jeval('.count', 'el => el.textContent')
            print(sign_txt, credit)

            if sign_txt.find('今日已签到') == -1:
                await page.click('.mobile-loading-btn-body')
                await asyncio.sleep(5)
                new_credit = await page.Jeval('.count', 'el => el.textContent')
                print(new_credit)

            await asyncio.sleep(3)

            break
        except Exception as e:
            print(e)
            await page.close()

    await page.close()
    await browser.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--username')
    parser.add_argument('--password')
    args = parser.parse_args()
    params = vars(args)
    asyncio.get_event_loop().run_until_complete(main(params.get('username'), params.get('password')))
