# Data-Collection-Pipeline

An industry-grade data pipeline that is scalable on the cloud.
- The website: https://www.theproteinworks.com/products is scraped to obtain information on every product and store them in json. This website is used, as helpful information could be scraped such as the product range, type of product, descriptions,flavours, prices, reviews and images. 
- Technologies used: Python, OOP, Selenium (Scraping Library), Docker (Containerisation)

## Milestone 1: Load libraries, set URL and driver variables.

- The neccessary libraries and modules are loaded like time.sleep and selenium.webdriver.
- The url for the website to be scraped is stored in variable url
- The chrome driver provided by selenium is stored in variable driver
- The driver gets and loads the website to be scraped

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

url = 'https://www.theproteinworks.com/products'
options = Options() 
options.add_argument("--headless") 
options.add_argument("window-size=1920,1080") 
driver = webdriver.Chrome(options=options)
driver.get(url)
```

## Milestone 2: Create Scraper Class

- A class called TPW (The Protein Works) is created with attributes driver, product_urls_list, page_urls_list, product_list and id_list.
- `self.page_urls_list` and `self.product_urls_list` are for iterating thorugh obtained urls to scrape data from.
- `self.product_dict_list` and `self.id_list` are for containing product dictionaries and product unique ids respectively.

```python
class TPW:

    def __init__(self):
        self.driver = driver
        self.page_urls_list = []
        # empty self.product_urls_list when scraping whole website
        self.product_urls_list = []
        self.product_dict_list = []
        self.id_list = []
```

## Milestone 3: Create Methods to deal with cookies and pop-ups

- The method load_and_accept_cookies seeks the element marked as the cookies pop-up window by XPATH and clicks on the button that exits the window.
    - In this case, the pop-up is a div instead of a window, so treated as such.
    - This is done inside a try and accpt block, as the window doesn't show up all the time.

- The method pop_up follows similar convention to load_and_accept_cookies, seeking the element by XPATH and clicking to exit the window; likewise it is done in a try and accept block and is a div.

``` python


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

 ```

## Milestone 4: Create methods to interact with website

- More methods are added for website interaction, namely to scroll, close driver (or website), click on the next page of product contents and get all the page urls covering all the product listings.

- All but the latter method requires the use of the driver to execute.

```python
        def scroll(self):
        '''
        Scrolls to the end of page
        '''
        sleep(1)
        self.driver.execute_script("window.scrollBy(0,1000)")
        sleep(1)
        self.driver.execute_script("window.scrollBy(0,1000)")
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
                                value='//*[@id="__next"]/div/div[3]/div/div[2]/div[2]/div/'
                                'section[2]/div/div[2]/div[3]/div/ul/li[10]')
        next_page.click()
        
    
    def get_pages(self):
        '''
        Grabs all the available page urls
        '''
        sleep(1)
        for i in range(1,8):
            page_url = url + f'/page/{i}' 
            self.page_urls_list.append(page_url)
        print(self.page_urls_list)
```

- The method `operate_driver()` runs the interactive methods in a sequence for demonstration.

```python
def operate_driver(self):
        self.__load_and_accept_cookies()
        self.__pop_up()
        self.__scroll()
        self.__click_next_page()
        self.__close_driver()
```

## Milestone 5: Call Class Methods and run Script under if __main__ == '__name__'

- The function run_scraper() runs all the methods within the TPW class to test them in sequence. 

- This function is called within the `if __main__ == '__name__'` so that it runs if the script is run directly, and does't run if imported from another file. 

``` python
def run_scraper():
    '''
    Creates an instance of the scraper class TPW and calls its methods in sequence
    '''
    scraper = TPW()
    scraper.operate_driver()
    scraper.get_page_links(1)
    scraper.get_product_links()
    scraper.generate_product_dictionaries()
    scraper.create_json("/home/van28/Desktop/AiCore/Scraper_Project")


if __name__ == '__main__':
    print('this is running directly')
    run_scraper()
