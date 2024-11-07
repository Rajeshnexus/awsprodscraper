import selenium
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
import time
import warnings

warnings.filterwarnings('ignore')

# Set up Chrome options and service
options = Options()
service = Service(r"C:\chromedriver-win64\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

# Open Amazon's website
driver.get("https://www.amazon.in/")

try:
    # Wait until the search box is available, then enter the product name
    search = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'twotabsearchtextbox'))
    )
    search.send_keys(input('Enter the search value: '))

    # Click on the search button
    find = driver.find_element(By.ID, 'nav-search-submit-button')
    find.click()

    product_links = []

    # Scrape all pages
    while True:
        # Wait for product links to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]'))
        )
        
        # Collect product links on the current page
        product_links_elems = driver.find_elements(By.XPATH, '//a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]')
        for elem in product_links_elems:
            product_links.append(elem.get_attribute("href"))

        # Check if there is a next page and click it, otherwise break the loop
        try:
            next_button = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, '//a[contains(@class, "s-pagination-next")]'))
            )
            next_button.click()
            time.sleep(3)  # Give it a moment to load the next page
        except (NoSuchElementException, TimeoutException):
            # If no next button is found or timeout occurs, break the loop
            print("No more pages found.")
            break

    # Create a list to hold the scraped data
    scrap_data = []

    # Loop through each product link and scrape the details
    for link in product_links:
        driver.get(link)
        time.sleep(2)
        
        try:
            brand = driver.find_element(By.XPATH, '//td[@class="a-span9"]/span').text.strip()
        except NoSuchElementException:
            brand = "-"
        try:
            name = driver.find_element(By.ID, "productTitle").text.strip().split(',')[0]
        except NoSuchElementException:
            name = "-"
        try:
            price = driver.find_element(By.XPATH, '//span[@class="a-price-whole"]').text.strip()
        except NoSuchElementException:
            price = "-"
        try:
            return_exchange = driver.find_element(By.XPATH, '//li[3][@class="a-carousel-card tw-scroll-carousel-element"]/div/span/div[2]/a').text.strip()
        except NoSuchElementException:
            return_exchange = "-"
        try:
            expected_delivery = driver.find_element(By.XPATH, '//span[@class="a-text-bold"]').text.strip()
        except NoSuchElementException:
            expected_delivery = "-"
        try:
            availability = driver.find_element(By.ID, "availability").text.strip()
        except NoSuchElementException:
            availability = "-"
        
        scrap_data.append([brand, name, price, return_exchange, expected_delivery, availability, link])

    # Save the scraped data to a CSV file
    df = pd.DataFrame(scrap_data, columns=["Brand Name", "Name of the Product", "Price", "Return/Exchange", "Expected Delivery", "Availability", "Product URL"])
    df.to_csv("amazon_products.csv", index=False)

finally:
    # Close the webdriver instance
    driver.quit()


###########################################################################################
# import selenium
# import pandas as pd
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
# from selenium.webdriver.common.by import By
# import time
# import warnings

# warnings.filterwarnings('ignore')

# # Set up Chrome options and service
# options = Options()
# service = Service(r"C:\chromedriver-win64\chromedriver-win64\chromedriver.exe")
# driver = webdriver.Chrome(service=service, options=options)

# # Open Amazon's website
# driver.get("https://www.amazon.in/")

# try:
#     # Wait until the search box is available, then enter the product name
#     search = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.ID, 'twotabsearchtextbox'))
#     )
#     search.send_keys(input('Enter the search value: '))

#     # Click on the search button
#     find = driver.find_element(By.ID, 'nav-search-submit-button')
#     find.click()

#     product_links = []
#     for page in range(1, 4):
#         # Wait for product links to load
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_all_elements_located((By.XPATH, '//a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]'))
#         )
        
#         product_links_elems = driver.find_elements(By.XPATH, '//a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]')
#         for elem in product_links_elems:
#             product_links.append(elem.get_attribute("href"))
        
#         # Click on the next page button if there is another page
#         if page < 3:
#             next_button = WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable((By.XPATH, '//a[@class="s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"]'))
#             )
#             next_button.click()
#             time.sleep(2)

#     # Create a list to hold the scraped data
#     scrap_data = []

#     # Loop through each product link and scrape the details
#     for link in product_links:
#         driver.get(link)
#         time.sleep(2)
        
