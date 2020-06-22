import asyncio
import platform
import random

from pyppeteer import launch


async def main():
    headless = False if platform.system() == 'Windows' else True
    browser = await launch(ignorehttpserrrors=True, headless=False,
                           args=['--disable-infobars', '--no-sandbox'])
    page = await browser.newPage()

    _name = random.randint(1000, 9999)
    _mail = f'{_name}@demo666.cn'
    await page.goto('https://cloud.ibm.com/registration', {'waitUntil': 'load'})
    await page.type('#email-input', _mail)
    await page.type('#password-input', 'Hack3321')
    await page.click('.reg-accordion-item__submit-button')
    await asyncio.sleep(3)

    await page.close()
    await browser.close()


asyncio.get_event_loop().run_until_complete(main())
