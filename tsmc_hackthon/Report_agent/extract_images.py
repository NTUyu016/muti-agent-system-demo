
from pypdf import PdfReader
import os

def extract_images_from_pdf(pdf_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    reader = PdfReader(pdf_path)
    count = 0
    
    print(f"Processing {len(reader.pages)} pages...")
    
    for i, page in enumerate(reader.pages):
        try:
            for image_file_object in page.images:
                image_name = f"page_{i+1}_{image_file_object.name}"
                image_path = os.path.join(output_dir, image_name)
                
                with open(image_path, "wb") as fp:
                    fp.write(image_file_object.data)
                
                print(f"Extracted: {image_name}")
                count += 1
        except Exception as e:
            print(f"Error on page {i+1}: {e}")

    print(f"Total extracted images: {count}")

if __name__ == "__main__":
    pdf_path = r"c:\Users\20151\OneDrive\桌面\tsmc\tsmc_hackthon\Report_agent\2026 TSMC CareerHack_ 智慧產業分析 Multi-Agent System 架構.pdf"
    output_dir = r"c:\Users\20151\OneDrive\桌面\tsmc\tsmc_hackthon\Report_agent\extracted_images"
    extract_images_from_pdf(pdf_path, output_dir)
