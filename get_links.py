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

    def save_to_db(file_link, title):
        mongo_url = os.getenv("MONGO_URL")

# Create a MongoDB client
        client = MongoClient(mongo_url)

        db = client["file_links"]  # Database name
        collection = db["links_coll"] 
    # Create the document structure
        document = {
            "novel_title": title,
            "sharable_link": file_link
        }
        
        # Insert the document into the collection
        try:
            collection.insert_one(document)
            print(f"Document for '{title}' saved successfully.")
        except Exception as e:
            print(f"Error saving document for '{title}': {e}")


    title = f"{title}_links"

    # Save the dictionary to a JSON file
    print(f"Saving shareable links to '{title}.json'...")
    
    with open(f'{title}.json', 'w') as json_file:
        json.dump(file_links, json_file, indent=4)
    
    folder_name = 'meta_data'
    
    folder = [item for item in files.values() if item['t'] >0 and item ['a']['n'] == folder_name]
    folder_handle = folder[0]["h"]
    file = m.upload(f"{title}.json",folder_handle)
    
    file_link =  m.get_upload_link(file)
    if file_link:
        save_to_db(file_link,title)

    print("File links have been successfully saved to 'file_links.json'.")


