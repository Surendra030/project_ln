import os
from mega import Mega
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip
from pdf2image import convert_from_path


def login_part():
    keys = os.getenv("M_TOKEN")
    keys = keys.split("_")
    return keys

import os

def pdf_to_video(pdf_path, audio_path, output_path, page_duration=10):
    
    try:
        # Step 1: Convert PDF pages to images and dynamically determine the total pages
        print(f"Converting PDF to images from {pdf_path}...")
        images = convert_from_path(pdf_path)
        total_pages = len(images)
        print(f"Processing {total_pages} pages from the PDF.")

        # Prepare image clips
        image_clips = []
        for page_number, image in enumerate(images):
            print(f"Processing page {page_number + 1} of {total_pages}...")
            image_name = f"page_{page_number + 1}.jpg"
            image.save(image_name, 'JPEG')

            # Add the image as a video frame with duration
            clip = ImageClip(image_name).with_duration(page_duration)
            image_clips.append(clip)

            # Clean up the temporary image file
            os.remove(image_name)
            print(f"Processed page {page_number + 1} of {total_pages}.")

        # Step 2: Load the audio file
        print(f"Loading audio from {audio_path}...")
        try:
            audio_clip = AudioFileClip(audio_path)
        except Exception as e:
            print(f"Error loading audio file: {e}")
            return

        # Step 3: Split audio to match page durations
        audio_duration = audio_clip.duration / len(image_clips)
        print(f"Audio duration per page: {audio_duration} seconds.")

        audio_intervals = [
            audio_clip.subclipped(i * audio_duration, (i + 1) * audio_duration)
            for i in range(len(image_clips))
        ]

        # Associate each image clip with the corresponding audio interval
        video_clips = [
            clip.set_audio(audio_intervals[i]) for i, clip in enumerate(image_clips)
        ]

        # Step 4: Concatenate the clips
        print("Concatenating video clips...")
        final_video = concatenate_videoclips(video_clips, method="compose")

        # Step 5: Write the video to the output path
        print(f"Writing the video to {output_path}...")
        final_video.write_videofile(output_path, fps=24)
        print(f"Video created successfully: {output_path}")

    except Exception as e:
        print(f"An error occurred during processing: {e}")

# Assuming `m` is the Mega instance and `title` is the folder name
def get_or_create_folder(m, title):
    """
    Retrieves an existing folder by title or creates a new one if it doesn't exist.

    Args:
        m: Mega instance (logged-in session).
        title (str): The name of the folder to find or create.

    Returns:
        dict: The folder handler (metadata of the folder).
    """
    try:
        print(f"Checking for the existence of the folder '{title}'...")
        # Fetch the list of folders
        all_folders = m.get_files()

        # Look for the folder with the given title
        folder_handler = next(
            (folder for folder in all_folders.values() if folder['a']['n'] == title and folder['t'] == 1), None
        )

        if folder_handler:
            print(f"Folder '{title}' already exists. Using the existing folder.")
            return folder_handler
        else:
            print(f"Folder '{title}' does not exist. Creating a new folder...")
            # Create a new folder and return its handler
            folder = m.create_folder(title)
            folder_handler = folder.get(title)
            print(f"Folder '{title}' created successfully.")
            return folder_handler

    except Exception as e:
        print(f"An error occurred while handling the folder: {e}")
        return None



def upload_mega(o_path,folder_title):
   
    print(f"Uploading video to Mega: {o_path}")
    mega = Mega()
    keys = login_part()
    m = mega.login(keys[0],keys[1])
    folder_handler = get_or_create_folder(m,folder_title)
    m.upload(o_path, folder_handler)
    print("Uploading completed.")


def start(pdf_url,audio_url,output_path,main_folder_path):
    print("Starting process...")
    
    # Call the function to create the video
    pdf_to_video(pdf_url, audio_url, output_path,main_folder_path)

    # Optionally upload to Mega
    upload_mega(output_path,main_folder_path)
# Example usage
    
