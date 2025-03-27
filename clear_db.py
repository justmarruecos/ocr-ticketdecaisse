import sqlite3
from pymongo import MongoClient

def clear_sqlite():
    conn = sqlite3.connect("invoices.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM articles")
    cur.execute("DELETE FROM invoices")
    conn.commit()
    conn.close()
    print("🗑️ SQLite vidé.")

def clear_mongodb():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["ticket_ocr"]
    collection = db["raw_tickets"]
    result = collection.delete_many({})
    print(f"🗑️ MongoDB vidé ({result.deleted_count} documents supprimés).")

if __name__ == "__main__":
    clear_sqlite()
    clear_mongodb()
