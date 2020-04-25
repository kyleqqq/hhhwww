import asyncio

from pyppeteer import launch


# executablePath='C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
async def main():
    browser = await launch(ignorehttpserrrors=True, args=['--disable-infobars', '--no-sandbox'])
    page = await browser.newPage()
    await page.goto('https://devcloud.huaweicloud.com/bonususer/home')
    await asyncio.sleep(2)

    await page.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
    await page.type('#personalAccountInputId .tiny-input-text', 'caoyufei')
    await page.type('#personalPasswordInputId .tiny-input-text', 'hack3321')
    await page.click('#btn_submit')

    await asyncio.sleep(5)

    await page.click('#homeheader-signin')

    await asyncio.sleep(5)

    title_elements = await page.xpath('//div[@id="homeheader-coins"]')
    txt = await (await title_elements[0].getProperty('textContent')).jsonValue()
    print(txt)

    await page.close()
    await browser.close()


asyncio.get_event_loop().run_until_complete(main())
