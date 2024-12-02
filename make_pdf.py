import requests
from PIL import Image
from io import BytesIO
from fpdf import FPDF
from mega import Mega
import os
import shutil
import pytesseract
import unicodedata

# Function to remove or replace unsupported characters in text
def sanitize_text(text):
    return ''.join(c if unicodedata.category(c) in ('Lu', 'Ll', 'Nd', 'Pc', 'Zs') else ' ' for c in text)

# Function to download images and perform OCR for each
def process_images(images, paper_name, pdf):
    os.makedirs("images", exist_ok=True)  # Ensure the "images" folder exists

    for index, image in enumerate(images):
        img_url = image["src"]
        
        # Fetch the image from the URL
        response = requests.get(img_url)
        response.raise_for_status()
        
        # Open the image
        img = Image.open(BytesIO(response.content))
        
        # Save the image locally
        img_path = os.path.join("images", f"{paper_name}_page{index + 1}.jpg")
        img.save(img_path)
        
        # Perform OCR on the image
        ocr_text = pytesseract.image_to_string(img)
        sanitized_text = sanitize_text(ocr_text)
        
        # Add a new page to the PDF for this image and its OCR text
        pdf.add_page()
        pdf.image(img_path, x=10, y=10, w=180)  # Adjust image size
        pdf.set_xy(10, 150)  # Set text position
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, sanitized_text)  # Add sanitized text

    return pdf

# Function to upload the PDF to Mega
def upload_to_mega(pdf_path, email, password):
    mega = Mega()
    print("Establishing connection to Mega...")
    m = mega.login(email, password)
    print("Uploading PDF to Mega cloud...")
    m.upload(pdf_path)
    print("Upload completed.")

def main_pdf(data, title, index):
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
            pdf = process_images(images, paper_name, pdf)

    # Save the final PDF
    pdf_output_path = f"{index}_{title}_ocr.pdf"
    pdf.output(pdf_output_path)

    # # Upload the PDF to Mega Cloud
    # key = os.getenv("M_TOKEN").split("_")
    # email = key[0]
    # password = key[1]
    email = "afg154007@gmail.com"
    password= "megaMac02335!"
    upload_to_mega(pdf_output_path, email, password)

    # Cleanup
    os.remove(pdf_output_path)
    shutil.rmtree("images")

