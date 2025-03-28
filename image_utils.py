from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np

def enhance_image_for_ocr(image_path):
    img = Image.open(image_path)

    # Niveaux de gris (indispensable)
    img = img.convert("L")

    # Contraste modéré (moins strict)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.2)  # 👈 Réduire la valeur si le contraste est trop fort (ex: 1.2-1.3)

    # Netteté légère
    img = img.filter(ImageFilter.SHARPEN)

    # Binarisation douce (moins stricte)
    seuil_binarisation = 110  # 👈 Ajuste ce seuil (100-120) selon le résultat
    img = img.point(lambda x: 0 if x < seuil_binarisation else 255, '1')

    enhanced_path = "temp_enhanced.jpg"
    img.save(enhanced_path)

    return enhanced_path

