import os
from mega import Mega
from moviepy.video.VideoClip import ImageClip
from moviepy import concatenate_videoclips, AudioFileClip
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from pdf2image import convert_from_path

def login_part():
    """Retrieve Mega credentials and log in."""
    try:
        keys = os.getenv("M_TOKEN")
        if not keys:
            raise ValueError("Mega credentials are not set in the environment variables.")
        
        keys = keys.split("_")
        if len(keys) != 2:
            raise ValueError("Mega credentials are not formatted correctly.")
        
        mega = Mega()
        print("Logging into Mega...")
        m = mega.login(keys[0], keys[1])
        print("Login successful.")
        return m
    except Exception as e:
        print(f"Error during login: {e}")
        return None

def download_file(m, url):
    """Download a file from Mega by URL."""
    try:
        output_name = m.download_url(url)
        return output_name

    except Exception as e:
        print(f"Error downloading file: {e}")
        return None

def pdf_to_video(pdf_path, audio_path, output_path, page_duration=10):
    """Convert a PDF to a video with synchronized audio."""
    try:
        # Convert PDF pages to images
        print(f"Converting PDF to images from {pdf_path}...")
        images = convert_from_path(pdf_path)
        total_pages = len(images)
        total_pages = 25
        print(f"Processing {total_pages} pages from the PDF.")

        # Save images to disk temporarily
        temp_image_files = []
        for page_number, image in enumerate(images):
            image_name = f"page_{page_number + 1}.jpg"
            image.save(image_name, 'JPEG')
            temp_image_files.append(image_name)

        # Create a video clip from the image sequence
        print("Creating video from image sequence...")
        video_clip = ImageSequenceClip(temp_image_files, fps=1 / page_duration)

        # Load the audio file
        print(f"Loading audio from {audio_path}...")
        audio_clip = AudioFileClip(audio_path)

        # Ensure the audio matches the total video duration
        video_clip = video_clip.with_audio(audio_clip.subclipped(0, video_clip.duration))

        # Write the video file
        print(f"Writing the video to {output_path}...")
        video_clip.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

        # Clean up temporary image files
        for temp_file in temp_image_files:
            os.remove(temp_file)

        print(f"Video created successfully: {output_path}")
        return output_path

    except Exception as e:
        print(f"An error occurred: {e}")
def get_or_create_folder(m,all_folders, title):
    """Retrieve an existing folder by title or create a new one."""
    try:
        print(f"Checking for the existence of the folder '{title}'...")

        folder_handler = next(
            (folder['h'] for folder in all_folders.values() if folder['a']['n'] == title and folder['t'] == 1),
            None
        )


        if folder_handler:
            print(f"Folder '{title}' already exists. Using the existing folder.")
            return folder_handler
        else:
            print(f"Folder '{title}' does not exist. Creating a new folder...")
            folder = m.create_folder(title)
            folder_handler = folder.get(title)
            print(f"Folder '{title}' created successfully.")
            return folder_handler

    except Exception as e:
        print(f"An error occurred while handling the folder: {e}")
        return None

def upload_mega(m,output_file_path, folder_title):
    """Upload a video file to Mega."""
    print(f"Uploading video to Mega: {output_file_path}")
    try:
        
        all_folders = m.get_files()

        
        m = login_part()    
            
        
        folder_handler = get_or_create_folder(m,all_folders, folder_title)
        m.upload(output_file_path,folder_handler)
        print("Upload completed successfully.")
    
    except Exception as e:
        print(f"Error uploading file: {e}")
    finally:
        os.remove(output_file_path)
def start(m,pdf_url, audio_path, output_path, main_folder_path):
    print("Starting process...")

    # Login to Mega
    if not m:
        m = login_part()
        return

    # Download the PDF file
    pdf_path = download_file(m, pdf_url)
    if not pdf_path:
        print("Failed to download PDF. Exiting process.")
        return

    
    output_path = f"{output_path}.mp4"
    # Create the video
    output_path = pdf_to_video(pdf_path, audio_path, output_path)

    # Optionally upload to Mega
    upload_mega(m,output_path, main_folder_path)

