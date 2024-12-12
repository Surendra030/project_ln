from utils.make_video_from_pdf import pdf_to_video
from utils.add_audio_to_video import add_audio_every_10_seconds

from mega import Mega
import os


# pdf_to_video(pdf_path, video_path)
# add_audio_every_10_minutes("video.mp4", "audio.mp3", "output_video.mp4")

def login_part(m=None):
    count = 0
    keys = os.getenv("M_TOKEN")
    keys = keys.split("_")
    [email,password] = keys
    if m:
        return m
    else:
        try:
            mega = Mega()
            m = mega.login(email,password)
            return m
        except Exception as e:
            print("login failed training again..")
            count +=1
            if count<=3:
                login_part()


def get_or_create_folder(m,all_folders, main_folder_name):
    """Retrieve an existing folder by main_folder_name or create a new one."""
    try:
        print(f"Checking for the existence of the folder '{main_folder_name}'...")

        folder_handler = next(
            (folder['h'] for folder in all_folders.values() if folder['a']['n'] == main_folder_name and folder['t'] == 1),
            None
        )


        if folder_handler:
            print(f"Folder '{main_folder_name}' already exists. Using the existing folder.")
            return folder_handler
        else:
            print(f"Folder '{main_folder_name}' does not exist. Creating a new folder...")
            folder = m.create_folder(main_folder_name)
            folder_handler = folder.get(main_folder_name)
            print(f"Folder '{main_folder_name}' created successfully.")
            return folder_handler

    except Exception as e:
        print(f"An error occurred while handling the folder: {e}")
        return None



def upload_to_mega(file_path,main_folder):
    m = login_part()
    all_folders = m.get_files()
    folder_handle = get_or_create_folder(m,all_folders,main_folder)
    file_obj = m.upload(file_path,folder_handle)
    file_link = m.get_upload_link(file_obj)

    return file_link



    


def make_video_and_give_link(pdf_file_name,audio_path,output_path,main_folder):
    
    video_path = f"{'temp'}.mp4"
    output_path = f"{output_path}.mp4"
    pdf_result = pdf_to_video(pdf_file_name,video_path)
    if pdf_result:
        video_result = add_audio_every_10_seconds(video_path,audio_path,output_path)
        if video_result:
            video_link = upload_to_mega(output_path,main_folder)
            if video_link:
                return {
                    "file_name : ":pdf_file_name,
                    "link":video_link
                }
            else:
                False
    else:
        print("pdf to video convrtion failed.")