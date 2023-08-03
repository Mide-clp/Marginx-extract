import json
import os
import time
import chromedriver_autoinstaller
import pandas as pd
import logging
# from concurrent.futures import ThreadPoolExecutor
import selenium.common.exceptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from iteration_utilities import unique_everseen
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import pickle
import random


# selenium_logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
# selenium_logger.setLevel(logging.DEBUG)
# logging.basicConfig(level=logging.DEBUG)
class DataGet:
    BASE_URL = "https://www.leboncoin.fr/voitures/offres"
    FORMATTED_URL = "https://www.leboncoin.fr/voitures/offres/p-{}"

    def __init__(self):
        user_agents = "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) " \
                      "Chrome/115.0.0.0 Safari/537.36"

        chromedriver_autoinstaller.install()
        options = Options()
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option(
            'excludeSwitches', [
                'disable-extensions',
                'disable-default-apps',
                'disable-component-extensions-with-background-pages',
            ])

        options.add_argument('user-agent={0}'.format(user_agents))
        # options.add_argument('--proxy-server=45.141.123.237')
        options.add_argument("—-no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_argument("--headless=new")
        # options.add_argument("start-maximized")

        # self.driver = uc.Chrome(headless=False, use_subprocess=False, options=options)
        # Execute the JavaScript code on the browser
        self.driver = webdriver.Chrome(options=options)
        script_navigator = "Object.defineProperty(navigator, 'webdriver', {get: () => false})"
        script_permission = "Object.defineProperty(Notification, 'permission', {get: () => 'default'})"
        self.driver.execute_script(script_navigator)
        self.driver.execute_script(script_permission)


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
            json_unique = pd.DataFrame(file_data).astype("str").drop_duplicates(subset=["owner"]).to_dict('records')

            with open(file_name, "w", encoding="utf-8") as file:
                for new_data in json_unique:
                    file.write(json.dumps(new_data, ensure_ascii=False) + "\n")

        except (FileNotFoundError, json.decoder.JSONDecodeError):
            with open(file_name, "w", encoding="utf-8") as file:
                file.write(json.dumps(data, ensure_ascii=False) + "\n")

    def get_page_listing(self, page: str, wait_time: int = 4):
        """ get url of each listing on a page """
        page_num = page.split("/")[-1]
        self.driver.get("https://www.google.com/search?q=hello")
        time.sleep(2)
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

    def _get_description(self, soup: BeautifulSoup, wait_time: int = 5):
        self.driver.execute_script("window.scrollTo(0, 900)")
        time.sleep(wait_time)
        try:
            self.driver.find_element(
                By.CSS_SELECTOR,
                ".src__DescriptionWrapper-sc-65yq3k-0.kiwPmI"
            ).click()

            description_list = soup.find(name="p", class_="src__DescriptionWrapper-sc-65yq3k-0 kiwPmI").text

        except (selenium.common.exceptions.ElementNotInteractableException,
                selenium.common.exceptions.NoSuchElementException):
            description_list = soup.find(name="p", class_="src__DescriptionWrapper-sc-65yq3k-0 bCuRQe").text

        return description_list

    def get_single_listing(self, url: str, wait_time: int = 5):
        parsed_url = "https://www.leboncoin.fr{}".format(url)
        print(parsed_url)
        logging.info(f"Extracting data from {parsed_url}")
        self.driver.get("https://www.google.com/search?q=hello")
        time.sleep(2)
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
                owner = soup.find(name="h2", class_="_3T4fR _3gP8T _35DXM _25LNb _3eNLO").text

        num_rating = soup.find(name="span", class_="Roh2X _137P- _35DXM P4PEa")

        time.sleep(wait_time)
        self._get_description(soup)

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
    for listing_pages in data_provider.generate_listing_urls():
        listings = data_provider.get_page_listing(page=listing_pages, wait_time=4)
        for listing_url in listings:
            listing_data = data_provider.get_single_listing(listing_url, wait_time=3)
            if listing_data is not None and type(listing_data) != str:
                print(listing_data)
                data_provider.save(listing_data, "car_listing_data.json")

            elif type(listing_data) == str:
                print(listing_data)
                continue

    data_provider.driver.close()