```

## Milestone 6: Create Methods to scrape and store text and image data

- The website is not too dynamic to need selenium, hence to scrape the items (name, price, description, images etc) for each product, the requests and BeautifulSoup libraries are used as a straightforward way to locate and scrape html objects given a parsed url page. 
- The sequence of steps for scraping the website are split into methods: `generate_product_dictionaries(self)` ,`scrape_contents(self,contents, soup)` and `retrieve_image_link(self, soup,contents)`.
- The other methods deal with storing the scraped data temporarily: `populate_contents_dict(self, contents...)`, and `append_products(self,contents,product,id)`.
- This makes the code more concise and easier to follow than cramming all functionalities in one method.

- `generate_product_dictionaries(self)` loops through all the urls from `self.product_urls_list`, converts them into requests objects, to then a Beautiful Soup object for locating of html elements.
- It creates dictionaries to store the data:
    - Each product is represented as a dictionary that contains the id, scrape time and a nested dictionary called 'contents' which contain the scraped         items which are text and image src data.
    - The uuid library makes it simple to generate unique ids for each product, which would then be used to identify directories.
        - ids are used to identify products when the data is stored locally.
- Other methods are called to populate the product dictionary and append it on the product_list.

```python
   def generate_product_dictionaries(self):
        '''
        1. Creates a product dictionary for each listed product. 
        2. Initiates requests and BeautifulSoup objects for locating elements
        3. Calls on other methods to fill in dictionaries with metadata, text and image data.

        Parameters:
        ----------
        product_urls_list: list
            A list of obtained urls for each product
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

        Returns:
        ----------
        self.create_json(self.product_list, self.id_list): method
            calls the method to create a json file from the product dictionary
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

            self.scrape_contents(contents, soup)
            self.retrieve_image_link(soup, contents)
            self.append_products(contents,product,id)
            
```

- `scrape_contents(self,contents, soup)` locates the neccessary HTML elements, stores them in corresponding variables then returns them in a method call along with the contents dictionary. 
- The name of the class or id is used to locate some of the text elements using BeautifulSoup. 
- For `price`, a try and except clause is used to avoid the scraper being distrupted with an exception error, as a few product pages may find its price <span> tag embedded differently to most other product pages. 
          
```python
    def scrape_contents(self,contents, soup):
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
        price = soup.select('span.ProductItem_price_normal__wYpSr.price_normal.price_special')[0].text
        description_short = soup.find(id='product-description-short').text
        sizes = soup.find(class_='ProductItem_size__3Ux92 size btn-group')
        flavours = soup.find(class_='form-select')
        description_long = soup.find(class_='RRT__panel panel').text
        rating_percentage = soup.find(class_='ProductItem_rating__1WQSr').text
        number_of_reviews = soup.find(class_='ProductItem_reviews__2xbGO').text
        number_of_reviews = re.sub(r'\W+','',number_of_reviews)
        
        return self.populate_contents_dict(contents, product_name, price, description_short, sizes, 
                        flavours,description_long, rating_percentage, number_of_reviews)
```

- The method `populate_contents_dict` adds the scraped elements to the contents dictionary.
- For Sizes and Flavours, list comprehension is used to iterate through the form options and append them to their corresponding lists.

```python

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
        [contents["Sizes"].append(options.text) for options in sizes]
        [contents["Flavours"].append(options.text) for options in flavours]
        contents["Description Long"].append(description_long)
        contents["Rating Percentage"].append(rating_percentage)
        contents["Number of Reviews"].append(number_of_reviews)
```

- Instead of locating each image element individually, `retrieve_image_link(self, soup,contents)` scrapeds all avaialble image src elements for simplicity. Unneccessary images can be filtered out at a later stage of the pipeline.

```python
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
```
- `append_products` takes the contents dictionary and appends to the product dictionary.
- The product dictionary is then appended to `self.product_list`.

```python

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
        self.product_dict_list.append(product)
        self.id_list.append(id)
        '''
```

## Milestone 7: Create new directories to store json files of each product

- To create the directories for the raw data collected, the os library is used to access the local filing system and the json library is use to create json objects from the python dictionaires.

- An optional file path is taken as argument to specify in string format the local path which the user wants to save the data to.
    
- If a file path is not specified, the user's current directory is taken as argument. 

- A folder called 'raw_data' is created if it doesn't yet exist where the json files corresponding to the product are created.
    - This allows flexibility when the code is containerized, (i.e. using Docker) and a folder of the same name is already created.  

- The product and id lists are iterated in parallel using zip; each id becomes the name of a folder conataining the json of the corresponding product.

- Within the same loop, the next method is called to open and download the src links within each product folder and save them in the same location.

```python
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
```

## Milestone 8: Extract and download each image src from each product and save to the corresponding directories 

- Using the urllib library, every src link in each product folder is downloaded (if possible) on the web and saved in a local folder called 'images' within the same product folder.

- The datetime library is used to construct the name that represents each image downloaded in sequence; the format is '<date>_<time>_<order of image>.<image file extension>' as shown in the variable `image_file_name_png` which creates the name of the image file.

- Within the loop of the previous method `create_json`, another loop in this method `download_save_images` iterates over the src links and using enurmerate, counts and assigns the order of images saved and downloaded.

```python
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

