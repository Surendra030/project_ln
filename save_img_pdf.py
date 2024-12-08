import os
import requests
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from mega import Mega
import shutil
from io import BytesIO
import re
from compress_pdf import  compress_pdf

 
def download_img(img_src,title,length,c):
    folder_name = "images"
    
    os.makedirs(folder_name,exist_ok=True)

    img_path = os.path.join(folder_name,title)

    

    try:
        res = requests.get(img_src)
        res.raise_for_status()
        img_data = res.content

            # Calculate the size in MB
        img_size_mb = len(img_data) / (1024 * 1024)

            # Open and save the image
        img = Image.open(BytesIO(img_data))
        img.save(img_path)
        c += 1
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
    
    # Sort files based on the `c` value extracted from the filename
    def extract_c_value(filename):
        match = re.match(r'(\d+)_', filename)
        return int(match.group(1)) if match else float('inf')  # Sort invalid files last

    image_files.sort(key=lambda x: extract_c_value(os.path.basename(x)))
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
def upload_to_mega(output_pdf,compress_pdf_path,title,images_folder):
    mega = Mega()
    
    keys = os.getenv("M_TOKEN")
    keys = keys.split("_")
    email = keys[0]
    password= keys[1]
    
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

        print(compress_pdf_path)
        if os.path.exists(compress_pdf_path):        
            m.upload(compress_pdf_path,folder_handle)
            print("compresss pdf uploaded..")
        
        
        

    except Exception as e:
        print(e)

    finally:
        os.remove(output_pdf)
        os.remove(f"{zip_file}.zip")
        shutil.rmtree(images_folder)
    


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
    compress_pdf_path = compress_pdf(output_pdf)

    upload_to_mega(output_pdf,compress_pdf_path,title,images_folder)

