# Data-Collection-Pipeline
2
An industry-grade data pipeline that is scalable on the cloud.
- The website: https://www.theproteinworks.com/products is scraped to obtain information on every product and store them in json. This website is used, as helpful information could be scraped such as the product range, type of product, descriptions,flavours, prices, reviews and images. 
- Technologies used: Python, OOP, Selenium (Scraping Library), Docker (Containerisation)
3
​
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
driver = webdriver.Chrome()
driver.get(url)
```

## Milestone 2: Create Scraper Class with methods to deal with cookies and pop-ups

- A class called TPW (The Protein Works) is created with init method setting variable driver to self.driver so that the driver can be used in other methods.

- The method load_and_accept_cookies seeks the element marked as the cookies pop-up window by XPATH and clicks on the button that exits the window.
    - In this case, the pop-up is a div instead of a window, so treated as such.
    - This is done inside a try and accpt block, as the window doesn't show up all the time.

- The method pop_up follows similar convention to load_and_accept_cookies, seeking the element by XPATH and clicking to exit the window; likewise it is done in a try and accept block and is a div.

``` python
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
 ```

## Milestone 3: Create methods to interact with website

- More methods are added for website interaction, namely to scroll, close driver (or website), click on the next page of product contents and get all the page urls covering all the product listings.

- All but the latter method requires the use of the driver to execute.

```python
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
```
## Milestone 4: Call Class Methods and run Script under if __main__ == '__name__'

- The function run_scraper() runs all the methods within the TPW class to test them in sequence. 

- This function is called within the `if __main__ == '__name__'` so that it runs if the script is run directly, and does't run if imported from another file. 

``` python
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
```

## Milestone 5: Create a Method to scrape text and image data

- The website is not too dynamic to need selenium, hence to scrape the items (name, price, description, images etc) for each product, the requests and BeautifulSoup libraries are used as a straightforward way to locate and scrape html objects given a parsed url page. 

- This method creates lists, one to contain product dictionaries and the other for the product unique id.

- Each page url from the url list are iterated and made into a requests object, to then a Beautiful Soup object for easier locating of html elements.

- The uuid library makes it simple to generate unique ids for each product, which would then be used to identify directories.

- Each product is represented as a dictionary that contains the id, scrape time and a nested dictionary called 'contents' which contain the scraped items which are text and image src data.

- The name of the class or id is used to locate some of the text elements. Using the lxml library, the XPath can also be used to locate elements, in this case the price, which was not straightforwardly accessible by tags due to how it was embedded in the html. 

- Instead of locating each image element individually, all avaialble image src elements are scraped for simplicity. Unneccessary images can be filtered out at a later stage of the pipeline.

- The method returns another method to create new directories and json files for the raw data collected. The product and id lists are returned with it as arguments.

```python
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
            product = {'unique id ':id, 'time' : str(datetime.datetime.now().strftime('%c')), 'contents' : None}
            contents = {"Product Name": [],"Price": [],"Description Short":[],
                                "Sizes":[],"Flavours":[],"Description Long" :[], 
                                "Rating Percentage" : [],"Number of Reviews":[], "Images":[]}
            
            sleep(1)
            # Scrape each category of text data and add to dictionary
            product_name = soup.find('h1').text
            contents["Product Name"].append(product_name)
                    
            price = dom.xpath('//*       [@id="__next"]/div/div[3]/div/section[1]/div/div/div[2]/section/div/div[3]/form/div[3]/div[1]/div/div[2]/div/span/span')[0].text
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
        
```

## Milestone 6: Create new directories to store json files of each product

- To create the directories for the raw data collected, the os library is used to access the local filing system and the json library is use to create json objects from the python dictionaires.

- A folder called 'raw_data' is created, within which a directory and a json file corresponding to the product are created.

- To do this, the product and id lists are iterated in parallel using zip; each id becomes the name of a folder conataining the json of the corresponding product.

- Within the same loop, the next method is called to open and download the src links within each product folder and save them in the same location.

```python
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
                    json.dump(product, f, indent=4, default=lambda o: '<not serializable>', ensure_ascii=False)
        
            self.download_save_images(product, item_path)
```

## Milestone 7: Extract and download each image src from each product and save to the corresponding directories 

- Using the urllib library, every src link in each product folder is downloaded (if possible) on the web and saved in a local folder called 'images' within the same product folder.

- The datetime library is used to construct the name that represents each image downloaded in sequence; the format is '<date>_<time>_<order of image>.<image file extension>' as shown in the variable `image_file_name_png` which creates the name of the image file.

- Within the loop of the previous method `create_json`, another loop in this method `download_save_images` iterates over the src links and using enurmerate, counts and assigns the order of images saved and downloaded.

```python
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
```
