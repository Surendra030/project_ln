import requests
from PIL import Image
from io import BytesIO
from fpdf import FPDF
from mega import Mega
import os
import shutil
import unicodedata
import pikepdf  # Library for compressing PDFs


# Function to remove or replace unsupported characters in text
def sanitize_text(text):
    """Sanitize text by removing unsupported characters and preserving basic formatting."""
    sanitized_lines = []
    for line in text.splitlines():
        sanitized_line = ''.join(c if unicodedata.category(c) in ('Lu', 'Ll', 'Nd', 'Pc', 'Zs', 'Zp') else ' ' for c in line)
        if sanitized_line.strip():
            sanitized_lines.append(sanitized_line.strip())
    return '\n'.join(sanitized_lines)


def process_images(images, paper_name, pdf, output_folder):
    """Download images, save them in an images folder, and add them directly to the PDF."""
    images_folder = os.path.join(output_folder, "images")
    os.makedirs(images_folder, exist_ok=True)  # Create the images folder inside the output folder

    for index, image in enumerate(images):
        img_url = image["src"]

        try:
            # Fetch the image from the URL
            response = requests.get(img_url)
            response.raise_for_status()

            # Open and save the image locally
            img = Image.open(BytesIO(response.content))
            img_path = os.path.join(images_folder, f"{paper_name}_page{index + 1}.jpg")
            img.save(img_path)

            # Add a new page for the image in the PDF
            pdf.add_page()
            pdf.image(img_path, x=10, y=10, w=180)  # Adjust image size
        except Exception as e:
            print(f"Failed to process image at {img_url}: {e}")
            continue  # Skip to the next image in case of an error

    # Save the PDF to the output folder
    output_pdf_path = os.path.join(output_folder, f"{paper_name}.pdf")
    pdf.output(output_pdf_path)

    return output_pdf_path


# Function to upload the PDF and images folder to Mega
def upload_to_mega(folder_path, title, email, password):
    """Upload the folder containing PDF and images to Mega Cloud."""
    mega = Mega()
    print("Establishing connection to Mega...")
    m = mega.login(email, password)

    # Create a folder in Mega with the title name
    print(f"Creating folder '{title}' in Mega cloud...")
    
    mega_folder = m.create_folder(f"three_{title}")
    

    # Upload all files and subfolders from the given folder path to the Mega folder
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            print(f"Uploading {file_path} to Mega...")
            m.upload(file_path, mega_folder[0])  # Upload file to the Mega folder

    print(f"Upload of '{title}' completed.")

    # Cleanup after uploading to Mega Cloud
    shutil.rmtree(os.path.join(folder_path, "images"))  # Remove the images folder
    pdf_path = os.path.join(folder_path, f"{title}.pdf")
    if os.path.exists(pdf_path):
        os.remove(pdf_path)  # Remove the PDF file
    print(f"Cleaned up local data for {title}.")


# Main function to generate the PDF
def main_pdf(data, title, index):
    """Generate a PDF and save data into a structured folder."""
    # Create the output folder for this title
    output_folder = f"{index}_{title}"
    os.makedirs(output_folder, exist_ok=True)

    paper_list = []
    for list_item_obj in data:
        for key in list_item_obj:
            paper_list.append(key)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=5)

    # Process images from each paper and add to the PDF
    for i, paper_name in enumerate(paper_list):
        images = data[i].get(paper_name, [])
        if images:
            process_images(images, paper_name, pdf, output_folder)

    # Save the final PDF
    pdf_output_path = os.path.join(output_folder, f"{title}.pdf")
    pdf.output(pdf_output_path)

    # Upload the entire folder to Mega Cloud
    email = "afg154010@gmail.com" 
    password = "megaMac02335!"
    upload_to_mega(output_folder, title, email, password)

    print(f"PDF and images saved in {output_folder}")
