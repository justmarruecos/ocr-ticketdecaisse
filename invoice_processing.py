import json
import re
from datetime import datetime

def nettoyer_texte(texte):
    if isinstance(texte, list):
        texte = " ".join(str(item) for item in texte)
    if not isinstance(texte, str):
        return ""
    texte = texte.lower()
    texte = re.sub(r"\s+", " ", texte)
    return texte.strip()

def contient_mots_cles(text, mots_cles):
    text = nettoyer_texte(text)
    return any(mot in text for mot in mots_cles)

def est_possiblement_une_facture(texte_ocr):
    if isinstance(texte_ocr, dict):
        texte_ocr = json.dumps(texte_ocr)

    texte_ocr = nettoyer_texte(texte_ocr)

    # Liste enrichie pour mieux filtrer les tickets réels
    mots_cles_facture = [
        "article", "tva", "total", "ttc", "cb", "paiement",
        "prix", "pu", "qté", "montant", "facture", "client"
    ]

    if len(texte_ocr) < 50:
        return False

    return contient_mots_cles(texte_ocr, mots_cles_facture)

def detect_vendor_from_text(raw_text):
    vendors_list = ["norauto", "carrefour", "leclerc", "auto5", "feu vert", "midas", "speedy", "lidl", "Uexpress"]
    raw_text_lower = raw_text.lower()
    for vendor in vendors_list:
        if vendor in raw_text_lower:
            return vendor.capitalize()
    return "Inconnu"

def detect_category(article_name):
    categories = {
        "Huile": ["huile", "lubrifiant"],
        "Filtre": ["filtre à huile", "filtre à air", "filtre à essence"],
        "Batterie": ["batterie"],
        "Pneus": ["pneu", "pneus"],
        "Freins": ["plaquette", "frein", "disque"],
        "Autre": []
    }
    article_name_lower = article_name.lower()
    for category, keywords in categories.items():
        if any(keyword in article_name_lower for keyword in keywords):
            return category
    return "Pas de relation avec l'automobile"

def extraire_elements(ocr_result):
    if isinstance(ocr_result, str):
        try:
            ocr_result = json.loads(ocr_result)
        except Exception:
            return {"not_invoice": True}

    texte_complet = json.dumps(ocr_result)

    if not est_possiblement_une_facture(texte_complet):
        return {"not_invoice": True}

    ticket_number = ocr_result.get("ticket_number", "Inconnu")
    date_raw = ocr_result.get("date", "")
    total = ocr_result.get("total")
    payment_method = ocr_result.get("mode_paiement", "Inconnu")
    has_discount = ocr_result.get("has_discount", "Non")
    vendor = ocr_result.get("vendor", "Inconnu")
    articles = ocr_result.get("articles", [])

    if not isinstance(articles, list):
        articles = []

    cleaned_articles = []
    calculated_total = 0.0

    for art in articles:
        name = art.get("name", "").strip()
        try:
            price_raw = str(art.get("price_unit", art.get("prix_unitaire", "0")))
        
            # Ignore les lignes sans prix valides ou trop courtes
            if len(name) < 3 or not price_raw.replace('.', '', 1).isdigit():
                continue

            price = float(price_raw)
            quantity = int(str(art.get("quantity", "1")).strip())
            calculated_total += price * quantity

            CATEGORIES_EXCLUES = ['cremerie', 'epicerie', 'boulangerie', 'boucherie', 'poissonnerie', 'fruits et legumes']
            if name.lower() in CATEGORIES_EXCLUES:
                continue
            cleaned_articles.append({
                "name": name,
                "price_unit": price,
                "quantity": quantity,
                "total": round(price * quantity, 2),
                "category": detect_category(name)
            })

        except Exception:
            continue


    if total is None or not isinstance(total, (int, float, str)) or str(total).strip() == "":
        total = round(calculated_total, 2)
    else:
        try:
            total = float(str(total).replace(",", ".").replace("€", "").strip())
        except:
            total = round(calculated_total, 2)

    try:
        if not date_raw or len(date_raw.strip()) < 6:
            raise ValueError
        date_invoice = datetime.strptime(date_raw, "%d/%m/%y").date()
    except Exception:
        date_invoice = datetime.today().date()

    texte_complet = json.dumps(ocr_result, ensure_ascii=False)
    vendor = detect_vendor_from_text(texte_complet)

    texte_ticket_complet = texte_complet.lower()
    if vendor == "Inconnu":
        if "u express" in texte_ticket_complet:
            vendor = "U Express"
        elif "carrefour" in texte_ticket_complet:
            vendor = "Carrefour"
        # Ajoute plus de magasins ici si besoin

    return {
        "ticket_number": ticket_number,
        "date": date_invoice.strftime("%Y-%m-%d"),
        "total": total,
        "payment_method": payment_method,
        "has_discount": has_discount,
        "articles": cleaned_articles,
        "vendor": vendor,
        "not_invoice": False
    }
