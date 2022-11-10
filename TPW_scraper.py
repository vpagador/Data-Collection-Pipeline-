from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import datetime
import json
import os
import requests
import re
import uuid
import urllib.request

url = 'https://www.theproteinworks.com/products'
driver = webdriver.Chrome()
driver.get(url)

class TPW:

    def __init__(self, driver):
        self.driver = driver
        self.page_urls_list = ["https://www.theproteinworks.com/vegan-wondershake",
                                "https://www.theproteinworks.com/whey-protein-360-extreme"]

    def load_and_accept_cookies(self):
        sleep(2)
        try:
            accept_cookies_button = self.driver.find_element(by=By.XPATH, 
                                    value ='//*[@id="cookieConsent"]/div/div[3]/button')
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
        next_page = self.driver.find_element(by=By.XPATH, 
                                value='//*[@id="__next"]/div/div[3]/div/div[2]/div[2]')
        next_page = next_page.find_element(by=By.XPATH, 
                                value='/div/section[2]/div/div[2]/div[3]/div/ul/li[10]')
        next_page.click()
    
    def get_pages(self):
        sleep(1)
        for i in range(0,7):
            page_url = url + f'/page/{i}' 
            self.page_urls_list.append(page_url)
        print(self.page_urls_list)

    def get_data(self):

        product_list = []
        id_list = []
        
        for page_url in self.page_urls_list:
            response = requests.get(page_url)
            sleep(1)
            soup = BeautifulSoup(response.content, "html.parser")
            dom = etree.HTML(str(soup))
            id = uuid.uuid4().hex
            # Create dictionary for each product to contain id, time scraped, text data and image data
            product = {'unique id ':id, 'time' : str(datetime.datetime.now().strftime('%c')), 
                        'contents' : None}
            contents = {"Product Name": [],"Price": [],"Description Short":[],
                                "Sizes":[],"Flavours":[],"Description Long" :[], 
                                "Rating Percentage" : [],"Number of Reviews":[], "Images":[]}
            sleep(1)
            # Scrape each category of text data and add to dictionary
            product_name = soup.find('h1').text
            contents["Product Name"].append(product_name)
                    
            price = dom.xpath('//*[@id="__next"]/div/div[3]/div/section[1]/div/div')
            price = price.xpath('/div[2]/section/div/div[3]/form/div[3]/div[1]/div')
            price = price.xpath('/div[2]/div/span/span')[0].text
            contents["Price"].append(price)

            description_short = soup.find(id='product-description-short').text
            contents["Description Short"].append(description_short)

            sizes = soup.find(class_='ProductItem_size__3Ux92 size btn-group').text
            contents["Sizes"].append(sizes)

            flavours = soup.find(class_='form-select').text
            contents["Flavours"].append(flavours)

            description_long = soup.find(class_='RRT__panel panel').text
            contents["Description Long"].append(description_long)

            rating_percentage = soup.find(class_='ProductItem_rating__1WQSr').text
            contents["Rating Percentage"].append(rating_percentage)

            number_of_reviews = soup.find(class_='ProductItem_reviews__2xbGO').text
            number_of_reviews = re.sub(r'\W+','',number_of_reviews)
            contents["Number of Reviews"].append(number_of_reviews)

            # Obtain all available image src and add to dictionary
            images = soup.find_all('img')
            for image in images:
                contents["Images"].append(image['src'])

            # Add contents to the bigger product dictionary 
            product['contents'] = contents

            # Add each product dictionary to the product list
            # and id of each product to the id list 
            product_list.append(product)
            id_list.append(id)

        # call the create_json method
        return self.create_json(product_list, id_list)
        

    def create_json(self, product_list, id_list):
        # set project directory, make raw data directory and join them
        parent_dir = "/home/van28/Desktop/AiCore/Scraper_Project"
        raw_data_dir = "raw_data"
        raw_data_path = os.path.join(parent_dir, raw_data_dir)
        os.mkdir(raw_data_path)
        print(f"Directory {raw_data_dir} created")
        
        # loop through ids and results in lists of scraped data and ids.
        # create folders of each id name and dump json file of each product
        for id, product in zip(id_list, product_list):
            item_dir = id
            item_path = os.path.join(raw_data_path, item_dir)
            os.mkdir(item_path)
            print(item_path)
            with open(item_path + '/data.json', 'w') as f:
                    json.dump(product, f, indent=4, 
                    default=lambda o: '<not serializable>', ensure_ascii=False)
        
            self.download_save_images(product, item_path)
            
    
    def download_save_images(self,product, item_path):
        # create image folder for each product
        images_dir = "images"
        images_dir_path = os.path.join(item_path +'/' + images_dir)
        os.mkdir(images_dir_path)
        print(images_dir_path)
        for count, image_url in enumerate(product['contents']['Images']):
            image_datetime =  datetime.datetime.now()
            image_day = image_datetime.strftime('%d')
            image_month = image_datetime.strftime('%m')
            image_year = image_datetime.strftime('%Y')
            image_seconds = image_datetime.strftime('%f')
            image_order = count
            image_file_name_png = f"{image_day}{image_month}{image_year}_{image_seconds}_{image_order}.png"
            try:
                with urllib.request.urlopen(image_url) as web_file:
                    data = web_file.read()
                    with open(images_dir_path + '/' + image_file_name_png, mode='wb') as local_file:
                        local_file.write(data)
            except:
                pass


def run_scraper():
    scraper = TPW(driver)
    '''scraper.load_and_accept_cookies()
    scraper.pop_up()
    scraper.scroll()
    scraper.click_next_page()
    scraper.close_driver()
    scraper.get_pages()'''
    scraper.get_data()
    scraper.close_driver()


if __name__ == '__main__':
    print('this is running directly')
    run_scraper()

