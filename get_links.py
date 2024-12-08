import json
from mega import Mega
import os


def main_load():
    
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
    print(f"Found {len(files)} files.")

    # Prepare a dictionary to store the file names and shareable links
    file_links = {}

    print("Generating shareable links for the files...")
    
    def get_folder_name(parent_id,file_dict):

        for i, file in enumerate(file_dict.values(), start=1):
            if file[i] == parent_id:
                return file['a']['n']
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
                        file_url = m.get_link(file)  # Generate shareable link
                        file_links[file_name] = {
                            "file_name": file_name,
                            "folder_name":parent_folder_name,
                            "sharable_link": file_url
                        }
                    except Exception as e:
                        print(f"Error generating link for file: {file_name}. Error: {e}")
                
                else:
                    print(f"Skipping file (missing file ID): {file_name}")
            
            # If it's a folder (t > 0), recursively call the function to explore its contents
            elif file['t'] > 0:  # It's a folder
                print(f"{i}/{l} : Entering folder: {file_name}")
                
                # To retrieve files from a folder, we should use the correct Mega method that handles folder IDs
                try:
                    # Assuming you have a method in Mega class to fetch files inside a specific folder
                    folder_files = m.get_files()  # Modify this if Mega has a method to get files from a folder.
                    
                    # If you have a method to fetch files in a folder, you can pass file_id to it
                    # For example: folder_files = m.get_files(file_id) 

                    get_shareable_links(folder_files)  # Recursively get links from the folder's contents
                except Exception as e:
                    print(f"Error processing folder: {file_name}. Error: {e}")

                
            # Print progress every 100 files
            if i % 100 == 0:
                print(f"Processed {i} files...")

    # Start by getting links for the root files and folders
    get_shareable_links(files)

    # Save the dictionary to a JSON file
    print("Saving shareable links to 'file_links.json'...")
    with open('file_links.json', 'w') as json_file:
        json.dump(file_links, json_file, indent=4)

    m.upload("file_links.json")
    print("File links have been successfully saved to 'file_links.json'.")
