import time
from get_books_url import main_books_fun
from get_img_id import get_images_urls
from save_img_pdf import main_pdf
from make_video import start
from get_links import main_load
from mega import Mega
import os
import re
import json

mega = Mega()

def login_part(mega):
    """Login to Mega using environment variables."""
    try:
        print("Logging in to Mega...")
        keys = os.getenv("M_TOKEN")
        if not keys:
            raise ValueError("Mega credentials are not set in environment variables.")
        
        keys = keys.split("_")
        if len(keys) != 2:
            raise ValueError("Mega credentials are incorrectly formatted in environment variables.")
        
        m = mega.login(keys[0], keys[1])
        print("Logged in to Mega successfully.")
        return m
    except Exception as e:
        print(f"Error during Mega login: {e}")
        return None

def download_file(m, file_name):
    try:
        all_folders = m.get_files()

        # Find the folder
        file = next(
            (item for item in all_folders.values() if item['a']['n'] == file_name and item['t'] == 0), 
            None
        )
        print(file)
        file_link = m.export(file)
        if not file:
            print(f"Folder '{file_name}' not found.")
            return None

        print(f"Folder '{file_name}' found. Listing all files in this folder:")
        m.download(file_link)
        
        return file_name

    except Exception as e:
        print(f"Error downloading file '{file_name}': {e}")
        return None

def process_links(m, links_data, audio_file):
    """Process the links data."""
    try:
        if not m:
            raise ConnectionError("Mega instance is not initialized.")
        
        print(f"Processing {len(links_data)} links...")
        for key, snippet in links_data.items():
            file_name = snippet.get("file_name", "No file_name found")
            link = snippet.get("sharable_link", "No link available")
            
            exten = file_name.split(".")[-1]
            output_path = file_name.split(".")[0]
            main_folder_name = output_path.split("_")[1] if "_" in output_path else "default_folder"
            
            print(f"Processing file: {file_name}, Type: {exten}")
            
            if exten == 'pdf' and "compress" not in output_path:
                print(f"Starting video creation for {file_name}...")
                start(link,file_name, audio_file, output_path, main_folder_name)
            else:
                print(f"Skipping file: {file_name}, as it does not meet criteria.")
    
    
    except Exception as e:
        print(f"Error processing links: {e}")

def main():
    """Main function to execute the workflow."""
    file_name = "file_links.json"
    audio_file = "audio.mp3"

    # Login to Mega
    m = login_part(mega)
    if not m:
        print("Failed to log in to Mega. Exiting.")
        return

    # Download required files
    downloaded_file = download_file(m, file_name)
    downloaded_audio = download_file(m, audio_file)

    if not downloaded_file or not downloaded_audio:
        print("Required files are missing. Exiting.")
        return

    # Load links data
    try:
        with open(downloaded_file, 'r', encoding='utf-8') as f:
            links_data = json.load(f)
        # Limit to a subset of data for testing
        links_data = {k: links_data[k] for k in list(links_data)[:2]}
    except Exception as e:
        print(f"Error reading links data: {e}")
        return

    # Process the links
    process_links(m, links_data, downloaded_audio)

if __name__ == "__main__":
    main()



# url = "https://anyflip.com/explore?q=Jobless%20reincarnation"

# data = main_books_fun(url)






# sindex=61
# eindex=71

# target_name = "jobless"

# data = [
#     {**i, 'serial_num': idx}  # Add the 'serial_num' label starting from sindex
#     for idx, i in enumerate(data, start=sindex)  # Start enumerate from sindex
#     if target_name in i['title'].lower()  # Filter for "jobless" in title
# ]


# data = data[sindex:eindex]
# constructed_urls = []

# def sanitize_title(title):
    
    
#     # Replace any non-alphanumeric character with an underscore
#     sanitized = re.sub(r'[^\w\s]', '_', title)
#     # Replace any whitespace with an underscore
#     sanitized = re.sub(r'\s+', '_', sanitized)
#     return sanitized

# for index,entity_obj in enumerate(data):
#     # Extract the last two segments from the href
#     parts = entity_obj['href'].split('/')
#     if len(parts) > 3:
#         base_code = parts[-3]  # Second-to-last segment
#         sub_code = parts[-2]  # Last segment
#         # Construct the new URL
#         new_url = f"https://online.anyflip.com/{base_code}/{sub_code}/mobile/index.html"
#         entity_obj['href'] = new_url

# for index,obj in enumerate(data):
#     img_url_data = get_images_urls(obj['href'])
#     #saving pdf file to cloud
#     temp_title = f"{obj['serial_num']}_{obj['title']}"
#     title = sanitize_title(temp_title)

#     main_pdf(img_url_data,title)
#     main_load(target_name)

