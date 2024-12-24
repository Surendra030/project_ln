import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import json
import time
import re

# Set up Chrome options
options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")
options.add_argument("--headless")  # Uncomment for headless mode

# Specify the path to your chromedriver
chromedriver_path = r"chromedriver"
service = Service(executable_path=chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)

def main_books_fun(url):
    
    # Navigate to the website
    driver.get(url)

    # Wait for the initial page to load
    time.sleep(5)  # Adjust the wait time based on your internet speed

    # Infinite scroll logic
    previous_item_count = 0

    # count = 1000 # In case for non-specified no of files.
    count = 10
    while count>=0:
        # Scroll down to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Wait for new content to load
        count -=1
        # Get the current count of water-items
        items = driver.find_elements(By.CSS_SELECTOR, ".water-item")
        current_item_count = len(items)

        # Break the loop if no new items are loaded
        if current_item_count == previous_item_count:
            break
        previous_item_count = current_item_count

    

    # Extract all items with the class "water-item"
    extracted_data = []

    def extract_volume_number(title):
        # Use a regex to find the pattern "volume <number>" or "vol <number>"
        match = re.search(r'\bvol(?:ume)?\s*(\d+)', title, re.IGNORECASE)
        if match:
            return int(match.group(1))  # Extract the number as an integer
        return None  # Return None if no match is found

    # Loop through each item and extract href and title
    for item in items:
        try:
            anchor_tag = item.find_element(By.CSS_SELECTOR, "a.water-item-link")
            image_tag = item.find_element(By.CSS_SELECTOR, "img.water-book-img")
            
            href = anchor_tag.get_attribute("href")
            title = image_tag.get_attribute("alt")
            
             #Append the extracted data as a dictionary
            extracted_data.append({
                "href": href,
                "title": title
            })

            # Deduplicate based on title
            title_seen = set()
            deduplicated_data = []

            for item in extracted_data:
                volume_num = extract_volume_number(item['title'])
                if volume_num not in title_seen:
                    title_seen.add(item['title'])
                    deduplicated_data.append(item)



        except Exception as e:
            print(f"Error processing an item: {e}")
            continue
    print("data extracted from url..")
    driver.quit()

    return deduplicated_data


    



