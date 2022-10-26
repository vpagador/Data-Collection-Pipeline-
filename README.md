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
