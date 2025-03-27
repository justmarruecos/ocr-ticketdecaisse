from pdf2image import convert_from_path
import os

def convert_pdf_to_images(pdf_path, output_folder="factures"):
    os.makedirs(output_folder, exist_ok=True)
    images = convert_from_path(pdf_path)

    image_paths = []
    for i, img in enumerate(images):
        path = os.path.join(output_folder, f"page_{i + 1}.jpg")
        img.save(path, "JPEG")
        image_paths.append(path)

    return image_paths

