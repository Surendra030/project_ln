import json
from mega import Mega
import os
from pymongo import MongoClient


def main_load(title):
    
    # Log in to Mega account
    print("Logging into Mega account...")
    mega = Mega()
    keys = os.getenv("M_TOKEN")
    keys = keys.split("_")
    email =keys[0] # Replace with your Mega email
    password = keys[1]  # Replace with your Mega password
    m = mega.login(email, password)
    print("Logged in successfully!")


    # Get a list of all files in your Mega account
    print("Retrieving files from your Mega account...")
    files = m.get_files()

    # Prepare a dictionary to store the file names and shareable links
    file_links = {}

    print("Generating shareable links for the files...")
    
    def get_folder_name(parent_id, file_dict):
        for file in file_dict.values():
            if file['h'] == parent_id:  # Use 'h' for the file ID
                return file['a']['n']  # Return the folder name from the 'a' dictionary
        return None  
    # Function to get shareable links for all files recursively, including files in subfolders

    def get_shareable_links(file_dict):
        l = len(file_dict)

        for i, file in enumerate(file_dict.values(), start=1):
            file_name = file['a']['n']  # The file name
            file_id = file['h']  # The file ID
            
            # If it's a file, 
            if file['t'] == 0: 
                if file_id:
                    
                    parent_folder_id = file['p']
                    parent_folder_name = get_folder_name(parent_folder_id,file_dict)
                    try:
                        file_url = m.export(file_name)  # Generate shareable link
                        file_links[file_name] = {
                            "file_name": file_name,
                            "folder_name":parent_folder_name,
                            "sharable_link": file_url
                        }
                    except Exception as e:
                        print(f"Error generating link for file: {file_name}. Error: {e}")
                else:
                    print(f"Skipping file (missing file ID): {file_name}")
            

                
            # Print progress every 100 files
            if i % 100 == 0:
                print(f"Processed {i} files...")

    # Start by getting links for the root files and folders
    get_shareable_links(files)

