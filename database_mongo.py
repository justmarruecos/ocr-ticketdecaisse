from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["ticket_ocr"]
collection = db["raw_tickets"]

def insert_invoice_mongo(ticket_number, vendor, client, date_invoice, total, payment_method, has_discount, ocr_result):
    existing = collection.find_one({"ticket_number": ticket_number})
    if existing:
        print(f"⚠️ Ticket {ticket_number} déjà présent dans MongoDB.")
        return

    document = {
        "ticket_number": ticket_number,
        "vendor": vendor,
        "client": client,
        "date_invoice": datetime.strptime(date_invoice, "%Y-%m-%d"),
        "total": total,
        "payment_method": payment_method,
        "has_discount": has_discount,
        "ocr_result": ocr_result,
        "inserted_at": datetime.now()
    }

    collection.insert_one(document)
    print(f"✅ Ticket {ticket_number} stocké dans MongoDB.")
