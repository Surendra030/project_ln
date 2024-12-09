import os
from mega import Mega
from moviepy.video.VideoClip import ImageClip
from moviepy import concatenate_videoclips, AudioFileClip
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
        print(output_name,"\n",os.listdir())
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
        print(f"Processing {total_pages} pages from the PDF.")

        # Prepare image clips
        image_clips = []
        for page_number, image in enumerate(images):
            image_name = f"page_{page_number + 1}.jpg"
            image.save(image_name, 'JPEG')

            # Add the image as a video frame with duration
            clip = ImageClip(image_name).set_duration(page_duration)
            image_clips.append(clip)

            # Clean up the temporary image file
            os.remove(image_name)

        # Load the audio file
        print(f"Loading audio from {audio_path}...")
        audio_clip = AudioFileClip(audio_path)

        # Split audio to match page durations
        audio_duration = audio_clip.duration / len(image_clips)
        print(f"Audio duration per page: {audio_duration:.2f} seconds.")

        audio_intervals = [
            audio_clip.subclipped(i * audio_duration, (i + 1) * audio_duration)
            for i in range(len(image_clips))
        ]

        # Associate each image clip with the corresponding audio interval
        video_clips = [
            clip.set_audio(audio_intervals[i]) for i, clip in enumerate(image_clips)
        ]

        # Concatenate the clips
        print("Concatenating video clips...")
        final_video = concatenate_videoclips(video_clips, method="compose")

        # Write the video to the output path
        print(f"Writing the video to {output_path}...")
        final_video.write_videofile(output_path, fps=24)
        print(f"Video created successfully: {output_path}")
        
        return output_path
    
    except Exception as e:
        print(f"An error occurred during processing: {e}")

def get_or_create_folder(m,all_folders, title):
    """Retrieve an existing folder by title or create a new one."""
    try:
        print(f"Checking for the existence of the folder '{title}'...")

        folder_handler = next(
            (folder for folder in all_folders.values() if folder['a']['n'] == title and folder['t'] == 1), None
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

def upload_mega(output_file_path, folder_title):
    """Upload a video file to Mega."""
    print(f"Uploading video to Mega: {output_file_path}")
    try:
        m = login_part()
        all_folders = m.get_files()

        if not m:
            print("Failed to log in to Mega. Aborting upload.")
            return
        
        folder_handler = get_or_create_folder(m,all_folders, folder_title)
        m.upload(output_file_path, folder_handler)
        print("Upload completed successfully.")
    except Exception as e:
        print(f"Error uploading file: {e}")

def start(pdf_url, audio_url, output_path, main_folder_path):
    print("Starting process...")

    # Login to Mega
    m = login_part()
    if not m:
        print("Failed to log in to Mega. Exiting process.")
        return

    # Download the PDF file
    pdf_path = download_file(m, pdf_url)
    if not pdf_path:
        print("Failed to download PDF. Exiting process.")
        return

    # Download the audio file
    audio_path = download_file(m, audio_url)
    if not audio_path:
        print("Failed to download audio. Exiting process.")
        return

    # Create the video
    output_path = pdf_to_video(pdf_path, audio_path, output_path)

    # Optionally upload to Mega
    upload_mega(output_path, main_folder_path)

