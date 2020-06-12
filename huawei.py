import asyncio

from pyppeteer import launch


async def main():
    browser = await launch(ignorehttpserrrors=True, headless=False,
                           args=['--disable-infobars', '--no-sandbox', '--start-maximized'])
    page = await browser.newPage()
    await page.setViewport({'width': 1200, 'height': 768})
    await page.goto('https://devcloud.huaweicloud.com/bonususer/home', {'waitUntil': 'load'})

    await page.waitForSelector('#personalAccountInputId .tiny-input-text', {'visible': True})

    await page.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
    await page.type('#personalAccountInputId .tiny-input-text', 'caoyufei')
    await page.type('#personalPasswordInputId .tiny-input-text', 'hack3321')
    await page.click('#btn_submit')
    await asyncio.sleep(5)

    try:
        nav = (await page.xpath('//ul[@class="devui-nav devui-nav-options"]'))[0]
        elements = await nav.querySelectorAll('li')
        for element in elements:
            await element.click()

            feedback_item_list = await page.xpath('//div[starts-with(@id, "experience-missions")]')
            for item in feedback_item_list:
                complate_img = await item.querySelector('.complate-img')
                if complate_img:
                    continue

                await item.click()
                await asyncio.sleep(2)
                await page.click('.devui-btn.devui-btn-stress.devui-btn-md')

                await asyncio.sleep(5)
                pages = (await browser.pages())
                print(pages[-1].url)
                # for i, p in enumerate(pages):
                #     print(i, p.url)
                # print(page2.url)
                # await page2.click('.devui-btn.devui-btn-primary.devui-btn-md')

            break
    except Exception:
        pass

    # print(await (await nav.getProperty('textContent')).jsonValue())

    # page_url = page.url
    # print(page_url)
    # if page_url.find('mobile') != -1:
    #     await page.waitForSelector('.mobile-loading-btn-body', {'visible': True})
    #     print(await page.Jeval('.count', 'el => el.textContent'))
    #     await page.click('.mobile-loading-btn-body')
    #     await asyncio.sleep(3)
    #     print(await page.Jeval('.count', 'el => el.textContent'))
    # else:
    #     await page.waitForSelector('#homeheader-signin', {'visible': True})
    #     print(await page.Jeval('#homeheader-coins', 'el => el.textContent'))
    #     await page.click('#homeheader-signin')
    #     await asyncio.sleep(3)
    #     print(await page.Jeval('#homeheader-coins', 'el => el.textContent'))

    await asyncio.sleep(50)
    await page.close()
    await browser.close()


asyncio.get_event_loop().run_until_complete(main())
