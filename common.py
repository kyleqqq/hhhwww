import asyncio

from pyppeteer import launch


async def close_dialog(dialog):
    await dialog.dismiss()


async def accept_dialog(dialog):
    await dialog.accept()


async def get_browser(url):
    browser = await launch(ignorehttpserrrors=True, headless=True,
                           args=['--disable-infobars', '--no-sandbox', '--start-maximized'])
    page = await browser.newPage()
    page.on('dialog', lambda dialog: asyncio.ensure_future(close_dialog(dialog)))

    await page.setViewport({'width': 1200, 'height': 768})
    await page.goto(url, {'waitUntil': 'load'})
    return page, browser


def patch_pyppeteer():
    import pyppeteer.connection
    original_method = pyppeteer.connection.websockets.client.connect

    def new_method(*args, **kwargs):
        kwargs['ping_interval'] = None
        kwargs['ping_timeout'] = None
        return original_method(*args, **kwargs)

    pyppeteer.connection.websockets.client.connect = new_method
