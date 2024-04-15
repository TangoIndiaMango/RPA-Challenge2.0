import logging
from RPA.Browser.Selenium import Selenium
import time
import os
from selenium.common.exceptions import NoSuchElementException

from utils import Helpers


class Scrapper:
    def __init__(self):
        self.driver = Selenium()
        self.driver.set_selenium_timeout(15)
        
    def open_browser(self, url):
        try:
            self.driver.open_available_browser(url)
            self.driver.maximize_browser_window()
        except Exception as e:
            print(f"Unable to open the browser and navigate to the URL: {e}")
            
    def close_browser(self):
        self.driver.close_browser()
        
    
    def search_lattimes(self, search_term):
        try:
            search_box = "//button[@data-element='search-button']"
            if self.driver.is_element_visible(search_box):
                self.driver.click_element(locator=search_box)
            time.sleep(5)
            search_input = "//input[@data-element='search-form-input']"
            self.driver.input_text(search_input, text=search_term)
            self.driver.press_keys(search_input, "ENTER")
            body = "//div[@class='page-content']/h1[@class='page-title']"
            self.driver.wait_until_element_contains(locator=body, text="Search results for")
            logging.info("Search phrase entered and results displayed")
        except Exception as e:
            print(f"Unable to search for search phrase: {e}")
            logging.error(f"Unable to search for search phrase: {e}")
            
    def set_news_category(self, category):
        try:
            see_all_locator = "//button[@class='button see-all-button']/span[@class='see-all-text']"
            category_locator = f"//div[@class='checkbox-input']/label[.//span[text()='{category}']]/input[@type='checkbox']"

            see_all_button = self.driver.get_webelement(locator=see_all_locator)
            self.driver.click_element(locator=see_all_button)
            time.sleep(5)
            category_button = self.driver.get_webelement(locator=category_locator)
            self.driver.click_element(locator=category_button)
            body = "//div[@class='page-content']/h1[@class='page-title']"
            self.driver.wait_until_element_contains(locator=body, text="Search results for")
            time.sleep(5)
            logging.info(f"News category set to {category}")
        except NoSuchElementException as e:
            logging.info(f"No {category} found: {e}")
        except Exception as e:
            print(f"Unable to set news category: {e}")
            logging.error(f"Unable to set news category: {e}")

    def sort_news(self):
        try:
            sort_select = "//select[@class='select-input']"
            self.driver.get_webelement(sort_select)
            self.driver.press_keys(sort_select, "Newest")
            body = "//div[@class='page-content']/h1[@class='page-title']"
            self.driver.wait_until_element_contains(locator=body, text="Search results for")
            time.sleep(5)
            logging.info("News sorted by newest")
        except Exception as e:
            print(f"Error sorting news by newest: {e}")
            
    def get_web_element_text(self, locator: str) -> str:
        if self.driver.does_page_contain_element(locator=locator):
            web_element = self.driver.get_webelement(locator=locator)
            return web_element.text
        else:
            return ""
            
    def get_news_data(self, search_phrase, folder_to_save_images, max_items=None):
        news_data = []
        try:
            while True:
                news_items = len(self.driver.get_webelements(locator="//ul[@class='search-results-module-results-menu']" "/li"))
                for item in range(news_items):
                    try:
                        title_locator = f"//ul[@class='search-results-module-results-menu']" "/li" \
                            f"[{item + 1}]//h3[@class='promo-title']"
                        description_locator = f"//ul[@class='search-results-module-results-menu']" "/li" \
                            f"[{item + 1}]//p[@class='promo-description']"
                        date_locator = f"//ul[@class='search-results-module-results-menu']" "/li" \
                            f"[{item + 1}]//p[@class='promo-timestamp']"
                        image_locator = f"//ul[@class='search-results-module-results-menu']" "/li" \
                            f"[{item + 1}]//div[@class='promo-media']//img[@class='image']"
                        
                        news_title = self.get_web_element_text(title_locator)
                        news_description = self.get_web_element_text(description_locator)
                        news_date = self.get_web_element_text(date_locator)
                        
                        if self.driver.does_page_contain_element(locator=image_locator):
                            image = self.driver.get_webelement(locator=f"//ul[@class='search-results-module-results-menu']" "/li" \
                            f"[{item + 1}]//div[@class='promo-media']//img[@class='image']")
                            news_image_src = self.driver.get_element_attribute(image, "src")
                            logging.info("NAME OF SRC", news_image_src)
                            image_filename = None
                            image_filename = Helpers.get_image_name(news_image_src)
                            logging.info("NAME OF IMAGE", image_filename)
                            # sanitize the image name
                            image_filename = os.path.basename(image_filename)
                            logging.info("NAME OF IMAGE AFTER BASEPATH", image_filename)
                            if image_filename:
                                Helpers.download_image(news_image_src, image_filename, folder_to_save_images)
                            
                        searchword_count = Helpers.count_occurrence(news_title, news_description, search_phrase)
                        contains_money = Helpers.check_contains_money(news_title, news_description)
                        
                        news_data.append([news_date, news_title, news_description, image_filename, searchword_count, contains_money])
                        
                        if max_items is not None and len(news_data) >= max_items:
                            return news_data
                        
                    except Exception as e:
                        print(f"Error getting news data: {e}")
                        logging.error(f"Error getting news data: {e}")
                next_url_more = "//div[@class='search-results-module-next-page']/a"
                if self.driver.does_page_contain_element(locator=next_url_more):
                    self.driver.click_element_when_visible(locator=next_url_more)
                    body = "//div[@class='page-content']/h1[@class='page-title']"
                    self.driver.wait_until_element_contains(locator=body, text="Search results for")
                    time.sleep(5)
                    logging.info("Next page displayed")
                else:
                    break
        except Exception as e:
            print(f"Error getting news: {e}")
            logging.error(f"Error getting news: {e}")
        
        return news_data
    