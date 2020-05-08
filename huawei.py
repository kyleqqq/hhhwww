import asyncio

from pyppeteer import launch


async def main():
    browser = await launch(ignorehttpserrrors=True,
                           args=['--disable-infobars', '--no-sandbox'])
    page = await browser.newPage()
    await page.goto('https://devcloud.huaweicloud.com/bonususer/home', {'waitUntil': 'load'})

    await page.waitForSelector('#personalAccountInputId .tiny-input-text', {'visible': True})

    await page.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
    await page.type('#personalAccountInputId .tiny-input-text', 'caoyufei')
    await page.type('#personalPasswordInputId .tiny-input-text', 'hack3321')
    await page.click('#btn_submit')
    await asyncio.sleep(3)

    page_url = page.url
    print(page_url)
    if page_url.find('mobile') != -1:
        await page.waitForSelector('.mobile-loading-btn-body', {'visible': True})
        print(await page.Jeval('.count', 'el => el.textContent'))
        await page.click('.mobile-loading-btn-body')
        await asyncio.sleep(3)
        print(await page.Jeval('.count', 'el => el.textContent'))
    else:
        await page.waitForSelector('#homeheader-signin', {'visible': True})
        print(await page.Jeval('#homeheader-coins', 'el => el.textContent'))
        await page.click('#homeheader-signin')
        await asyncio.sleep(3)
        print(await page.Jeval('#homeheader-coins', 'el => el.textContent'))

    await page.close()
    await browser.close()


asyncio.get_event_loop().run_until_complete(main())
