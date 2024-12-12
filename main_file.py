import time
from get_books_url import main_books_fun
from get_img_id import get_images_urls
from save_img_pdf import main_pdf
from full_video import make_video_and_give_link
from get_links import main_load
from mega import Mega
from pymongo import MongoClient
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

def download_file(m,file_links):

    if type(file_links) == list:
        try:
            file_name = m.download_url(file_links[0])
            audio_file_name = m.download_url(file_links[1])
            return [file_name,audio_file_name]
        except Exception as e:
            print("Error downloading meta data :",e)
    else:
        try:
            
            file_name = m.download_url(file_links)
        except Exception as e:
            print(f"Error downloading Key files : ",e)


def download_pdf_file(m,file_link):
    
    if file_link:
        try:
            
            file_name = m.download_url(file_link)
            return file_name
        except Exception as e:
            print(f"Error downloading Key files : \n",e)




def save_links_to_db(lst,collection_name):
    collection_name = f"{collection_name}_video_links"
    mongourl = os.getenv("MONGO_URL")
    try:
        client = MongoClient(mongourl)
    except Exception as e:
        print("Error connecting to db.")
    
    db = client['file_links']
    collection = db[collection_name]

    if lst:
        try:
            collection.insert_many(lst)
            print(f"Successfully inserted {len(lst)} documents into the collection.")
        except Exception as e:
            print("Error uploading file to db.")
    else:
        print("No data to insert")


def process_links(m,mega, links_data, audio_file_name):
    """Process the links data."""

    video_files_data = []
    try:
        if not m:
            m = login_part(mega)

        o_path = ""
        for key, snippet in links_data.items():
            file_name = snippet.get("file_name", "No file_name found")
            link = snippet.get("sharable_link", "No link available")
            
            try:
                if link:
                    pdf_file_name = download_pdf_file(m,link)
            except Exception as e:
                print(f"Downloading failed for pdf file : {pdf_file_name}\n",e)  
            
            if pdf_file_name:
                exten = file_name.split(".")[-1]
                output_path = file_name.split(".")[0]
                o_path  = output_path
                main_folder_name = output_path.split("_")[1] if "_" in output_path else "temp_folder"
                
                
                if exten == 'pdf' and "compress"  in output_path:
                    video_file_data_obj = make_video_and_give_link(pdf_file_name,audio_file_name,output_path,main_folder_name)
                    if video_file_data_obj: video_files_data.append(video_file_data_obj)
            else:
                print(f"pdf file not found : {pdf_file_name}")
        if len(video_files_data) > 0:
            return [video_files_data,o_path]
        else:
            print("Video files data is Empty.")

    except Exception as e:
        print(f"Error processing links: {e}")
        

def get_shrable_links_db():
    mongo_url = os.getenv("MONGO_URL")
    client = MongoClient(mongo_url)
    db = client["file_links"]
    coll = db['links_coll']

    json_file_link = coll.find_one({"novel_title":"jobless_links"})
    audio_file_link = coll.find_one({"file_name":"audio.mp3"})
    
    
    # Fetch sharable links for specific documents
    json_file_link = coll.find_one({"novel_title": "jobless_links"}, {"_id": 0, "sharable_link": 1})
    audio_file_link = coll.find_one({"file_name": "audio.mp3"}, {"_id": 0, "sharable_link": 1})

    # Extracting only the links
    json_sharable_link = json_file_link.get("sharable_link") if json_file_link else None
    audio_sharable_link = audio_file_link.get("sharable_link") if audio_file_link else None
    
    try:
    # Closing Connection
        client.close()
    except Exception as e:
        print("Error trying to close connection.")
    
    return [json_sharable_link,audio_sharable_link]

def main():
    """Main function to execute the workflow."""
    
    # Login to Mega
    file_links = get_shrable_links_db()
    m = login_part(mega)
    if not m:
        print("Failed to log in to Mega. Exiting.")
        return

    # Download required meta files
    downloaded_files_name = download_file(m,file_links)

    if not downloaded_files_name:
        print("Required files are missing.")
        return
    else:
        print("Required files are Available.",downloaded_files_name)

    # Load links data
    try:
        with open(downloaded_files_name[0], 'r', encoding='utf-8') as f:
            links_data = json.load(f)
        # Limit to a subset of data for testing
        links_data = {k: links_data[k] for k in list(links_data)[23:46]}
    except Exception as e:
        print(f"Error reading links data: {e}")
        return

    # Process the links
    videos_data = process_links(m,mega, links_data, downloaded_files_name[1])

    if videos_data : print("All Pdf's converted to Videos")

    # if videos_data:
    #     try:

    #         save_links_to_db(videos_data[0],videos_data[1])
    #     except Exception as e:
    #         print("Error saving data to DB.",e) 

if __name__ == "__main__":
    main()
