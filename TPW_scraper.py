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

    '''
    A webscraper class that has methods to interact with, scrape data from and locally store 
    data from The Protein Works website
    
    Parameters:
    ----------
    driver: selenium webdriver object
        A webdriver (Chrome) that drives the website(s) listed in the page_urls_list

    Attributes:
    ----------
    page_urls_list: list
        A list of available page urls obtained from the main website
    
    product_list: list
        A list of product dictionaries
    
    id_list: list
        A list of the ids of the product dictionaries
    
    Methods:
    ----------
    load_and_accept_cookies()
        Clicks on the agree button on the pop-up window asking to accept cookies

    pop_up()
        Clicks on the exit button on the promo pop-up window

    scroll()
        Scrolls to the end of page

    close_driver()
        Closes the webdriver and browser

    click_next_page()
        Clicks on the next page button 

    get_pages()
        Grabs all the available page urls

    generate_product_dict()
        Creates the product dictionary that contains data about a product and metadata. 
        Also initiates requests and BeautifulSoup objects for locating elements

    scrape_contents(contents, soup, dom)
        Locates and grabs elements where text data is found

    populate_contents_dict(contents,product_name, price, 
                        description_short, sizes, flavours,
                        description_long, rating_percentage, 
                        number_of_reviews)
        Populates the contents dictionary with the scraped text data
        
    retrieve_image_link(soup,contents)
        Retrieves all src links available on the page

    append_products(contents,product,id, product_list, id_list)
        Appends contents dictionary to the product dictionary
        Adds the product dictionary and id to the product list and id list

    create_json(product_list, id_list)
        Creates a json file from each product dictionary and saves it locally 

    download_save_images(product, item_path)
        Downloads src links from each product dictionary and saves images locally
    '''
    def __init__(self, driver):
        self.driver = driver
        self.page_urls_list = ["https://www.theproteinworks.com/vegan-wondershake",
                                "https://www.theproteinworks.com/whey-protein-360-extreme"]
        self.product_list = []
        self.id_list = []

    def load_and_accept_cookies(self):
        '''
        Clicks on the agree button on the pop-up window asking to accept cookies, 
        if applicatble. If not, passes on the method
        '''
        sleep(2)
        try:
            accept_cookies_button = self.driver.find_element(by=By.XPATH, 
                                    value ='//*[@id="cookieConsent"]/div/div[3]/button')
            accept_cookies_button.click()
            sleep(1)
        except:
            pass

    def pop_up(self):
        '''
        Clicks on the exit button on the promo pop-up window if applicable. 
        If not, passes on the method
        '''
        sleep(1)
        try:
            pop_up = self.driver.find_element(by=By.XPATH, value ='/html/body/div[5]/div/div')
            pop_up_button = pop_up.find_element(by=By.XPATH, value= '/div[1]/button')
            pop_up_button.click()
        except:
            pass

    def scroll(self):
        '''
        Scrolls to the end of page
        '''
        sleep(1)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def close_driver(self):
        '''
        Closes the webdriver and browser
        '''
        sleep(1)
        self.driver.close()

    def click_next_page(self):
        '''
        Locates and clicks on the next page button
        '''
        sleep(1)
        next_page = self.driver.find_element(by=By.XPATH, 
                                value='//*[@id="__next"]/div/div[3]/div/div[2]/div[2]')
        next_page = next_page.find_element(by=By.XPATH, 
                                value='div/section[2]/div/div[2]/div[3]/div/ul/li[10]')
    
    def get_pages(self):
        '''
        Grabs all the available page urls
        '''
        sleep(1)
        for i in range(0,7):
            page_url = url + f'/page/{i}' 
            self.page_urls_list.append(page_url)
        print(self.page_urls_list)

    def generate_product_dict(self):
        '''
        1. Creates the product dictionary that contains data about a product and metadata. 
        2. Initiates requests and BeautifulSoup objects for locating elements

        Parameters:
        ----------
        response: requests object
            Parses an url to get the HTML of the website
        soup: BeautifulSoup object
            Parses request object to get BeautifulSoup HTML document
        dom: etree object
            Parses BeautifulSoup object to get XML tree of the HTML
        id: str
            Unique id to identify a product
        contents: dict
            A dictionary containing the text and src data of the product
        product: dict
            A product dictionary containing the metadata and the contents dictionary

        Returns:
        ----------
        self.create_json(self.product_list, self.id_list): method
            calls the method to create a json file from the product dictionary
        '''
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

            self.scrape_contents(contents, soup, dom)
            self.retrieve_image_link(soup, contents)
            self.append_products(contents,product,id)
        
        # call the create_json method
        return self.create_json()

    def scrape_contents(self,contents, soup, dom):
        '''
        Locates and grabs elements where text data is found

        Parameters:
        ----------
        contents: dict
            Dictionary containing scraped data about the product
        soup: BeautifulSoup Object
            Parses request object to get BeautifulSoup HTML document
        dom: etree Object
            Parses BeautifulSoup object to get XML tree of the HTML
        '''
        sleep(1)
        # Scrape each category of text data and add to dictionary
        product_name = soup.find('h1').text    
        price = dom.xpath('//*[@id="__next"]/div/div[3]/div/section[1]/div/div/div[2]/section/div/div[3]/'
                                'form/div[3]/div[1]/div/div[2]/div/span/span')[0].text
        description_short = soup.find(id='product-description-short').text
        sizes = soup.find(class_='ProductItem_size__3Ux92 size btn-group').text
        flavours = soup.find(class_='form-select').text
        description_long = soup.find(class_='RRT__panel panel').text
        rating_percentage = soup.find(class_='ProductItem_rating__1WQSr').text
        number_of_reviews = soup.find(class_='ProductItem_reviews__2xbGO').text
        number_of_reviews = re.sub(r'\W+','',number_of_reviews)
        
        self.populate_contents_dict(contents, product_name, price, description_short, sizes, 
                        flavours,description_long, rating_percentage, number_of_reviews)


    def populate_contents_dict(self, contents,product_name, price, description_short, sizes, 
                        flavours,description_long, rating_percentage, number_of_reviews):
        '''
        Populates the contents dictionary with the scraped text data

        Parameters:
        ----------
        contents: dict
            A dictionary containing text and image data and metadata for a product
        product_name: str
            The name of the product
        price: str
            The retail price (msrp) of the product
        description_short: str
            Short description of the product found on the product page
        sizes: str
            The size options the product comes in
        flavours: str
            The flavour options the product comes in
        description_long: str
            Longer description of the product found on the product page
        rating_percentage: str
            The percentage rating based on reviews on the product
        number_of_reviews: str
            The number of customer reviews on the product
        '''
        contents["Product Name"].append(product_name)
        contents["Price"].append(price)
        contents["Description Short"].append(description_short)
        contents["Sizes"].append(sizes)
        contents["Flavours"].append(flavours)
        contents["Description Long"].append(description_long)
        contents["Rating Percentage"].append(rating_percentage)
        contents["Number of Reviews"].append(number_of_reviews)
    
    def retrieve_image_link(self, soup,contents):
        '''
        1. Retrieves all src links available on the page 
        2. Appends to the contents dictionary

        Parameters:
        ----------
        soup: BeautifulSoup Object
            Parses request object to get BeautifulSoup HTML document
        contents: dict
            Dictionary containing scraped data about the product
        '''
        # Obtain all available image src and add to dictionary
        images = soup.find_all('img')
        [contents["Images"].append(image['src']) for image in images]

    def append_products(self,contents,product,id):
        '''
        1. Appends contents dictionary to the product dictionary
        2. Adds the product dictionary to the product list
        3. Adds product id to the id list

        Parameters:
        ----------
        contents: dict
            A dictionary containing the text and src data of the product
        product: dict
            A product dictionary containing the metadata and the contents dictionary
        id: str
            Unique id to identify a product
        '''
        # Add contents to the bigger product dictionary 
        product['contents'] = contents
        # Add each product dictionary to the product list
        # and id of each product to the id list 
        self.product_list.append(product)
        self.id_list.append(id)


    def create_json(self):
        '''
        Creates a json file from each product dictionary and saves it locally:
        1. Creates a new directory called 'raw_data' to contain the scraped data for all products
        2. Jointly iterates through the id_list and product_list to create a directory for each product 
        with the id as the name of the directory. 
        3. Each product dictionary is converted into a json file and is saved within its corresponding directory
        '''
        # set project directory, make raw data directory and join them
        parent_dir = "/home/van28/Desktop/AiCore/Scraper_Project"
        raw_data_dir = "raw_data"
        raw_data_path = os.path.join(parent_dir, raw_data_dir)
        os.mkdir(raw_data_path)
        print(f"Directory {raw_data_dir} created")
        
        # loop through ids and results in lists of scraped data and ids.
        # create folders of each id name and dump json file of each product
        for id, product in zip(self.id_list, self.product_list):
            item_dir = id
            item_path = os.path.join(raw_data_path, item_dir)
            os.mkdir(item_path)
            print(item_path)
            with open(item_path + '/data.json', 'w') as f:
                    json.dump(product, f, indent=4, 
                    default=lambda o: '<not serializable>', ensure_ascii=False)
        
            self.download_save_images(product, item_path)
            
    
    def download_save_images(self,product, item_path):
        '''
        Downloads src links from each product dictionary, if possible.
        Else it passes on downloading the src link
        Saves each image locally within each corresponding product directory
        The name of each image follows format '{image_date}_{image_seconds}_{image_order}.png' where:
        1. image_date: The date in dd/mm/YYYY format that the image was downloaded
        2. image_seconds: The time is seconds that the image was downloaded
        3. image_order: The order in which the image was downloaded from the src list

        Parameters:
        ----------
        product: dict
            A product dictionary containing the metadata and the contents dictionary
        item_path: str
            The path of directories where the product directory can be found 
        '''
        # create image folder for each product
        images_dir = "images"
        images_dir_path = os.path.join(item_path +'/' + images_dir)
        os.mkdir(images_dir_path)
        print(images_dir_path)
        for count, image_url in enumerate(product['contents']['Images']):
            image_datetime =  datetime.datetime.now()
            image_date = image_datetime.strftime("%d%m%Y")
            image_seconds = image_datetime.strftime('%f')
            image_order = count
            image_file_name_png = f"{image_date}_{image_seconds}_{image_order}.png"
            try:
                with urllib.request.urlopen(image_url) as web_file:
                    data = web_file.read()
                    with open(images_dir_path + '/' + image_file_name_png, mode='wb') as local_file:
                        local_file.write(data)
            except:
                pass


def run_scraper():
    '''
    Creates an instance of the scraper class TPW and calls its methods in sequence
    '''
    scraper = TPW(driver)
    '''scraper.load_and_accept_cookies()
    scraper.pop_up()
    scraper.scroll()
    scraper.click_next_page()
    scraper.close_driver()
    scraper.get_pages()'''
    scraper.generate_product_dict()
    scraper.close_driver()


if __name__ == '__main__':
    print('this is running directly')
    run_scraper()

