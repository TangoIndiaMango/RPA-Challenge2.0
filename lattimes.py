import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from selenium.common.exceptions import NoSuchElementException

from utils import Utils


class Scrapper:
    def __init__(self, *args, **kwargs):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(5)
        self.wait = WebDriverWait(self.driver, 10)
        
    def open_browser(self, url):
        try:
            self.driver.get(url)
            self.driver.maximize_window()
        except Exception as e:
            print(f"Unable to open the browser and navigate to the URL: {e}")
            
    def close_browser(self):
        self.driver.close()
        
    
    def search_lattimes(self, search_term):
        try:
            search_box = self.driver.find_element(By.XPATH, "//button[@data-element='search-button']")
            search_box.click()
            time.sleep(5)
            search_input = self.driver.find_element(By.XPATH, "//input[@data-element='search-form-input']")
            search_input.send_keys(search_term)
            search_input.send_keys(Keys.ENTER)
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//main[@class='search-results-module-main']")))
            
        except Exception as e:
            print(f"Unable to search for search phrase: {e}")
            logging.error(f"Unable to search for search phrase: {e}")
            
    def set_news_category(self, category):
        try:
            see_all_locator = "//button[@class='button see-all-button']"
            category_locator = f"//div[@class='checkbox-input']/label[.//span[text()='{category}']]/input[@type='checkbox']"

            see_all_button = self.driver.find_element(By.XPATH, see_all_locator)
            category_button = self.driver.find_element(By.XPATH, category_locator)

            see_all_button.click()
            time.sleep(5)
            category_button.click()
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//main[@class='search-results-module-main']")))
            time.sleep(5)
        except NoSuchElementException as e:
            logging.info(f"No {category} found: {e}")
        except Exception as e:
            print(f"Unable to set news category: {e}")
            logging.error(f"Unable to set news category: {e}")

    def sort_news(self):
        try:
            sort_select = self.driver.find_element(By.XPATH, "//select[@class='select-input']")
            sort_select.send_keys("newest")
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//main[@class='search-results-module-main']")))
            logging.info("News sorted by newest")
            time.sleep(5)
        except Exception as e:
            print(f"Error sorting news by newest: {e}")
            
    def get_news_data(self, search_phrase, folder_to_save_images, max_items=None):
        news_data = []
        try:
            while True:
                news_items = self.driver.find_elements(By.XPATH, "//ul[@class='search-results-module-results-menu']" "/li")
                for item in news_items:
                    try:
                        title_locator = ".//h3[@class='promo-title']"
                        description_locator = ".//p[@class='promo-description']"
                        date_locator = ".//p[@class='promo-timestamp']"
                        image_locator = ".//div[@class='promo-media']//img"
                        
                        news_title = item.find_element(By.XPATH, title_locator).text
                        news_description = item.find_element(By.XPATH, description_locator).text
                        news_date = item.find_element(By.XPATH, date_locator).text
                        news_image_element = item.find_element(By.XPATH, image_locator)
                        news_image_src = news_image_element.get_attribute("src")
                        image_filename = Utils.get_image_name(news_image_src)
                        # sanitize the image name
                        image_filename = os.path.basename(image_filename)
                        if image_filename:
                            Utils.download_image(news_image_src, image_filename, folder_to_save_images)
                            
                        searchword_count = Utils.count_occurrence(news_title, news_description, search_phrase)
                        contains_money = Utils.check_contains_money(news_title, news_description)
                        
                        news_data.append([news_date, news_title, news_description, image_filename, searchword_count, contains_money])
                        
                        if max_items is not None and len(news_data) >= max_items:
                            return news_data
                        
                    except Exception as e:
                        print(f"Error getting news data: {e}")
                        logging.error(f"Error getting news data: {e}")
                next_url_more = self.driver.find_element(By.XPATH, "//div[@class='search-results-module-next-page']//a")
                if next_url_more:
                    next_url_more.click()
                    self.wait.until(EC.presence_of_element_located((By.XPATH, "//main[@class='search-results-module-main']")))
                    time.sleep(5)
                else:
                    break
        except Exception as e:
            print(f"Error getting news: {e}")
            logging.error(f"Error getting news: {e}")
        
        return news_data
    