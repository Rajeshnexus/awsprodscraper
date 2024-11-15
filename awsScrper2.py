import selenium
import pandas as pd
import requests
import re
from selenium.webdriver import ActionChains
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException,StaleElementReferenceException
import time
import os
import warnings

warnings.filterwarnings('ignore')

# Set up Chrome options and service
options = Options()
options.add_argument('--ignore-certificate-errors')
service = Service(r"C:\chromedriver-win64\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

# Define a sanitize function to clean the filename
def sanitize_filename(filename, length=10):
    # return re.sub(r'[<>:"/\\|?*]', '', filename)
    # return re.sub(r'[<>:"/\\|?*\n]', '', filename).replace(" ", "_")
       # Keep only alphanumeric characters, make lowercase, and truncate to the specified length
    sanitized = re.sub(r'\W+', '', filename)[:length].lower()
    return sanitized
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
    count = 0  # Initialize counter for products

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
            count += 1  # Increment the counter
            if count >= 10:  # Stop if 10 products have been scraped
                break
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

    print(f"Collected {len(product_links)} product links.")
    
    scrap_data = []  # List to hold all product data
    
     # Directory to save images
    image_dir = "product_images"
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    # Loop through each product link and scrape the details
    for ind, link in enumerate(product_links):
        driver.get(link)
        time.sleep(3)
        
        # print(f"Scraping product: {link}")
        try:
            brand = driver.find_element(By.XPATH, '//td[@class="a-span9"]/span').text.strip()
        except NoSuchElementException:
            brand = "-"
        try:
            name = driver.find_element(By.ID, "productTitle").text.strip().split(',')[0]
            sanitized_name = sanitize_filename(name)  # Apply filename sanitization here
        except NoSuchElementException:
            name = "-"
            sanitized_name = "unknown"  # Default name if not found
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
        try:
            # Locate the description <ul> inside the feature bullets div
            description_elements = driver.find_elements(By.XPATH, '//div[@id="featurebullets_feature_div"]//ul/li/span')
            description = " ".join([item.text.strip() for item in description_elements])
        except NoSuchElementException:
            description = "-"
       
       

        # Wait for the 'productDetails_feature_div' to be visible
        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'productDetails_feature_div'))
            )
             # Initialize an empty dictionary to store specifications
            product_specifications = {}
            # try:
            #     element = WebDriverWait(driver, 5).until(
            #         EC.presence_of_element_located((By.ID, 'productDetails_techSpec_section_1'))
            #     )
            #     driver.execute_script("arguments[0].scrollIntoView();", element)
            # except Exception as e:
            #     print(f"Error mezcal: {e}")
            # Scroll to the 'productDetails_feature_div' section to ensure all elements are visible 
            # driver.execute_script("arguments[0].scrollIntoView();", driver.find_element(By.ID, 'productDetails_techSpec_section_1'))
            # First, attempt to scrape all `<tr>` elements within `productDetails_feature_div`
            try:
                spec_elements = driver.find_elements(By.XPATH, '//div[@id="productDetails_feature_div"]//table//tr')
                print(f"Total 'spec_elements' found in general structure: {len(spec_elements)}")
                driver.execute_script("arguments[0].scrollIntoView();", driver.find_element(By.ID, 'productDetails_techSpec_section_1'))
                for row in spec_elements:
                    try:
                        key = row.find_element(By.XPATH, './th').text.strip()
                        value = row.find_element(By.XPATH, './td').text.strip()
                        product_specifications[key] = value
                    except NoSuchElementException:
                        continue  # Skip rows that don't match the structure

            except NoSuchElementException:
                print("No 'spec_elements' found in the general structure.")

            # Next, check specific tables by their IDs
            table_ids = ['productDetails_techSpec_section_1', 'productDetails_detailBullets_sections1']
            
            for table_id in table_ids:
                try:
                    table = driver.find_element(By.ID, table_id)
                    rows = table.find_elements(By.XPATH, './/tr')
                    print(f"Total rows found in '{table_id}': {len(rows)}")

                    for row in rows:
                        try:
                            key_element = row.find_element(By.XPATH, './th')
                            value_element = row.find_element(By.XPATH, './td')

                            if key_element and value_element:
                                key = key_element.text.strip()
                                value = value_element.text.strip()
                                product_specifications[key] = value
                        except NoSuchElementException:
                            continue  # Skip rows without expected structure
                except NoSuchElementException:
                    print(f"Table '{table_id}' not found.")
            
        except TimeoutException:
            product_specifications = {}
            print("Failed to load product specifications section.")

       

      
        try:
            # Collect review data
            reviews_data = []
            review_elements = driver.find_elements(By.XPATH, '//div[@id="customerReviews"]')
         
            #new code comment
            print(f"Found {len(review_elements)} reviews, Scraping link {ind + 1}.") 
            if len(review_elements) == 0:
                # Print page source for analysis if no reviews found
                print("No reviews found. Here is the page source:")
                # print(driver.page_source[:1000])  # Print only the first 1000 characters for quick debugging
            
                #  cm-cr-dp-review-list for scrolling to review
            for review in review_elements:
                review_data = {}
                try:
                    # Get reviewer name
                    review_data['reviewer_name'] = review.find_element(By.XPATH, './/div[@data-hook="genome-widget"]').text.strip()
                except NoSuchElementException:
                    review_data['reviewer_name'] = None

                # try:
                #     # Get star rating
                #     review_data['star_rating'] = review.find_element(By.XPATH, './/a[@data-hook="review-title"]//i[@data-hook="review-star-rating"]//span[@class="a-icon-alt"]').text.strip()
                # except NoSuchElementException:
                #     review_data['star_rating'] = None

                try:
                    # Locate the star rating element within each review
                    rating_element = review.find_element(By.XPATH, './/a[@data-hook="review-title"]//i[@data-hook="review-star-rating"]')

                    # Extract the class attribute
                    rating_class = rating_element.get_attribute("class")
                    
                    # Find the part of the class that matches "a-star-X" and split to get the rating number
                    rating = next((part for part in rating_class.split() if part.startswith("a-star-")), None)
                    
                    # If a rating is found, extract the number from "a-star-X"
                    if rating:
                        rating_number = rating.split('-')[-1]
                        review_data['star_rating'] = rating_number
                    else:
                        review_data['star_rating'] = None
                        
                except NoSuchElementException:
                    review_data['star_rating'] = None

                try:
                    # Get review text
                    review_data['review_text'] = review.find_element(By.XPATH, './/span[@data-hook="review-body"]').text.strip()
                except NoSuchElementException:
                    review_data['review_text'] = None

             

                reviews_data.append(review_data)
        except NoSuchElementException:
            print("Could not locate review elements.")
            reviews_data = []

        try:
            price = driver.find_element(By.XPATH, '//span[@class="a-price-whole"]').text.strip()
        except NoSuchElementException:
            price = "-"

        # Sanitize the price to make it safe for file naming
        sanitized_price = price.replace(" ", "_").replace(",", "").replace(".", "_")

        try:
            # Locate all <li> elements that trigger the high-res image modal
            li_elements = driver.find_elements(By.XPATH, '//li[@data-csa-c-action="image-block-main-image-hover"]')
            
            # Prepare to store image paths and previous image URL for comparison
            image_paths = []
            previous_img_url = None
            
            # Initialize ActionChains for interactions
            actions = ActionChains(driver)
            
            for idx, li_elem in enumerate(li_elements):
                try:
                    # Click on the <li> element to open the high-res image modal
                    li_elem.click()
                    time.sleep(2)  # Wait for modal to load
                    
                    # Locate the main high-resolution image inside the modal
                    high_res_image_elem = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@id="ivLargeImage"]//img[@class="fullscreen"]'))
                    )
                    
                    # Get the initial high-res image URL
                    high_res_img_url = high_res_image_elem.get_attribute("src")
                    
                    # Ensure the image is unique by comparing with the previous one
                    if high_res_img_url != previous_img_url and high_res_img_url:
                        img_filename = f"{sanitized_name}_price_{sanitized_price}_img_{idx + 1}_high_res.jpg"
                        img_path = os.path.join(image_dir, img_filename)
                        
                        # Download and save the unique high-resolution image
                        img_data = requests.get(high_res_img_url, stream=True).content
                        with open(img_path, "wb") as f:
                            f.write(img_data)
                        
                        image_paths.append(img_path)  # Save the file path
                        previous_img_url = high_res_img_url  # Update the previous image URL

                    # Now find and interact with thumbnails within the modal to change the main image
                    thumbnail_elements = driver.find_elements(By.XPATH, '//div[@class="ivThumb"]')
                    for thumb_idx, thumb_elem in enumerate(thumbnail_elements):
                        try:
                            # Click on each thumbnail to update the main high-res image
                            thumb_elem.click()
                            time.sleep(1)  # Wait for image to change
                            
                            # Get the updated high-res image URL
                            updated_img_elem = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, '//div[@id="ivLargeImage"]//img[@class="fullscreen"]'))
                            )
                            updated_img_url = updated_img_elem.get_attribute("src")
                            
                            # Check if the updated image is unique
                            if updated_img_url != previous_img_url and updated_img_url:
                                img_filename = f"{sanitized_name}_price_{sanitized_price}_img_{idx + 1}_thumb_{thumb_idx + 1}.jpg"
                                img_path = os.path.join(image_dir, img_filename)
                                
                                # Download and save the updated high-resolution image
                                img_data = requests.get(updated_img_url, stream=True).content
                                with open(img_path, "wb") as f:
                                    f.write(img_data)
                                
                                image_paths.append(img_path)  # Save the file path
                                previous_img_url = updated_img_url  # Update the previous image URL

                        except (NoSuchElementException, ElementClickInterceptedException, TimeoutException, StaleElementReferenceException) as e:
                            print(f"Could not load image for thumbnail at index {thumb_idx}: {e}")

                except (NoSuchElementException, ElementClickInterceptedException, TimeoutException, StaleElementReferenceException) as e:
                    print(f"Could not load image for <li> at index {idx}: {e}")

        except NoSuchElementException:
            print(f"No image thumbnails found for product: {name}")
            image_paths = []

        # try:
        #     # Locate all <li> elements that trigger the high-res image modal
        #     li_elements = driver.find_elements(By.XPATH, '//li[@data-csa-c-action="image-block-main-image-hover"]')
            
        #     # Prepare to store image paths and previous image URL for comparison
        #     image_paths = []
        #     previous_img_url = None
            
        #     # Initialize ActionChains for interactions
        #     actions = ActionChains(driver)
            
        #     for idx, li_elem in enumerate(li_elements):
        #         try:
        #             # Click on the <li> element to open the high-res image modal
        #             li_elem.click()
        #             time.sleep(2)  # Wait for modal to load
                    
        #             # Locate the main high-resolution image inside the modal
        #             high_res_image_elem = WebDriverWait(driver, 10).until(
        #                 EC.presence_of_element_located((By.XPATH, '//div[@id="ivLargeImage"]//img[@class="fullscreen"]'))
        #             )
                    
        #             # Get the initial high-res image URL
        #             high_res_img_url = high_res_image_elem.get_attribute("src")
                    
        #             # Ensure the image is unique by comparing with the previous one
        #             if high_res_img_url != previous_img_url and high_res_img_url:
        #                 img_filename = f"{sanitized_name}_img_{idx + 1}_high_res.jpg"
        #                 img_path = os.path.join(image_dir, img_filename)
                        
        #                 # Download and save the unique high-resolution image
        #                 img_data = requests.get(high_res_img_url, stream=True).content
        #                 with open(img_path, "wb") as f:
        #                     f.write(img_data)
                        
        #                 image_paths.append(img_path)  # Save the file path
        #                 previous_img_url = high_res_img_url  # Update the previous image URL

        #             # Now find and interact with thumbnails within the modal to change the main image
        #             thumbnail_elements = driver.find_elements(By.XPATH, '//div[@class="ivThumb"]')
        #             for thumb_idx, thumb_elem in enumerate(thumbnail_elements):
        #                 try:
        #                     # Click on each thumbnail to update the main high-res image
        #                     thumb_elem.click()
        #                     time.sleep(1)  # Wait for image to change
                            
        #                     # Get the updated high-res image URL
        #                     updated_img_elem = WebDriverWait(driver, 10).until(
        #                         EC.presence_of_element_located((By.XPATH, '//div[@id="ivLargeImage"]//img[@class="fullscreen"]'))
        #                     )
        #                     updated_img_url = updated_img_elem.get_attribute("src")
                            
        #                     # Check if the updated image is unique
        #                     if updated_img_url != previous_img_url and updated_img_url:
        #                         img_filename = f"{sanitized_name}_img_{idx + 1}_thumb_{thumb_idx + 1}.jpg"
        #                         img_path = os.path.join(image_dir, img_filename)
                                
        #                         # Download and save the updated high-resolution image
        #                         img_data = requests.get(updated_img_url, stream=True).content
        #                         with open(img_path, "wb") as f:
        #                             f.write(img_data)
                                
        #                         image_paths.append(img_path)  # Save the file path
        #                         previous_img_url = updated_img_url  # Update the previous image URL

        #                 except (NoSuchElementException, ElementClickInterceptedException, TimeoutException, StaleElementReferenceException) as e:
        #                     print(f"Could not load image for thumbnail at index {thumb_idx}: {e}")

        #         except (NoSuchElementException, ElementClickInterceptedException, TimeoutException, StaleElementReferenceException) as e:
        #             print(f"Could not load image for <li> at index {idx}: {e}")

        # except NoSuchElementException:
        #     print(f"No image thumbnails found for product: {name}")
        #     image_paths = []   
        

        # Append the product data to scrap_data
        scrap_data.append([brand, name, price, return_exchange, expected_delivery, availability, link, description, product_specifications, reviews_data,image_paths])

    # Save the scraped data to a CSV file
    df = pd.DataFrame(scrap_data, columns=["Brand Name", "Product Name", "Price", "Return/Exchange", "Expected Delivery", "Availability", "Product URL", "Description", "Specs", "Reviews", "Product Images"])
    df.to_csv("amazon_products.csv", index=False)
    print("Data saved to amazon_products.csv")

finally:
    # Close the webdriver instance
    driver.quit()
