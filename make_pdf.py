import requests
from PIL import Image
from io import BytesIO
from fpdf import FPDF
from mega import Mega
import os
import shutil

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

# Function to create PDF from images
def create_pdf(image_paths,title):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=5)
    
    for image_path in image_paths:
        pdf.add_page()
        pdf.image(image_path, x=10, y=10, w=180)  # Adjust the image size as needed
    
    # Save the PDF locally temporarily
    pdf_output_path = f"{title}.pdf"
    pdf.output(pdf_output_path)
    
    return pdf_output_path

def upload_to_mega(pdf_path, email, password, title):
    # Log in to Mega
    mega = Mega()
    print("New connection establishing")
    m = mega.login(email, password)
    
    # Ensure the "images" folder exists before zipping it
    if not os.path.exists("images"):
        print("Error: The 'images' folder does not exist.")
        return

    # Create the zip file only if images are present
    output_zip = f"{title}.zip"
    try:
        print(f"Creating zip archive for images: {output_zip}")
        shutil.make_archive(output_zip, "zip", "images")
    except Exception as e:
        print(f"Error creating zip archive: {e}")
        return

    # Upload the PDF file to Mega
    print("Uploading PDF to Mega cloud...")
    m.upload(pdf_path)
    
    # Upload the zip file to Mega
    print(f"Uploading {output_zip} to Mega cloud...")
    try:
        m.upload(output_zip)
        print("Uploading completed successfully.")
    except Exception as e:
        print(f"Error uploading zip file: {e}")


def main_pdf(data,title,index):
    
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
    pdf_path = create_pdf(image_paths,title)

    # Upload the PDF to Mega Cloud
    email = "afg154006@gmail.com"  # Replace with your Mega email
    password = "megaMac02335!"  # Replace with your Mega password
    upload_to_mega(pdf_path, email, password,title)

    # Optional: Remove the locally saved PDF file after uploading
    os.remove(pdf_path)
    shutil.rmtree("images")