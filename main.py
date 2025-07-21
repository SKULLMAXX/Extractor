import fitz
import pdfplumber
import os
import json
from PIL import Image

PDF_FILE = "somatosensory.pdf"
OUTPUT_FOLDER = "output"
IMAGE_FOLDER = os.path.join(OUTPUT_FOLDER, "images")
JSON_FILE = os.path.join(OUTPUT_FOLDER, "content.json")

os.makedirs(IMAGE_FOLDER, exist_ok=True)

def extract_images(pdf_path):
    doc = fitz.open(pdf_path)
    images_per_page = {}

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        image_list = page.get_images(full=True)
        images_per_page[page_num + 1] = []

        for img_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_name = f"page{page_num + 1}_image{img_index}.{image_ext}"
            image_path = os.path.join(IMAGE_FOLDER, image_name)

            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)

            images_per_page[page_num + 1].append(image_path)
    return images_per_page

def extract_text(pdf_path):
    content = {}
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            content[i] = text.strip() if text else ""
    return content

def build_json(text_data, image_data):
    pages = []
    for page_num in sorted(text_data.keys()):
        page_entry = {
            "page": page_num,
            "text": text_data[page_num],
            "images": image_data.get(page_num, [])
        }
        pages.append(page_entry)

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(pages, f, indent=4)

    print(f"✅ JSON created at: {JSON_FILE}")

def main():
    print("📄 Extracting images...")
    image_data = extract_images(PDF_FILE)

    print("✏️ Extracting text...")
    text_data = extract_text(PDF_FILE)

    print("🧱 Creating structured JSON...")
    build_json(text_data, image_data)

if __name__ == "__main__":
    main()