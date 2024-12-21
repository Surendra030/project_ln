import re
import json
import os




from get_books_url import main_books_fun
from get_img_id import get_images_urls
from save_img_pdf import main_pdf
from get_links import main_load

url = 'https://anyflip.com/explore?q=Eminence%20in%20Shadow'

data = main_books_fun(url)


sindex=1
eindex=71

target_name = "Eminence in Shadow"
data = [
    {**i, 'serial_num': idx}  # Add the 'serial_num' label starting from sindex
    for idx, i in enumerate(data, start=sindex)  # Start enumerate from sindex
    if target_name.lower() in i['title'].lower()  # Filter for "jobless" in title
]

print(data)

constructed_urls = []

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
    print("entering the loop.")
    img_url_data = get_images_urls(obj['href'])
    #saving pdf file to cloud
    temp_title = f"{obj['serial_num']}_{obj['title']}"
    title = sanitize_title(temp_title)

    main_pdf(img_url_data,title)
    main_load(target_name)