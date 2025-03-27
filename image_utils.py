import cv2

def enhance_image_for_ocr(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        return image_path
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sharpened = cv2.GaussianBlur(gray, (0, 0), 3)
    sharpened = cv2.addWeighted(gray, 1.5, sharpened, -0.5, 0)
    enhanced_path = "temp_enhanced.jpg"
    cv2.imwrite(enhanced_path, sharpened)
    return enhanced_path