import os
import subprocess
import platform

def compress_pdf(input_path):
    """
    Compress a PDF file or all PDF files in a directory.

    Args:
    input_path (str): The path to a PDF file or directory.

    Returns:
    str: The path of the output compressed PDF.
    """
    # Determine the correct Ghostscript command based on the OS
    if platform.system() == 'Windows':
        gs_command = 'gswin64c'  # For Windows
    else:
        gs_command = 'gs'  # For Linux

    # Check if the input path is a file or directory
    if os.path.isfile(input_path):
        # Handle a single file
        base_name = os.path.basename(input_path)
        file_name, file_extension = os.path.splitext(base_name)
        output_path = os.path.join(os.path.dirname(input_path), f"{file_name}-compress{file_extension}")
        print(f"Processing file: {input_path}")
        subprocess.call([gs_command, '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                         '-dPDFSETTINGS=/screen', '-dNOPAUSE', '-dQUIET', '-dBATCH',
                         '-sOutputFile=' + output_path, input_path])
        print(f"File compressed and saved as: {output_path}")
        return output_path

    elif os.path.isdir(input_path):
        # Handle a directory of files
        pdf_files = [item for item in os.listdir(input_path) if item.endswith('.pdf')]
        
        if not pdf_files:
            print("No PDF files found in the directory.")
            return None
        
        print(f"Found {len(pdf_files)} PDF files to process.")
        for idx, item in enumerate(pdf_files, start=1):
            full_input_path = os.path.join(input_path, item)
            file_name, file_extension = os.path.splitext(item)
            output_path = os.path.join(input_path, f"{file_name}-compress{file_extension}")
            print(f"Processing file {idx} of {len(pdf_files)}: {item}")
            subprocess.call([gs_command, '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                             '-dPDFSETTINGS=/screen', '-dNOPAUSE', '-dQUIET', '-dBATCH',
                             '-sOutputFile=' + output_path, full_input_path])
            print(f"File compressed and saved as: {output_path}")
        print("input path : ",input_path,"\noutput path : ",output_path)
        return output_path

    else:
        print("Invalid input path. Please provide a valid file or directory.")
        return None

