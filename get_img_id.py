from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# Set up Chrome options
options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")
options.add_argument("--headless")
options.add_argument("--no-sandbox")


# Specify the path to your chromedriver
chromedriver_path = r"chromedriver"

# Output data

# Create a set to keep track of unique image URLs to avoid duplicates

def get_images_urls(url):
    # Try to open the main URL
    try:
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(url)
        print("Loading for 5 seconds...")
        time.sleep(5)  # Allow time for the page to load
        output_data = []

        # Find total pages (from #currentPageIndexTextField)
        page_index_element = driver.find_element(By.ID, "currentPageIndexTextField")
        page_num_text = page_index_element.get_attribute("value")  # e.g., "1/100"
        total_pages = int(page_num_text.split("/")[-1])  # Extract total number of pages
        target_pages = (total_pages + 1) // 2  # Adjust target page count for two parts per page
        right_arrow = driver.find_element(By.CSS_SELECTOR, ".flip_button_right")

        # Loop through pages (limit to 5 pages for example)
        for page in range(target_pages):
            page_mask_num = page_index_element.get_attribute("value").split("/")[0].split("-")  # e.g., "1/100"
            # Create a list for the current paper
            paper_data = []

            # Find all image elements on the page
            
            for i in page_mask_num:
                num = int(i)
                    # Extract image URLs from both page masks
                img1_element = driver.find_element(By.CSS_SELECTOR, f"#pageMask{num} img")

                    # Get the src (image URL) attribute for both images
                img1_src = img1_element.get_attribute("src")
                img1_alt = img1_element.get_attribute("alt")
                img1_id = img1_element.get_attribute('id')

                if img1_src:
                        # Prepare the image data for this paper
                    img_data = {
                            "src": img1_src,
                            "alt": img1_alt,
                            "id": img1_id
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
        print("all data extraction completed..")
