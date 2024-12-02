import requests
from PIL import Image
from io import BytesIO
from fpdf import FPDF
from mega import Mega
import os
import shutil
import pytesseract

# Function to download images and return their paths
def download_images(images, paper_name):
    # Ensure the "images" folder exists
    os.makedirs("images", exist_ok=True)
    
    image_paths = []
    for index, image in enumerate(images):
        img_url = image["src"]
        
        # Fetch the image from the URL
        response = requests.get(img_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Open and save the image
        img = Image.open(BytesIO(response.content))
        img_path = os.path.join("images", f"{paper_name}_page{index + 1}.jpg")
        img.save(img_path)
        
        image_paths.append(img_path)
    
    return image_paths

# Function to create PDF from images with OCR text
def create_pdf_with_ocr(image_paths, title, index):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=5)
    
    for image_path in image_paths:
        # Apply OCR to the image and extract the text
        img = Image.open(image_path)
        ocr_text = pytesseract.image_to_string(img)

        # Add OCR text to the PDF
        pdf.add_page()
        pdf.image(image_path, x=10, y=10, w=180)  # Adjust the image size as needed
        pdf.set_xy(10, 150)  # Set text position after the image (adjust as needed)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, ocr_text)  # Add the OCR text to the PDF
    
    # Save the PDF locally temporarily
    pdf_output_path = f"{index}_{title}_ocr.pdf"
    pdf.output(pdf_output_path)
    
    return pdf_output_path

# Function to upload the PDF to Mega
def upload_to_mega(pdf_path, email, password):
    # Log in to Mega
    mega = Mega()
    print("new connection establishing")
    m = mega.login(email, password)
    print("Uploading to Mega cloud...")
    # Upload the PDF file to Mega
    m.upload(pdf_path)
    print("uploading completed..")

def main_pdf(data, title, index):
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

    # Create the OCR PDF
    pdf_path = create_pdf_with_ocr(image_paths, title, index)

    # Upload the PDF to Mega Cloud
    email = "afg154007@gmail.com"  # Replace with your Mega email 
    password = "megaMac02335!"  # Replace with your Mega password
    upload_to_mega(pdf_path, email, password)

    # Optional: Remove the locally saved PDF file after uploading
    os.remove(pdf_path)
    shutil.rmtree("images")

