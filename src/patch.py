import requests, json, re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller  # pip install chromedriver-autoinstaller


# Get free proxies for rotating
def get_proxies():
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.get('https://sslproxies.org')

    table = driver.find_element(By.TAG_NAME, 'table')
    thead = table.find_element(By.TAG_NAME, 'thead').find_elements(By.TAG_NAME, 'th')
    tbody = table.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')

    header = []
    for th in thead:
        header.append(th.text.strip())

    proxies = []
    for tr in tbody:
        proxy_data = {}
        tds = tr.find_elements(By.TAG_NAME, 'td')
        for i in range(len(header)):
            proxy_data[header[i]] = tds[i].text.strip()
        proxies.append(proxy_data)

    driver.quit()
    return proxies


if __name__ == "__main__":
    pass


