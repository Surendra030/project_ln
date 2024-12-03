import time
from get_books_url import main
from get_img_id import get_images_urls
from save_img_pdf import main_pdf
import re

url = "https://anyflip.com/explore?q=Jobless%20reincarnation"

data = main(url)
data = [i for i in data  if "jobless" in i['title'].lower()]
constructed_urls = []
data= data[:21]

def sanitize_title(title):
    
    # Replace any non-alphanumeric character with an underscore
    sanitized = re.sub(r'[^\w\s]', '_', title)
    # Replace any whitespace with an underscore
    sanitized = re.sub(r'\s+', '_', sanitized)
    return sanitized

for index,entity_obj in enumerate(data):
    # Extract the last two segments from the href
    parts = entity_obj['href'].split('/')
    if len(parts) > 3:
        base_code = parts[-3]  # Second-to-last segment
        sub_code = parts[-2]  # Last segment
        # Construct the new URL
        new_url = f"https://online.anyflip.com/{base_code}/{sub_code}/mobile/index.html"
        entity_obj['href'] = new_url

for index,obj in enumerate(data):
    img_url_data = get_images_urls(obj['href'])
    #saving pdf file to cloud
    title = sanitize_title(obj['title'])
    main_pdf(img_url_data,title)
    

    
