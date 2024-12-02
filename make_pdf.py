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
    """Sanitize text by removing unsupported characters and preserving basic formatting."""
    sanitized_lines = []
    for line in text.splitlines():
        sanitized_line = ''.join(c if unicodedata.category(c) in ('Lu', 'Ll', 'Nd', 'Pc', 'Zs', 'Zp') else ' ' for c in line)
        if sanitized_line.strip():
            sanitized_lines.append(sanitized_line.strip())
    return '\n'.join(sanitized_lines)


# Function to download images, perform OCR, and create pages in the PDF
def process_images(images, paper_name, pdf):
    """Process images to extract text (OCR) or add pure images to the PDF."""
    os.makedirs("images", exist_ok=True)  # Ensure the "images" folder exists

    for index, image in enumerate(images):
        img_url = image["src"]

        # Fetch the image from the URL
        response = requests.get(img_url)
        response.raise_for_status()

        # Open and save the image locally
        img = Image.open(BytesIO(response.content))
        img_path = os.path.join("images", f"{paper_name}_page{index + 1}.jpg")
        img.save(img_path)

        # Perform OCR on the image
        ocr_text = pytesseract.image_to_string(img)
        sanitized_text = sanitize_text(ocr_text.strip())

        if sanitized_text:  # If OCR detects text
            # Add a new page for the extracted text
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.set_xy(10, 10)
            pdf.multi_cell(0, 10, sanitized_text)  # Write OCR text on the page with newlines preserved
        else:
            # Add a new page for the pure image
            pdf.add_page()
            pdf.image(img_path, x=10, y=10, w=180)  # Adjust image size

    return pdf


# Function to upload the PDF to Mega
def upload_to_mega(pdf_path, email, password):
    """Upload the PDF file to Mega Cloud."""
    mega = Mega()
    print("Establishing connection to Mega...")
    m = mega.login(email, password)
    print("Uploading PDF to Mega cloud...")
    m.upload(pdf_path)
    print("Upload completed.")


# Main function to generate the PDF
def main_pdf(data, title, index):
    """Generate a PDF with OCR text and pure images."""
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

    # Upload the PDF to Mega Cloud
    email = "afg154006@gmail.com"
    password = "megaMac02335!"
    upload_to_mega(pdf_output_path, email, password)

    # Cleanup
    os.remove(pdf_output_path)
    shutil.rmtree("images")
