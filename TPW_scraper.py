import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

url = 'https://www.theproteinworks.com/products'
driver = webdriver.Chrome()
driver.get(url)

class TPW:

    def __init__(self, driver):
        self.driver = driver
        
    def load_and_accept_cookies(self):
        sleep(2)
        try:
            accept_cookies_button = self.driver.find_element(by=By.XPATH, value ='//*[@id="cookieConsent"]/div/div[3]/button')
            accept_cookies_button.click()
            sleep(1)
        except:
            pass

    def pop_up(self):
        sleep(1)
        try:
            pop_up = self.driver.find_element(by=By.XPATH, value ='/html/body/div[5]/div/div')
            pop_up_button = pop_up.find_element(by=By.XPATH, value= '/div[1]/button')
            pop_up_button.click()
        except:
            pass

    def scroll(self):
        sleep(1)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def close_driver(self):
        sleep(1)
        self.driver.close()

    def click_next_page(self):
        sleep(1)
        next_page = self.driver.find_element(by=By.XPATH, value='//*[@id="__next"]/div/div[3]/div/div[2]/div[2]/div/section[2]/div/div[2]/div[3]/div/ul/li[10]')
        next_page.click()
    
    def get_pages(self):
        sleep(1)
        page_url_list = []
        for i in range(0,7):
            page_url = url + f'/page/{i}' 
            page_url_list.append(page_url)
        print(page_url_list)

    def get_prod_info(self):
            pass


def run_scraper():
    scraper = TPW(driver)
    scraper.load_and_accept_cookies()
    scraper.pop_up()
    scraper.scroll()
    scraper.click_next_page()
    scraper.close_driver()
    scraper.get_pages()


if __name__ == '__main__':
    print('this is running directly')
    run_scraper()

