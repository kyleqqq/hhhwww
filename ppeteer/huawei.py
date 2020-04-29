import asyncio

from pyppeteer import launch


async def main():
    browser = await launch(ignorehttpserrrors=True, args=['--disable-infobars', '--no-sandbox'])
    page = await browser.newPage()
    await page.goto('https://devcloud.huaweicloud.com/bonususer/home', {'waitUntil': 'load'})

    await page.waitForSelector('#personalAccountInputId .tiny-input-text', {'visible': True})

    await page.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
    await page.type('#personalAccountInputId .tiny-input-text', 'caoyufei')
    await page.type('#personalPasswordInputId .tiny-input-text', 'hack3321')
    await page.click('#btn_submit')

    await asyncio.sleep(5)

    print(page.url)

    html = await page.content()
    if html.find('homeheader-signin') != -1:
        await page.click('#homeheader-signin')

        await asyncio.sleep(5)

        title_elements = await page.xpath('//div[@id="homeheader-coins"]')
        txt = await (await title_elements[0].getProperty('textContent')).jsonValue()
        print(txt)
    elif html.find('mobile-loading-btn-body') != -1:
        await page.click('.mobile-loading-btn-body')

        await asyncio.sleep(5)

        title_elements = await page.xpath('//div[@class="count"]')
        txt = await (await title_elements[0].getProperty('textContent')).jsonValue()
        print(txt)

    await page.close()
    await browser.close()


asyncio.get_event_loop().run_until_complete(main())
