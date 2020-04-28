import asyncio

from pyppeteer import launch


async def main():
    browser = await launch(ignorehttpserrrors=True, headless=False, args=['--disable-infobars', '--no-sandbox'])
    page = await browser.newPage()
    await page.goto('https://drive.google.com/u/0', {'waitUntil': 'load'})
    page_url = page.url
    if page_url.find('accounts') == -1:
        link = await page.Jeval('.button-download', 'el => el.href')
        await page.goto(link, {'waitUntil': 'load'})

    await page.type('#identifierId', 'pod78@aaedu.edu.pl')
    await page.click('#identifierNext')

    await page.waitForSelector('input[type="password"]', {'visible': True})

    await page.type('input[type="password"]', 'hack3321')
    await page.click('#passwordNext')

    await asyncio.sleep(2)

    await page.goto('https://colab.research.google.com/drive/1YGfIYheilIKbevGnraJpwnszAkUOr_Na', {'waitUntil': 'load'})

    await page.waitForSelector('.cell-execution-indicator', {'visible': True})

    await page.click('.cell-execution-indicator')

    await page.waitForSelector('.outputview iframe', {'visible': True})

    q = await page.xpath('//div[@class="outputview"]/iframe')
    f = q[0].contentFrame()
    print(f.content())
    # nodeInfo = await q._client.send('DOM.describeNode', {
    #     'objectId': q._remoteObject.get('objectId'),
    # })
    # node_obj = nodeInfo.get('node', {})

    # print(frame.title)
    print('')
    for f in page.frames:
        print(await f.content())

    # link = await page.Jeval('#output-footer a', 'el => el.href')
    # await page.type('#output-footer .raw_input', 'hack3321')

    await asyncio.sleep(200)

    await page.close()
    await browser.close()


asyncio.get_event_loop().run_until_complete(main())
