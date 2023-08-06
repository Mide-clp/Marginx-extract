import json
import time
import chromedriver_autoinstaller
import pandas as pd
import logging
import selenium.common.exceptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from seleniumwire import webdriver
from patch import get_proxies
import requests


# selenium_logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
# selenium_logger.setLevel(logging.DEBUG)
# logging.basicConfig(level=logging.INFO)

def include_proxy(use_proxy: bool = False):
    if use_proxy:
        headers = {"authority": "www.leboncoin.fr", "scheme": "https",
                   "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                   "accept-language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7", "sec-fetch-dest": "document",
                   "sec-fetch-mode": "navigate", "sec-fetch-site": "none", "sec-fetch-user": "?1",
                   "upgrade-insecure-requests": "1",
                   "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.170 Safari/537.36"}
        url = "https://www.leboncoin.fr/voitures/offres"

        proxies = get_proxies()

        for proxy in proxies[:20]:
            proxy_conn = proxy["IP Address"] + ":" + proxy["Port"]
            print(proxy_conn)

            proxy_param = {
                "http": f"http://{proxy_conn}",
                # "https": f"https://{proxy_conn}"
            }

            r = requests.get(url, headers=headers, proxies=proxy_param, verify=False)

            if r.status_code == 200:
                print(f"This is a good proxy: {proxy_conn}")
                options = {
                    'proxy': {
                        'http': f'http://{proxy_conn}',
                        'https': f'https://{proxy_conn}',
                    }
                }

                return options


