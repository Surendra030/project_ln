import requests
from PIL import Image
from io import BytesIO
from fpdf import FPDF
import json
import dropbox
import os

# Function to download and save images
def download_images(images, paper_name):
    image_paths = []
    for index, image in enumerate(images):
        img_url = image["src"]
        response = requests.get(img_url)
        img = Image.open(BytesIO(response.content))
        img_path = f"{paper_name}_page{index + 1}.jpg"
        img.save(img_path)
        image_paths.append(img_path)
    return image_paths

# Function to create PDF from images
def create_pdf(image_paths, title):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=5)
    
    for image_path in image_paths:
        pdf.add_page()
        pdf.image(image_path, x=10, y=10, w=180)  # Adjust the image size as needed
    
    # Save the PDF locally temporarily
    pdf_output_path = f"{title}.pdf"
    pdf.output(pdf_output_path)
    
    return pdf_output_path

# Function to upload the PDF to Dropbox
def upload_to_dropbox(pdf_path, folder_name="/light-novels"):
    dropbox_token = os.getenv("M_TOKEN")
    # Connect to Dropbox
    dbx = dropbox.Dropbox(dropbox_token)
    print("Uploading to Dropbox...")
    
    # Open the PDF file and upload to Dropbox
    with open(pdf_path, "rb") as f:
        file_data = f.read()
        # Upload file to specified folder in Dropbox
        dbx.files_upload(file_data, folder_name + "/" + os.path.basename(pdf_path), mode=dropbox.files.WriteMode.overwrite)

    print("Upload complete!")

def main_pdf(data, title):
    paper_list = []

    for list_item_obj in data:
        for key in list_item_obj:
            paper_list.append(key)

    # Download images from all papers
    image_paths = []

    # Download images for paper1 in the original order
    image_paths.extend(download_images(data[0].get("paper1", []), "paper1"))

    # Download images for paper2 onwards in their original order
    for i in range(1, len(data)):
        paper_name = paper_list[i]
        images = data[i].get(paper_name, [])  # Use .get() to avoid KeyError
        if images:  # Proceed only if there are images
            image_paths.extend(download_images(images, paper_name))

    # Create the PDF
    pdf_path = create_pdf(image_paths, title)

    # Upload the PDF to Dropbox
    upload_to_dropbox(pdf_path)

    # Optional: Remove the locally saved PDF file after uploading
    os.remove(pdf_path)

