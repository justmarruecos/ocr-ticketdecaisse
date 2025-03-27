import base64
import mimetypes
import hashlib
import json
from mistralai import Mistral
from image_utils import enhance_image_for_ocr

API_KEY = "iQUfZle3E832CGpT5Bh2x4c3xoFZjvxP"
client = Mistral(api_key=API_KEY)

def perform_ocr(image_path):
    enhanced_path = enhance_image_for_ocr(image_path)
    mime_type = mimetypes.guess_type(enhanced_path)[0] or "image/jpeg"
    
    with open(enhanced_path, "rb") as f:
        encoded_image = base64.b64encode(f.read()).decode()

    data_url = f"data:{mime_type};base64,{encoded_image}"

    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": "Donne uniquement un JSON structuré contenant les informations du ticket (date, ticket_number, total, mode_paiement, articles, etc.). Pas de texte hors JSON."},
            {"type": "image_url", "image_url": {"url": data_url}}
        ]
    }]

    try:
        response = client.chat.complete(model="pixtral-12b", messages=messages)
        raw_content = response.choices[0].message.content

        # Tentative d'extraction JSON
        try:
            json_data = extract_json_from_string(raw_content)
            return json_data
        except Exception:
            return raw_content
    except Exception as e:
        print(f"Erreur Pixtral OCR : {e}")
        return None

def extract_json_from_string(content):
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1:
        json_string = content[start:end+1]
        return json.loads(json_string)
    raise ValueError("Aucun JSON valide détecté")

def generate_hash(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()
