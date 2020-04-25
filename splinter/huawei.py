import os
import platform

from selenium.webdriver.chrome.options import Options
from splinter import Browser

IS_WIN = platform.system() == 'Windows'

executable_path = 'chromedriver'
if IS_WIN:
    executable_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'drive', 'chromedriver.exe')

chrome_options = Options()
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--log-level=3')
chrome_options.add_argument('--start-maximized')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')

browser = Browser('chrome', executable_path=executable_path,
                  options=chrome_options)
browser.visit(
    'https://auth.huaweicloud.com/authui/login.html?service=https%3A%2F%2Fdevcloudsso.huaweicloud.com%2Fauthticket%3Fservice%3Dhttps%253A%252F%252Fdevcloud.huaweicloud.com%252Fbonususer%252Fhome#/login')

browser.find_by_css('#personalAccountInputId .tiny-input-text').fill('caoyufei')
browser.find_by_css('#personalPasswordInputId .tiny-input-text').fill('hack3321')
browser.find_by_id('btn_submit').click()

browser.find_by_id('homeheader-signin').click()
browser.quit()