#         try:
#             brand = driver.find_element(By.XPATH, '//td[@class="a-span9"]/span').text.strip()
#         except NoSuchElementException:
#             brand = "-"
#         try:
#             name = driver.find_element(By.ID, "productTitle").text.strip().split(',')[0]
#         except NoSuchElementException:
#             name = "-"
#         try:
#             price = driver.find_element(By.XPATH, '//span[@class="a-price-whole"]').text.strip()
#         except NoSuchElementException:
#             price = "-"
#         try:
#             return_exchange = driver.find_element(By.XPATH, '//li[3][@class="a-carousel-card tw-scroll-carousel-element"]/div/span/div[2]/a').text.strip()
#         except NoSuchElementException:
#             return_exchange = "-"
#         try:
#             expected_delivery = driver.find_element(By.XPATH, '//span[@class="a-text-bold"]').text.strip()
#         except NoSuchElementException:
#             expected_delivery = "-"
#         try:
#             availability = driver.find_element(By.ID, "availability").text.strip()
#         except NoSuchElementException:
#             availability = "-"
        
#         scrap_data.append([brand, name, price, return_exchange, expected_delivery, availability, link])

#         # Stop if we reach 144 products
#         if len(scrap_data) >= 144:
#             break

#     # Save the scraped data to a CSV file
#     df = pd.DataFrame(scrap_data, columns=["Brand Name", "Name of the Product", "Price", "Return/Exchange", "Expected Delivery", "Availability", "Product URL"])
#     df.to_csv("amazon_products.csv", index=False)

# finally:
#     # Close the webdriver instance
#     driver.quit()

###########################################################################
# import selenium
# import pandas as pd
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# import warnings
# warnings.filterwarnings('ignore')
# from selenium.common.exceptions import StaleElementReferenceException,NoSuchElementException
# from selenium.webdriver.common.by import By
# import time

# # connecting to the crome
# # driver=webdriver.Chrome(r"chromedriver.exe")
# options = Options()
# service = Service(r"C:\chromedriver-win64\chromedriver-win64\chromedriver.exe")  # Replace with the full path if necessary
# driver = webdriver.Chrome(service=service, options=options)

# # searching the website
# driver.get("https://www.amazon.in/")

# # entering the product name
# search=driver.find_element(By.ID,'twotabsearchtextbox')
# search.send_keys(input('Enter the search value :'))

# # searching the product
# find=driver.find_element(By.ID,'nav-search-submit-button')
# find.click()

# product_links = []
# for page in range(1, 4):
#     product_links_elems = driver.find_elements(By.XPATH,'//a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]')
#     for elem in product_links_elems:
#         product_links.append(elem.get_attribute("href"))
#     if page < 3:
#         next_button = driver.find_element(By.XPATH,'//a[@class="s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"]')
#         next_button.click()
#         time.sleep(2)

#         # Create a list to hold the scraped data
# scrap_data = []

# # Loop through each product link and scrape the details
# for link in product_links:
#     driver.get(link)

#     time.sleep(2)
#     try:
#         brand = driver.find_element(By.XPATH,'//td[@class="a-span9"]/span').text.strip()
#     except:
#         brand = "-"
#     try:
#         name = driver.find_element(By.ID,"productTitle").text.strip().split(',')[0]
#     except:
#         name = "-"
#     try:
#         price = driver.find_element(By.XPATH,'//span[@class="a-price-whole"]').text.strip()
#     except:
#         price = "-"
#     try:
#         return_exchange = driver.find_element(By.XPATH,'//li[3][@class="a-carousel-card tw-scroll-carousel-element"]/div/span/div[2]/a').text.strip()
#     except:
#         return_exchange = "-"
#     try:
#         expected_delivery = driver.find_element(By.XPATH,'//span[@class="a-text-bold"]').text.strip()
#     except:
#         expected_delivery = "-"
#     try:
#         availability = driver.find_element(By.ID,"availability").text.strip()
#     except:
#         availability = "-"
#     scrap_data.append([brand, name, price, return_exchange, expected_delivery, availability, link])

#     # If we have scraped 144 products, stop the loop (3 pages * 48 products per page)
#     if len(scrap_data) >= 144:
#         break

# # Create a pandas dataframe with the scraped data and save it to a CSV file
# df = pd.DataFrame(scrap_data, columns=["Brand Name", "Name of the Product", "Price", "Return/Exchange", "Expected Delivery", "Availability", "Product URL"])
# df.to_csv("amazon_products.csv", index=False)

# # Close the webdriver instance
# driver.quit()

