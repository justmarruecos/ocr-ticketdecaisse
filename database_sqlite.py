import sqlite3

DB_NAME = "invoices.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        user_ticket_id INTEGER,
        ticket_number TEXT,
        vendor TEXT,
        date_invoice TEXT,
        payment_method TEXT,
        total REAL,
        has_discount TEXT,
        UNIQUE(ticket_number, date_invoice)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_ticket TEXT,
        article_name TEXT,
        article_price REAL,
        article_quantity INTEGER,
        article_total REAL
    )
    """)

    cur.execute("PRAGMA table_info(articles)")
    columns = [row[1] for row in cur.fetchall()]
    if "article_total" not in columns:
        cur.execute("ALTER TABLE articles ADD COLUMN article_total REAL")

    conn.commit()
    conn.close()

def get_next_user_ticket_id(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT MAX(user_ticket_id) FROM invoices WHERE user_id = ?
    """, (user_id,))
    last_id = cur.fetchone()[0]
    conn.close()
    return 1 if last_id is None else last_id + 1

def insert_invoice_sqlite(user_id, ticket_number, vendor, date_invoice, payment_method, total, has_discount):
    user_ticket_id = get_next_user_ticket_id(user_id)
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO invoices (user_id, user_ticket_id, ticket_number, vendor, date_invoice, payment_method, total, has_discount)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, user_ticket_id, ticket_number, vendor, date_invoice, payment_method, total, has_discount))
    conn.commit()
    conn.close()

def insert_article_sqlite(ticket_number, name, price_unit, quantity):
    if isinstance(price_unit, str):
        price_unit = price_unit.replace("€", "").replace(",", ".").strip()
    try:
        price_unit = float(price_unit)
    except:
        price_unit = 0.0


    try:
        article_total = round(price_unit * quantity, 2)
    except:
        article_total = 0.0
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO articles (invoice_ticket, article_name, article_price, article_quantity, article_total)
    VALUES (?, ?, ?, ?, ?)
    """, (ticket_number, name, price_unit, quantity, article_total))
    conn.commit()
    conn.close()

def check_existing_ticket(ticket_number, date_invoice, articles):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
    SELECT id FROM invoices WHERE ticket_number = ? AND date_invoice = ?
    """, (ticket_number, date_invoice))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

# 🔽 Fonctions supplémentaires pour lecture des données 🔽

def get_all_invoices():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM invoices ORDER BY date_invoice DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_articles_by_ticket(ticket_number):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT article_name, article_price, article_quantity, article_total FROM articles WHERE invoice_ticket = ?", (ticket_number,))
    rows = cur.fetchall()
    conn.close()
    return rows

def delete_invoice(ticket_number):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM invoices WHERE ticket_number = ?", (ticket_number,))
    cur.execute("DELETE FROM articles WHERE invoice_ticket = ?", (ticket_number,))
    conn.commit()
    conn.close()

def get_invoice_by_id(invoice_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
    invoice = cur.fetchone()
    conn.close()
    return invoice

def get_top_articles(limit=10):
    conn = sqlite3.connect('invoices.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT article_name, COUNT(article_name) as frequency 
        FROM articles 
        GROUP BY article_name 
        ORDER BY frequency DESC 
        LIMIT ?
    """, (limit,))
    top_articles = cursor.fetchall()
    conn.close()
    return top_articles
