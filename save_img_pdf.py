import json
import os
import requests
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from mega import Mega
import shutil
import io



def download_img(img_src,title,length,c):
    folder_name = "images"
    
    os.makedirs(folder_name,exist_ok=True)

    img_path = os.path.join(folder_name,title)

    res = requests.get(img_src,stream=True)
    res.raise_for_status()

    try:
        with open(img_path,'wb')as f:
            for chunk in res.iter_content(1024):
                f.write(chunk)
        c +=1

        return c
    except requests.exceptions.RequestException as e:
        print("error : ",e)



def images_to_pdf(images_folder, output_pdf):
    # Get all image file paths in the folder
    image_files = [
        os.path.join(images_folder, file) 
        for file in os.listdir(images_folder) 
        if file.lower().endswith('.jpg')
    ]
    
    # Sort files based on naming (optional, for ordered sequence)
    image_files.sort()

    # Create a PDF file
    c = canvas.Canvas(output_pdf, pagesize=letter)
    
    for image_path in image_files:
        try:
            # Open the image using Pillow
            with Image.open(image_path) as img:
                # Ensure image fits within the PDF page dimensions
                img_width, img_height = img.size
                page_width, page_height = letter
                
                # Scale image to fit within the page
                scale = min(page_width / img_width, page_height / img_height)
                scaled_width = int(img_width * scale)
                scaled_height = int(img_height * scale)
                
                # Add image to the PDF
                c.drawImage(image_path, 
                            x=(page_width - scaled_width) / 2, 
                            y=(page_height - scaled_height) / 2, 
                            width=scaled_width, 
                            height=scaled_height)
                
                c.showPage()  # Add a new page for the next image
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
    
    # Save the PDF
    c.save()
    print(f"PDF created successfully: {output_pdf}")

def upload_to_mega(output_pdf,title,images_folder):
    mega = Mega()
    key = os.getenv("M_TOKEN")
    key = key.split("_")
    email = key[0]
    password = key[1]
    
    m = mega.login(email,password)
    folder = m.create_folder(title)
    folder_handle = folder.get(title)
    zip_file = f"{title}"
    try:
        shutil.make_archive(f"{zip_file}","zip","images")

        m.upload(output_pdf,folder_handle)
        print("pdf uploded..")
        m.upload(f"{zip_file}.zip",folder_handle)
        print("zip file uploded..")
        os.remove(output_pdf)
        os.remove(f"{zip_file}.zip")
        shutil.rmtree(images_folder)

    except Exception as e:
        print(e)
    


def main_pdf(data,title):
    
    c = 1
    for entry in data:
        for key_lst in entry:
            for item_obj in entry[key_lst]:
                img_src = item_obj["src"]
                img_title = f"{c}_{item_obj['id']}_{item_obj['alt']}.jpg"

                c = download_img(img_src,img_title,len(data),c)

    # Example usage
    images_folder = "images"
    output_pdf = f"{title}.pdf"  # Output PDF path

    images_to_pdf(images_folder, output_pdf)
    upload_to_mega(output_pdf,title,images_folder)