def interceptor(request):
    del request.headers['Referer']
    del request.headers['Sec-Ch-Ua']
    del request.headers['Sec-Ch-Ua-Platform']
    del request.headers['User-Agent']
    del request.headers['cookie']
    request.headers['Referer'] = 'https://www.leboncoin.fr/voitures/offres'
    request.headers['Sec-Ch-Ua'] = '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"'
    request.headers['Sec-Ch-Ua-Platform'] = '"macOS"'
    request.headers[
        'User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) " \
                        "Chrome/115.0.5790.170 Safari/537.36"
    request.headers[
        'cookie'] = "datadome=61Ct4w96EHAZvfeia9IW_TN6Enh9ygB9VeB4jV9as0QcY~lRDvUhBLasvgRUZhBvcE7SxLgvk3qAmBmUQVzQGqRUYgS9bBShdK3jPefqKHuhmj5xICkZXBjbZcc0wbSH;"


class DataGet:
    BASE_URL = "https://www.leboncoin.fr/voitures/offres"
    FORMATTED_URL = "https://www.leboncoin.fr/voitures/offres/p-{}"

    def __init__(self):
        user_agents = "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) " \
                      "Chrome/115.0.0.0 Safari/537.36"

        chromedriver_autoinstaller.install()
        options = Options()
        # options = uc.ChromeOptions()

        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option(
            'excludeSwitches', [
                'disable-extensions',
                'disable-default-apps',
                'disable-component-extensions-with-background-pages',
            ])

        options_with_proxy = include_proxy(use_proxy=False)
        # selenium_wire_options = options_with_proxy if options_with_proxy is not None else {}
        selenium_wire_options = {
            'proxy': {
                'http': 'http://brhsvlta:ktvgd9lm686i@185.199.229.156:7492',
                'https': 'https://brhsvlta:ktvgd9lm686i@185.199.229.156:7492',
            }
        }

        options.add_argument("—-no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--headless=new")

        self.driver = webdriver.Chrome(options=options, seleniumwire_options=selenium_wire_options)
        self.driver.request_interceptor = interceptor

    @staticmethod
    def generate_listing_urls(max_pagination: int = 51) -> list:
        """generate url for each paginated page"""
        all_listing_url = []

        for x in range(1, max_pagination):
            url = DataGet.FORMATTED_URL.format(x)
            all_listing_url.append(url)

        return all_listing_url

    @staticmethod
    def save(data: dict, file_name: str) -> None:
        """save data to json file"""

        try:
            with open(file_name, "r") as file:
                file_data = [json.loads(line) for line in file]

            # remove duplicates using url as unique identifier
            file_data.append(data)
            json_unique = pd.DataFrame(file_data).astype("str").drop_duplicates(subset=["owner"]).to_dict("records")

            with open(file_name, "w", encoding="utf-8") as file:
                for new_data in json_unique:
                    file.write(json.dumps(new_data, ensure_ascii=False) + "\n")

        except (FileNotFoundError, json.decoder.JSONDecodeError):
            with open(file_name, "w", encoding="utf-8") as file:
                file.write(json.dumps(data, ensure_ascii=False) + "\n")

    def get_page_listing(self, page: str, wait_time: int = 2):
        """ get url of each listing on a page """

        print(f"extracting from page {page}")
        self.driver.get("https://www.google.com/search?q=hello")
        time.sleep(wait_time)
        self.driver.get(page)

        time.sleep(wait_time)

        self.driver.execute_script("window.scrollTo(0, 10000)")
        time.sleep(wait_time)

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        all_listing = soup.find_all(name="div", class_="styles_adCard__HQRFN styles_classified__rnsg4")

        listing_urls = []
        for listing in all_listing:
            listing_urls.append(listing.find(name="a", class_="sc-f097e434-0 kchccg", href=True)["href"])

        return listing_urls

    @staticmethod
    def _get_attributes(soup: BeautifulSoup):
        "get car criteria"
        criteria_attributes = soup.find(name="div", class_="sc-925f8dc0-0 FZzko")
        attributes = {}
        try:
            for attribute in criteria_attributes.find_all(name="div", class_="sc-925f8dc0-1 fRpuqr"):
                attribute_name = attribute.find(name="p", class_="_2k43C _1pHkp Dqdzf _3j0OU cJtdT").text
                attribute_value = attribute.find(name="span", class_="_137P- _35DXM P4PEa _38n__ _3eNLO").text
                attributes[attribute_name] = attribute_value
        except Exception:
            return None
        return attributes

    def wrap_command(self):
        pass

    def _get_description(self, soup: BeautifulSoup, wait_time: int = 2):
        self.driver.execute_script("window.scrollTo(0, 900)")
        time.sleep(wait_time)
        print()
        try:
            self.driver.find_element(
                By.CSS_SELECTOR,
                ".src__DescriptionWrapper-sc-65yq3k-0.kiwPmI"
            ).click()

            description_list = soup.find(name="p", class_="src__DescriptionWrapper-sc-65yq3k-0 kiwPmI").text

        except (selenium.common.exceptions.ElementNotInteractableException,
                selenium.common.exceptions.NoSuchElementException):

            try:
                description_list = soup.find(name="p", class_="src__DescriptionWrapper-sc-65yq3k-0 bCuRQe").text
            except (selenium.common.exceptions.NoSuchElementException,
                    AttributeError):
                self.driver.find_element(
                    By.CLASS_NAME,
                    "_27ngl Roh2X _2NG-q _29R_v HGqCc _3Q3XS Mb3fh _137P- _35DXM P4PEa wEezs"
                ).click()
                time.sleep(wait_time)
                description_list = soup.find(name="p", class_="src__DescriptionWrapper-sc-65yq3k-0 kiwPmI").text

        except selenium.common.exceptions.ElementClickInterceptedException:
            data_provider.driver.find_element(By.CSS_SELECTOR,
                                              ".didomi-components-button.didomi-button.didomi-dismiss-button"
                                              ".didomi-components-button--color.didomi-button-highlight"
                                              ".highlight-button").click()
            time.sleep(2)
            description_list = soup.find(name="p", class_="src__DescriptionWrapper-sc-65yq3k-0 kiwPmI").text
            # self.driver.execute_script("window.open('', '_blank');")
            # self.driver.switch_to.window(self.driver.window_handles[-1])
            # self.driver.close()

        return description_list

    def get_single_listing(self, url: str, wait_time: int = 2):
        self.driver.execute_script("window.open('', '_blank');")
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])
        parsed_url = "https://www.leboncoin.fr{}".format(url)
        print(parsed_url)
        logging.info(f"Extracting data from {parsed_url}")

        self.driver.get("https://www.google.com/search?q=hello")
        time.sleep(wait_time)
        self.driver.get(parsed_url)

        time.sleep(wait_time)
        self.driver.execute_script("window.scrollTo(0, 2000)")

        time.sleep(wait_time)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        title = soup.find(name="title")
        if title.text == "Annonce introuvable":
            return None
        elif title.text == "leboncoin.fr":
            return "Either your network is slow, or you facing a recaptcha, increase wait_time " \
                   "or remove headless browser to answer recaptcha "

        price = soup.find(name="div", class_="flex flex-wrap items-center mr-md")

        self._get_attributes(soup)

        # get owner url
        try:
            posted_by = soup.find(name="a", class_="_3gP8T _35DXM _25LNb _38n__")["href"]
        except (AttributeError, TypeError):

            try:
                posted_by = soup.find(name="div", class_="src__Box-sc-10d053g-0 hmRkLH").find("a")["href"]
            except AttributeError:
                posted_by = None

        # get owner name
        try:
            owner = soup.find(name="a", class_="_3gP8T _35DXM _25LNb _38n__").text
        except (AttributeError, TypeError):
            try:
                owner = soup.find(name="div", class_="src__Box-sc-10d053g-0 hmRkLH").find("a").text
            except AttributeError:
                try:
                    owner = soup.find(name="h2", class_="_3T4fR _3gP8T _35DXM _25LNb _3eNLO").text

                except AttributeError:
                    owner = soup.find(name="a",
                                      class_="_3k87M _3Hrjq _3Wx6b _2MFch _1hnil _35DXM _1-TTU _1GcfX _2DyF8 _3k00F").text

        num_rating = soup.find(name="span", class_="Roh2X _137P- _35DXM P4PEa")

        time.sleep(wait_time)

        listing_data = {
            "title": title.text,
            "url": url,
            "price": price.text if price is not None else "",
            "attributes": self._get_attributes(soup),
            "description": self._get_description(soup),
            "owner_profile": posted_by,
            "owner": owner,
            "number_of_rating": num_rating.text if num_rating is not None else ""
        }

        return listing_data


if __name__ == "__main__":
    data_provider = DataGet()
    # data = data_provider.get_single_listing("/offre/voitures/2376440762")
    # print(data)
    for listing_pages in data_provider.generate_listing_urls():

        listings = data_provider.get_page_listing(page=listing_pages, wait_time=2)

        for listing_url in listings:
            # print(listings)
            listing_data = data_provider.get_single_listing(listing_url, wait_time=2)

            if listing_data is not None and type(listing_data) != str:
                print(listing_data)
                data_provider.save(listing_data, "car_listing_data.json")

            elif type(listing_data) == str:
                print(listing_data)
                continue

    data_provider.driver.quit()