```

## Milestone 9: Create Unit Tests to Run

- The file test_scraper.py is a module with five unit tests for the public methods namely `test_get_pages()`, `test_generate_product_dictionaries()`, `test_scrape_day()`, `test_pound_sign()`, `test_key_values_type()`. 
- These test different aspects of the outputted scraped data to ensure that the correct information is being scraped for the product, in the expected format and data type.

```python
from TPW_scraper import *
import unittest

```

- Upon initialising, an instance of the class `TPW()` is initiated, with the website url of one of the products being the test website and stored in `self.test.product_urls_list`.
- The dictionary generated in `self.test.generate_product_dictionaries` is the output against which aspects of it are test against expected values.

```python
class TpwTestCase(unittest.TestCase):

    def setUp(self):
        self.test = TPW()
        self.test.product_urls_list = ['https://www.theproteinworks.com/upgrade']
        self.test.generate_product_dictionaries()
```
- `test_get_pages()` expects a list of paginated urls available scrape from.

```python
        
    def test_get_pages(self):
        self.test.get_pages()
        expected_value= ['https://www.theproteinworks.com/products/page/1',
        'https://www.theproteinworks.com/products/page/2',
        'https://www.theproteinworks.com/products/page/3',
        'https://www.theproteinworks.com/products/page/4',
        'https://www.theproteinworks.com/products/page/5',
        'https://www.theproteinworks.com/products/page/6',
        'https://www.theproteinworks.com/products/page/7']
        actual_value = self.test.page_urls_list
        self.assertEqual(expected_value, actual_value)
```
-`test_generate_product_dict_name()` expects the correct name of the product being scraped. 
- The page may change in the future, including the name of the product, so it is a good test to ensure that the correct name to date is obtained.

```python

    def test_generate_product_dict_name(self):
        expected_value = "Upgrade Multi-Protein"
        actual_value = self.test.product_list[0]['contents']['Product Name'][0]
        self.assertEqual(expected_value, actual_value)
```
- `test_scrape_day()` tests that the `timedate.timedate.now().strftime('%c')` is working correctly by outputting a valid abbreviated day of the week in the first three characters.

```python

    def test_scrape_day(self):
        days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
        day = self.test.product_list[0]['time'][0:3]
        self.assertTrue(day in days)
```

-`test_pound_sign` checks that a pound sign is included in the price scraped.

```python
    def test_pound_sign(self):
        price = self.test.product_list[0]['contents']['Price'][0]
        self.assertRegex('£', price[0])
        
```
`test_key_values_type()` checks that all values in the product dictionary are a string datatype, provided that they can be accessed as list via iteration. Essentially it checks that all values are a list within which a string(s) are found.

```python 
    def test_key_values_type(self):
        for k in self.test.product_list[0]['contents']:
            value_list = self.test.product_list[0]['contents'][k]
            for value in value_list: 
                self.assertIsInstance(value, str)
```
- `tearDown()` deletes the instance of the class once the tests are completed

```python

    def tearDown(self):
        del self.test
        
```
## Milestone 10: Build Docker image, run container and push image to Docker Hub
    
Building the Image:    
    
- A Dockerfile is created with the sequence of steps to build the docker image.
- The docker image is built using `docker build -t <image_name>:<version> [DOCKERPATH]`
- The docker image is tagged using `docker tag [IMAGE_ID] [IMAGE_NAME]`
   where [IMAGE_NAME] is `<username>/<image_name>:<version>`
- After logging in to Docker Hub with the Docker ID, the docker image is pushed using `docker push [IMAGE_NAME]`
    
Running the Container with a Docker Volume:
    
- The image has been built, so it can run a container with it.
- To run the container: `docker run -v [LOCAL_PATH]:[DOCKER_PATH] <image_name>`
    - Where `-v` specifies to run the container with a Docker Volume so the contents scraped can be saved on the local machine.
    - Since the data scraped is saved in a folder called `raw_data`, that would be the name of the `[DOCKERPATH]` .i.e, `/raw_data`
    - `<image_name>` not to be confused with `[IMAGE_NAME]` created to tag the image when pushing to Docker Hub
    
## Milestone 11: Set up CI/CD pipeline using Github Actions

- CI/CD stands for Continuous Integration/ Continuous Deployment.
- Using a CI/CD pipeline like Github Actions allows a workflow/automation of processes to be executed everytime a pull or push action is done on the Github repo.
- This is useful for seemless integration of new features to production without a third-party tool to do it i.e. since the app is in Github, Github Actions can perform this.
    - The main.yml script is created to specify the actions to be performed automatically.
    - In this case, the yaml script will push an image to Docker Hub when a repo pull or push is performed. This will mean an image with the implemented        changes to the repo or code i.e., `TPW_scraper.py` will be push automatically.  
- The documentation below is followed to build a CI/CD pipeline using Github actions:
    https://docs.docker.com/build/ci/github-actions/
    
