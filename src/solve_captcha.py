from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC
import time as t
import base64
from PIL import Image
import chromedriver_autoinstaller
chromedriver_autoinstaller.install()
options = Options()
options.add_argument("--no-sandbox")
# options.add_argument('--disable-notifications')
# options.add_argument("--window-size=1280,720")

# options.add_argument('--headless')

browser = webdriver.Chrome(options=options)

wait = WebDriverWait(browser, 5)
url = 'https://www.leboncoin.fr/offre/voitures/2384763862'
browser.get(url)

t.sleep(4)

piece_img = browser.find_element(By.XPATH, '//*[@id="captcha__puzzle"]/canvas[1]')
piece_img.screenshot('piece.png')

captcha_img_background = browser.find_element(By.XPATH, '.canvas-mask')
captcha_img_background.screenshot('full_captcha_image.png')
print('got captcha!')
b64img_background = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div[1]/canvas[1]'))).get_attribute('style').split('url("data:image/png;base64,')[1].split('");')[0]
bgimgdata = base64.b64decode(b64img_background)
with open('bg_image.png', 'wb') as f:
    f.write(bgimgdata)
print('also saved the base64 image as bg_image.png')

