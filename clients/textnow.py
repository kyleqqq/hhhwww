import asyncio
import time

from common import send_ding_task


async def run(page, username, password):
    print('start login.')
    await page.type('#txt-username', username)
    await asyncio.sleep(1)
    await page.type('#txt-password', password)
    await asyncio.sleep(1)
    await page.click('#btn-login')
    await asyncio.sleep(5)

    page_url = page.url
    if page_url != 'https://www.textnow.com/messaging':
        error_info = str(await page.Jeval('.uikit-text-field__message', 'el => el.textContent')).strip()
        print(f'{page_url}\n{error_info}')
        send_ding_task(f'TextNow:{username}-{password}\n{error_info}')
        return

    print('login success.')
    await asyncio.sleep(20)

    try:
        await page.waitForSelector('.toast-container', {'visible': True})
        await page.click('img.js-dismissButton')
    except Exception as e:
        print(e)

    await page.waitForSelector('#newText', {'visible': True})
    await page.click('#newText')
    await asyncio.sleep(1)

    sms_content = '{}: {}'.format(username, time.strftime('%Y-%m-%d %H:%M:%S'))
    await page.type('.newConversationTextField ', '3205001183')
    await asyncio.sleep(1)
    await page.click('#text-input')
    await page.type('#text-input', sms_content)
    await asyncio.sleep(1)
    await page.click('#send_button')
    await asyncio.sleep(2)
    print('send done.')
