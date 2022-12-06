from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep
import datetime
import json
import os
import requests
import re
import uuid
import urllib.request

url = 'https://www.theproteinworks.com/products'
options = Options() 
options.add_argument("--headless") 
options.add_argument("window-size=1920,1080") 
options.add_argument("--no-sandbox"),
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)
driver.get(url)

class TPW:

    '''
    A webscraper class that has methods to interact with, scrape data from and locally store 
    data from The Protein Works website

    Attributes:
    ----------
    driver: selenium webdriver object
        A webdriver (Chrome) that drives the website(s) listed in the page_urls_list

    page_urls_list: list
        A list of available page urls obtained from the main website

    product_urls_list: list
        A list of obtained product urls
    
    product_dict_list: list
        A list of product dictionaries
    
    id_list: list
        A list of the ids of the product dictionaries
    
    Methods:
    ----------
    __load_and_accept_cookies()
        Clicks on the agree button on the pop-up window asking to accept cookies

    operate_driver()
        Interacts with the website with a sequence of driver methods 

    __pop_up()
        Clicks on the exit button on the promo pop-up window

    __scroll()
        Scrolls to the end of page

    __close_driver()
        Closes the webdriver and browser

    __click_next_page()
        Clicks on the next page button 

    get_page_links()
        Grabs all the available page urls
    
    get_product_links()
        Grabs all the available product links on the page

    generate_product_dictionaries()
        Creates a dictionary for each product that contains data about the product and metadata. 
        Also initiates requests and BeautifulSoup objects for locating elements

    __scrape_contents(contents, soup)
        Locates and grabs elements where text data is found

    __populate_contents_dict(contents,product_name, price, 
                        description_short, sizes, flavours,
                        description_long, rating_percentage, 
                        number_of_reviews)
        Populates the contents dictionary with the scraped text data
        
    __retrieve_image_link(soup,contents)
        Retrieves all src links available on the page

    __append_products(contents,product,id)
        Appends contents dictionary to the product dictionary
        Adds the product dictionary and id to the product list and id list

    create_json(raw_data_path)
        Creates a json file from each product dictionary and saves in the folder raw_data 

    __download_save_images(product, item_path)
        Downloads src links from each product dictionary and saves images locally
    '''
    def __init__(self):
        self.driver = driver
        self.page_urls_list = []
        self.product_urls_list = []
        self.product_dict_list = []
        self.id_list = []

    def operate_driver(self):
        self.__load_and_accept_cookies()
        self.__pop_up()
        self.__scroll()
        self.__click_next_page()
        self.__close_driver()

    def __load_and_accept_cookies(self):
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

    def __pop_up(self):
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

    def __scroll(self):
        '''
        Scrolls to the end of page
        '''
        sleep(1)
        self.driver.execute_script("window.scrollBy(0,1000)")
        sleep(1)
        self.driver.execute_script("window.scrollBy(0,1000)")
        sleep(1)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def __close_driver(self):
        '''
        Closes the webdriver and browser
        '''
        sleep(1)
        self.driver.close()

    def __click_next_page(self):
        '''
        Locates and clicks on the next page button
        '''
        sleep(1)
        next_page = self.driver.find_element(by=By.XPATH, 
                                value='//*[@id="__next"]/div/div[3]/div/div[2]/div[2]/div/'
                                'section[2]/div/div[2]/div[3]/div/ul/li[10]')
        next_page.click()
        
    
    def get_page_links(self, number_of_pages):
        '''
        Grabs all the available page urls

        Parameters:
        ----------
        page_urls_list: list
        A list of available page urls obtained from the main website
        '''
        sleep(1)
        if number_of_pages + 1 > 8:
            print('Specify a number less than 8')
        else:
            for i in range(1,number_of_pages + 1):
                page_url = url + f'/page/{i}' 
                self.page_urls_list.append(page_url)
                print(self.page_urls_list)


    def get_product_links(self):
        '''
        Grabs all the available product links on the page

        Parameters:
        ----------
        product_urls_list: list
            A list of obtained product urls
        '''
        sleep(1)
        for page in self.page_urls_list:
            response = requests.get(page)
            sleep(1)
            soup = BeautifulSoup(response.content, "html.parser")
            product_grid = soup.select('ul.list-unstyled.row.product-list.product-items')[0]
            product_grid = product_grid.select('li.grid-item')
            for product in product_grid:
                product = product.select('a.ProductItem_product_name__2JI6M.product-item-'
                                        'link.product-name.no-hover-effect', href=True)[0]
                self.product_urls_list.append(product['href'])


    def generate_product_dictionaries(self):
        '''
        1. Creates a product dictionary for each listed product. 
        2. Initiates requests and BeautifulSoup objects for locating elements
        3. Calls on other methods to fill in dictionaries with metadata, text and image data.

        Parameters:
        ----------
        product_urls_list: list
            A list of obtained product urls 
        response: requests object
            Parses an url to get the HTML of the website
        soup: BeautifulSoup object
            Parses request object to get BeautifulSoup HTML document
        id: str
            Unique id to identify a product
        contents: dict
            A dictionary containing the text and src data of the product
        product: dict
            A product dictionary containing the metadata and the contents dictionary
        '''
        for product_url in self.product_urls_list:
            response = requests.get(product_url)
            sleep(1)
            soup = BeautifulSoup(response.content, "html.parser")
            id = uuid.uuid4().hex
            # Create dictionary for each product to contain id, time scraped, text data and image data
            product = {'unique id ':id, 'time' : str(datetime.datetime.now().strftime('%c')), 
                        'contents' : None}
            contents = {"Product Name": [],"Price": [],"Description Short":[],
                                "Sizes":[],"Flavours":[],"Description Long" :[], 
                                "Rating Percentage" : [],"Number of Reviews":[], "Images":[]}

            self.__scrape_contents(contents, soup)
            self.__retrieve_image_link(soup, contents)
            self.__append_products(contents,product,id)
            

    def __scrape_contents(self,contents, soup):
        '''
        Locates and grabs elements where text data is found

        Parameters:
        ----------
        contents: dict
            Dictionary containing scraped data about the product
        soup: BeautifulSoup Object
            Parses request object to get BeautifulSoup HTML document
        '''
        sleep(1)
        # Scrape each category of text data and add to dictionary
        product_name = soup.find('h1').text  
        try:
            price = soup.select('span.ProductItem_price_normal__wYpSr.price_normal.price_special')[0].text
        except:
            price = ""
        description_short = soup.find(id='product-description-short').text
        sizes = soup.find(class_='ProductItem_size__3Ux92 size btn-group')
        flavours = soup.find(class_='form-select')
        description_long = soup.find(class_='RRT__panel panel').text
        rating_percentage = soup.find(class_='ProductItem_rating__1WQSr').text
        number_of_reviews = soup.find(class_='ProductItem_reviews__2xbGO').text
        number_of_reviews = re.sub(r'\W+','',number_of_reviews)
        
        return self.__populate_contents_dict(contents, product_name, price, description_short, sizes, 
                        flavours,description_long, rating_percentage, number_of_reviews)


    def __populate_contents_dict(self, contents,product_name, price, description_short, sizes, 
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
        [contents["Sizes"].append(options.text) for options in sizes]
        [contents["Flavours"].append(options.text) for options in flavours]
        contents["Description Long"].append(description_long)
        contents["Rating Percentage"].append(rating_percentage)
        contents["Number of Reviews"].append(number_of_reviews)
    
    def __retrieve_image_link(self, soup,contents):
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

    def __append_products(self,contents,product,id):
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
        self.product_dict_list.append(product)
        self.id_list.append(id)

    def create_json(self, file_path=None):    
        '''
        1. Creates a new folder raw_data if it doesn't yet exist
        2. Has an option to pass a local directory to which raw_data is saved in
        3. Jointly iterates through the id_list and product_list to create a directory for each product 
        with the id as the name of the directory. 
        4. Each product dictionary is converted into a json file and is saved within its corresponding directory
        
        Parameters:
        ----------
        file_path: str
            local directory to store the scraped data in
        '''
        # set project directory, make raw data directory if non-existent yet
        raw_data_path = "raw_data"
        if file_path == None:
            pass
        else:
            raw_data_path = os.path.join(file_path, "raw_data")
            os.mkdir(raw_data_path)
            print("Directory 'raw_data' created")
        
        # loop through ids and results in lists of scraped data and ids.
        # create folders of each id name and dump json file of each product
        for id, product in zip(self.id_list, self.product_dict_list):
            item_dir = id
            item_path = os.path.join(raw_data_path, item_dir)
            os.mkdir(item_path)
            print(item_path)
            with open(item_path + '/data.json', 'w') as f:
                    json.dump(product, f, indent=4, 
                    default=lambda o: '<not serializable>', ensure_ascii=False)
        
            self.__download_save_images(product, item_path)
                
    def __download_save_images(self,product, item_path):
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
    scraper = TPW()
    scraper.operate_driver()
    scraper.get_page_links(1)
    scraper.get_product_links()
    scraper.generate_product_dictionaries()
    scraper.create_json()


if __name__ == '__main__':
    print('this is running directly')
    run_scraper()

