import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import os
from io import BytesIO  # Import BytesIO
import cv2
import tabula  # Library for extracting tables from PDFs

# Specify the path to Tesseract-OCR executable (adjust for your system)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def load_pdf(file_path):
    """Load a PDF document."""
    try:
        doc = fitz.open(file_path)
        print("PDF successfully loaded.")
        return doc
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return None

def extract_text_with_ocr(doc):
    """Extract and print text from scanned PDF using OCR."""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()  # Render the page as an image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Perform OCR on the image
        text = pytesseract.image_to_string(img)
        print(f"--- Text from Page {page_num + 1} ---")
        print(text)
        print("\n")

def extract_metadata(doc):
    """Extract and print metadata of the PDF."""
    metadata = doc.metadata
    print("--- PDF Metadata ---")
    for key, value in metadata.items():
        print(f"{key}: {value}")
    print("\n")

def extract_images(doc, output_dir=r"C:\Users\Nisha kadian\Documents\pyhton Netz\advanced python\TASK2_DATA_EXTRACTION\extracted_images"):
    """Extract embedded images from the PDF and save them to the specified directory in PNG format."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        print(f"--- Extracting embedded images from Page {page_num + 1} ---")

        # Extract all images in the page
        img_list = page.get_images(full=True)

        if not img_list:
            print("No embedded images found on this page.\n")
            continue

        for img_index, img in enumerate(img_list, start=1):
            xref = img[0]  # XREF of the image
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            # Convert image bytes to PNG format using PIL (Pillow)
            img_pil = Image.open(BytesIO(image_bytes))

            # Create a unique filename for the image in PNG format
            img_filename = os.path.join(output_dir, f"page_{page_num + 1}_image_{img_index}.png")

            # Save the image as PNG
            img_pil.save(img_filename, "PNG")

            print(f"Saved Image {img_index} from Page {page_num + 1} as {img_filename}")

def extract_and_save_images_from_png(png_folder, output_folder):
    """
    Detects and extracts individual images (diagrams) from PNG files and saves them
    in the 'images' subfolder inside the output folder.
    """
    # Ensure the 'images' subfolder exists inside output_folder
    images_folder = os.path.join(output_folder, 'images')
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)

    # Iterate through all PNG files in the folder
    for page_num, image_name in enumerate(os.listdir(png_folder), start=1):
        if image_name.endswith(".png"):
            image_path = os.path.join(png_folder, image_name)
            
            # Open the image using OpenCV
            img = cv2.imread(image_path)
            
            # Convert the image to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding or edge detection to detect images/diagrams
            _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
            
            # Find contours (potential diagrams)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours):
                # Get the bounding box for each contour
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter out small contours that might not be actual images (diagrams)
                if w > 50 and h > 50:  # Adjust these values based on your images
                    # Crop the image based on the bounding box
                    cropped_img = img[y:y+h, x:x+w]
                    
                    # Save the cropped image as a separate file
                    diagram_img_path = os.path.join(images_folder, f"{image_name}diagram{i+1}.png")
                    cv2.imwrite(diagram_img_path, cropped_img)
                    
                    print(f"Saved diagram from {image_name} as {diagram_img_path}")

import pdfplumber
import pandas as pd

def extract_tables_with_pdfplumber(file_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()

            if not tables:
                print(f"No tables found on Page {page_num}")
                continue

            for i, table in enumerate(tables):
                df = pd.DataFrame(table)
                csv_filename = os.path.join(output_dir, f"table_page_{page_num}_table_{i+1}.csv")
                df.to_csv(csv_filename, index=False)
                print(f"Saved Table {i+1} from Page {page_num} as {csv_filename}")




def main():
    file_path = r'C:\Users\Nisha kadian\Documents\pyhton Netz\advanced python\PublicWaterMassMailing.pdf'
    doc = load_pdf(file_path)
    if not doc:
        return

    # Extract metadata
    extract_metadata(doc)

    # Extract and print text using OCR
    extract_text_with_ocr(doc)

    # Extract images and save them in PNG format
    extract_images(doc)

    # Close the document
    doc.close()

    # Now extract and save diagrams from the extracted PNG images
    png_folder = r"C:\Users\Nisha kadian\Documents\pyhton Netz\advanced python\TASK2_DATA_EXTRACTION\extracted_images"  # Folder with PNG images
    output_folder = r"C:\Users\Nisha kadian\Documents\pyhton Netz\advanced python\TASK2_DATA_EXTRACTION\output"  # Main output folder
    extract_and_save_images_from_png(png_folder, output_folder)

    # Extract tables and save them as CSV files
    tables_output_dir = r"C:\Users\Nisha kadian\Documents\pyhton Netz\advanced python\TASK2_DATA_EXTRACTION\tables_output"  # Folder for CSVs
    extract_tables_with_pdfplumber(file_path, tables_output_dir)

if __name__ == "__main__":
    main()