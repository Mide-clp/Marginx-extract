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


# from scrapingbee import ScrapingBeeClient
# import requests
#
#
# # Get free proxies for rotating
# def get_proxies():
#     url = "https://www.leboncoin.fr/voitures/offres"
#
#     client = ScrapingBeeClient(
#         api_key='4Q6XZRZFRG8ZI1Y3QSH6Z5JL86XM63CEWKVA18KOZC3F6D5MQFS4W0TNVIZQD6CVKK2DHIPOIFCYJG29')
#
#     response = client.get(url, params={'premium_proxy': 'True'})
#
#     return response.headers
#

# print(get_proxies())

    # requests.get("https://proxy.webshare.io/api/v2/profile/", headers={"Authorization": "Token <TOKEN>"})

    http_proxy = "http://brhsvlta-1:ktvgd9lm686i@45.155.68.129:80"
    https_proxy = "http://brhsvlta:ktvgd9lm686i@2.56.119.93:5074"
    url = "https://www.leboncoin.fr/voitures/offres"

    proxyDict = {
        "http": "http://brhsvlta-rotate:ktvgd9lm686i@p.webshare.io:80/",
        # "https": "http://brhsvlta-rotate:ktvgd9lm686i@p.webshare.io:80/"
    }

    print("here")
    r = requests.get(url, proxies=proxyDict, verify=False)
    print(r)
    print(r.headers)
    print(r.status_code)

