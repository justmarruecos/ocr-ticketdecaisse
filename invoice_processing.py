import json
import re
from datetime import datetime
from difflib import get_close_matches

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

    categories_to_ignore = ["cremerie", "epicerie", "charcuterie", "boucherie", "poissonnerie"]
    # Dictionnaire des articles courants pour corrections basiques
    correct_names = ["MINI BABYBEL", "YAOURT A BOIRE", "NOIX CAJOU GRILLEES SALEES", "EPINETTE"]

    for art in articles:
        name = art.get("name") or art.get("nom") or "Inconnu"
        if nettoyer_texte(name) in categories_to_ignore:
            continue
        try:
            raw_name = art.get("name") or art.get("nom") or "Inconnu"
            # Correction automatique par similarité
            corrected_name = get_close_matches(raw_name.upper(), correct_names, n=1, cutoff=0.6)
            name = corrected_name[0] if corrected_name else raw_name

            price = art.get("price_unit") or art.get("prix_unitaire") or art.get("price") or 0
            price = float(str(price).replace(",", ".").replace("€", "").strip())
            quantity = art.get("quantity") or art.get("quantite") or art.get("qte") or 1
            quantity = int(quantity)

            total_price = round(price * quantity, 2)
            calculated_total += total_price

            cleaned_articles.append({
                "name": name,
                "price_unit": round(price, 2),
                "quantity": quantity,
                "total": total_price
            })

        except Exception as e:
            print(f"[Erreur Article] : {art}, Exception: {e}")
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