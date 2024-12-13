from pdf2image import convert_from_path
import cv2
import os

def pdf_to_video(pdf_path, video_path, duration=10, fps=1):
    # Convert PDF pages to images
    images = convert_from_path(pdf_path)
    img_folder = "temp_images"
    os.makedirs(img_folder, exist_ok=True)
    
    img_files = []
    for i, img in enumerate(images):
        img_file = f"{img_folder}/page_{i + 1}.jpg"
        img.save(img_file, "JPEG")
        img_files.append(img_file)
    
    # Determine video frame size from the first image
    first_image = cv2.imread(img_files[0])
    height, width, _ = first_image.shape
    frame_size = (width, height)
    
    # Create VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(video_path, fourcc, fps, frame_size)
    
    # Add images to video
    frames_per_image = duration * fps
    for img_file in img_files:
        img = cv2.imread(img_file)
        for _ in range(frames_per_image):
            video_writer.write(img)
    
    # Release VideoWriter
    video_writer.release()
    
    # Cleanup temporary images
    for img_file in img_files:
        os.remove(img_file)
    os.rmdir(img_folder)
    print(f"Video saved at: {video_path}")
    if os.path.exists(video_path):
        os.remove(pdf_path)
        return True
    else:
        False

# # Example usage
# pdf_path = "file.pdf"  # Path to the input PDF
# video_path = "video.mp4"  # Path to save the video
# pdf_to_video(pdf_path, video_path)
