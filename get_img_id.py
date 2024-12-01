import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import json
import time

# Set up Chrome options
options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")
options.add_argument("--headless")  # Uncomment for headless mode

# Specify the path to your chromedriver
chromedriver_path = r"chromedriver"
service = Service(executable_path=chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)

# Output data
output_data = []

# Create a set to keep track of unique image URLs to avoid duplicates
unique_image_urls = set()

def get_images_urls(url):
    # Try to open the main URL
    try:
        driver.get(url)
        print("Loading for 5 seconds...")
        time.sleep(5)  # Allow time for the page to load

        # Find total pages (from #currentPageIndexTextField)
        page_index_element = driver.find_element(By.ID, "currentPageIndexTextField")
        page_num_text = page_index_element.get_attribute("value")  # e.g., "1/100"
        total_pages = int(page_num_text.split("/")[-1])  # Extract total number of pages
        target_pages = (total_pages + 1) // 2  # Adjust target page count for two parts per page
        right_arrow = driver.find_element(By.CSS_SELECTOR, ".flip_button_right")

        # Loop through pages (limit to 5 pages for example)
        for page in range(target_pages):

            # Create a list for the current paper
            paper_data = []

            # Find all image elements on the page
            image_elements = driver.find_elements(By.CSS_SELECTOR, "div.side-image img")
            
            for img in image_elements:
                img_src = img.get_attribute("src")
                img_alt = img.get_attribute("alt")
                img_id = img.get_attribute("id")

                # Skip the image if it is already in the set of unique URLs
                if img_src in unique_image_urls:
                    continue  # Don't add the image if it was already added to another paper

                # Add the image URL to the set of unique URLs
                unique_image_urls.add(img_src)

                # Prepare the image data for this paper
                img_data = {
                    "src": img_src,
                    "alt": img_alt,
                    "id": img_id
                }

                # Append image data to the paper
                paper_data.append(img_data)

            # Only add the paper if it has unique images
            if paper_data:
                output_data.append({"paper" + str(page + 1): paper_data})

            # Click the right arrow to move to the next page
            if page < target_pages - 1:  # Avoid clicking after the last page
                right_arrow.click()
                time.sleep(3)  # Wait for the page to load after the click
        print("Image URLs extracted from url")
        driver.quit()
        return output_data

        

    finally:
        if driver is None:
        # Quit the driver
            driver.quit()
