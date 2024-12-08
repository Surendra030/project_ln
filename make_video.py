import os
from mega import Mega
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip
from pdf2image import convert_from_path
import time


def login_part():
    keys = os.getenv("M_TOKEN")
    keys = keys.split("_")
    return keys

def download_file_from_mega(url, output_path):
    """
    Download a file from Mega.nz using the Mega.py library.
    
    Args:
        url (str): Mega.nz file URL.
        output_path (str): Path to save the downloaded file.
    """
    print(f"Downloading file from Mega URL")
    
    # Initialize Mega API
    mega = Mega()
    keys = login_part()
    # Log in anonymously
    m = mega.login(keys[0],keys[1])
    
    # Step 1: Attempt to download the file
    attempt = 0
    while attempt < 3:  # Retry mechanism (max 3 attempts)
        try:
            print("Starting download...")
            file = m.download_url(url, dest_filename=output_path)
            print(f"File downloaded successfully to {output_path}")
            return output_path
        except Exception as e:
            print(f"Error downloading file (Attempt {attempt+1}): {e}")
            attempt += 1
            time.sleep(5)  # Wait before retrying
    print(f"Failed to download file after {attempt} attempts.")
    return None
def pdf_to_video(pdf_url, audio_url, output_path, page_duration=10, max_pages=20):
    """
    Convert a PDF to a video with page flip effect and audio on page change.
    
    Args:
        pdf_url (str): URL of the PDF file to download.
        audio_url (str): URL of the audio file to download.
        output_path (str): Path to save the output video.
        page_duration (int): Duration for each page in seconds.
        max_pages (int): Maximum number of pages to process.
    """
    # Step 1: Download PDF file from Mega
    print("Downloading PDF file...")
    pdf_file_path = "downloaded_pdf.pdf"
    download_file_from_mega(pdf_url, pdf_file_path)
    
    # Step 2: Convert PDF pages to images
    print(f"Converting PDF to images...")
    images = convert_from_path(pdf_file_path, first_page=1, last_page=max_pages)
    total_pages = len(images)
    print(f"Processing {total_pages} pages from the PDF.")

    image_clips = []
    for page_number, image in enumerate(images):
        print(f"Processing page {page_number + 1} of {total_pages}...")
        # Save each page as a temporary image
        image_name = f"page_{page_number + 1}.jpg"
        image.save(image_name, 'JPEG')
        
        # Add the image as a video frame with duration using with_duration
        clip = ImageClip(image_name).with_duration(page_duration)
        image_clips.append(clip)
        
        # Clean up the temporary image file
        os.remove(image_name)
        print(f"Processed page {page_number + 1} of {total_pages}.")

    # Step 3: Download audio from Mega
    print("Downloading audio file...")
    audio_file_path = "audio_downloaded.mp3"
    download_file_from_mega(audio_url, audio_file_path)
    
    # Step 4: Add audio for page change
    try:
        print("Loading audio file...")
        audio_clip = AudioFileClip(audio_file_path)
    except Exception as e:
        print(f"Error loading audio file: {e}")
        return
    
    audio_duration = audio_clip.duration / len(image_clips)  # Split audio to match the pages' duration
    print(f"Audio duration per page: {audio_duration} seconds.")

    # Create audio subclips for each image page
    audio_intervals = []
    for i in range(len(image_clips)):
        start_time = i * audio_duration
        end_time = (i + 1) * audio_duration
        audio_intervals.append(audio_clip.subclipped(start_time, end_time))

    # Associate each image clip with the corresponding audio subclip
    audio_clips = [clip.with_audio(audio_intervals[i]) for i, clip in enumerate(image_clips)]

    # Step 5: Concatenate the clips
    print("Concatenating video clips...")
    final_video = concatenate_videoclips(audio_clips, method="compose")

    # Step 6: Write the video to the output path
    print(f"Writing the video to {output_path}...")
    final_video.write_videofile(output_path, fps=24)
    print(f"Video created successfully: {output_path}")


def upload_mega(o_path):
    """
    Upload the generated video to Mega.nz.
    
    Args:
        o_path (str): Path to the video file.
    """
    print(f"Uploading video to Mega: {o_path}")
    mega = Mega()
    keys = login_part()
    m = mega.login(keys[0],keys[1])
    title = "video_files"
    folder = m.create_folder(title)
    print(folder)
    folder_handler = folder.get(title)
    m.upload(o_path, folder_handler)
    print("Uploading completed.")


def start():
    print("Starting process...")
    pdf_url = "https://mega.nz/file/KMQH0T6J#01dkodTbqfwtZF7oibEgASkp7rHryvzyKlEsLFhgxN0"  # PDF file URL
    audio_url = "https://mega.nz/file/ScYViJaZ#U6DHMdMBgAF1ngVO3bL244QlNJq65UCuDgygL0vnSe4"
    output_path = "output.mp4"  # Path to save the output video

    # Call the function to create the video
    pdf_to_video(pdf_url, audio_url, output_path)

    # Optionally upload to Mega
    upload_mega(output_path)
# Example usage
    
