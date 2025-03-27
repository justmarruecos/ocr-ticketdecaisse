import sqlite3

def clear_all():
    conn = sqlite3.connect("invoices.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM articles")
    cur.execute("DELETE FROM invoices")
    conn.commit()
    conn.close()
    print("🗑️ Base de données vidée.")

if __name__ == "__main__":
    clear_all()
