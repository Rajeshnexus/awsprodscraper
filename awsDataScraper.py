from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import random

# Set up the browser options
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Optional, to run in headless mode
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Initialize the driver
driver = webdriver.Chrome(options=options)

# Define URL for the toys category on Amazon
url = "https://www.amazon.in/s?k=toy"

# Open the URL
driver.get(url)

# Initialize lists to hold the scraped data
product_names = []
prices = []
urls = []

# Define the number of pages to scrape
num_pages = 3  # Adjust as necessary

for page in range(1, num_pages + 1):
    print(f"Scraping page {page}...")

    # Wait until product listings are present on the page
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@data-component-type='s-search-result']"))
        )
    except:
        print("Failed to load product listings.")
        break

    # Locate product listings
    products = driver.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")

    for product in products:
        try:
            # Get product name
            name = product.find_element(By.XPATH, ".//span[@class='a-size-medium a-color-base a-text-normal']").text
            product_names.append(name)
        except:
            product_names.append("N/A")

        try:
            # Get product price
            price = product.find_element(By.XPATH, ".//span[@class='a-price-whole']").text
            prices.append(price)
        except:
            prices.append("N/A")

        try:
            # Get product URL and filter out video URLs
            product_url = product.find_element(By.XPATH, ".//a[@class='a-link-normal s-no-outline']").get_attribute("href")
            if "gp/video" not in product_url and "primevideo.com" not in product_url:
                urls.append(product_url)
            else:
                urls.append("N/A")
        except:
            urls.append("N/A")

    # Try to click the "Next" button
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[@class='a-last']/a"))
        )
        next_button.click()
        # Random sleep to mimic human behavior
        time.sleep(random.uniform(2, 5))
    except:
        print("No more pages found or failed to navigate to the next page.")
        break

# Close the browser
driver.quit()

# Save data to a DataFrame
data = pd.DataFrame({
    "Product Name": product_names,
    "Price": prices,
    "URL": urls
})

# Save to CSV
data.to_csv("amazon_toys.csv", index=False)

print("Data has been saved to amazon_toys.csv")




#########################################################################################################
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# import time
# import pandas as pd

# # Set up the browser options (optional)
# options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Run in headless mode to avoid opening the browser

# # Initialize the driver
# driver = webdriver.Chrome(options=options)

# # Define URL for the toys category on Amazon
# url = "https://www.amazon.in/s?k=toy"

# # Open the URL
# driver.get(url)
# time.sleep(2)  # Let the page load

# # Initialize lists to hold the scraped data
# product_names = []
# prices = []
# urls = []

# # Define the number of pages to scrape
# num_pages = 3  # Adjust as necessary

# for page in range(1, num_pages + 1):
#     print(f"Scraping page {page}...")
#     time.sleep(2)  # Pause for loading

#     # Locate product listings
#     products = driver.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")

#     for product in products:
#         try:
#             # Get product name
#             name = product.find_element(By.XPATH, ".//span[@class='a-size-medium a-color-base a-text-normal']").text
#             product_names.append(name)
#         except:
#             product_names.append("N/A")

#         try:
#             # Get product price
#             price = product.find_element(By.XPATH, ".//span[@class='a-price-whole']").text
#             prices.append(price)
#         except:
#             prices.append("N/A")

#         try:
#             # Get product URL and filter out video URLs
#             product_url = product.find_element(By.XPATH, ".//a[@class='a-link-normal s-no-outline']").get_attribute("href")
#             if "gp/video" not in product_url and "primevideo.com" not in product_url:
#                 urls.append(product_url)
#             else:
#                 urls.append("N/A")
#         except:
#             urls.append("N/A")

#     # Go to the next page if there is one
#     try:
#         next_button = driver.find_element(By.XPATH, "//li[@class='a-last']/a")
#         next_button.click()
#         time.sleep(2)
#     except:
#         print("No more pages found or failed to navigate to the next page.")
#         break

# # Close the browser
# driver.quit()

# # Save data to a DataFrame
# data = pd.DataFrame({
#     "Product Name": product_names,
#     "Price": prices,
#     "URL": urls
# })

# # Save to CSV
# data.to_csv("amazon_toys.csv", index=False)

# print("Data has been saved to amazon_toys.csv")
