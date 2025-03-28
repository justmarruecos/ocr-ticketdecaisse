import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os, json
import winsound
from datetime import datetime
from pixtral_ocr import perform_ocr
from invoice_processing import extraire_elements
from database_sqlite import insert_invoice_sqlite, insert_article_sqlite, check_existing_ticket, init_db
from database_mongo import check_existing_ticket_mongo, insert_invoice_mongo
from pdf_to_img import convert_pdf_to_images
from camera import capture_image
from image_utils import enhance_image_for_ocr

# ID utilisateur pour traçabilité
user_id = "utilisateur_001"  # à adapter pour chaque session

init_db()

root = tk.Tk()
root.title("Analyse de Tickets - OCR Automobile")
root.geometry("950x750")

file_path_var = tk.StringVar()
ocr_result_text = tk.StringVar()

img_label = tk.Label(root)
img_label.pack(pady=10)

result_label = tk.Label(root, text="", font=("Arial", 10), fg="green")
result_label.pack(pady=5)

frame_output = tk.Frame(root)
frame_output.pack(pady=10, fill="both", expand=True)

scrollbar = tk.Scrollbar(frame_output)
scrollbar.pack(side="right", fill="y")

text_output = tk.Text(frame_output, height=25, width=100, yscrollcommand=scrollbar.set)
text_output.pack(side="left", fill="both", expand=True)

scrollbar.config(command=text_output.yview)


def show_image_preview(path):
    img = Image.open(path)
    img.thumbnail((400, 400))
    img_tk = ImageTk.PhotoImage(img)
    img_label.configure(image=img_tk)
    img_label.image = img_tk

def reset_interface():
    file_path_var.set("")
    ocr_result_text.set("")
    text_output.delete(1.0, tk.END)
    img_label.configure(image='')
    img_label.image = None

def process_invoice(image_path):
    enhanced_path = enhance_image_for_ocr(image_path)
    print(f"📄 Traitement OCR pour {enhanced_path}...")

    ocr_result = perform_ocr(enhanced_path)
    if not ocr_result:
        messagebox.showerror("Erreur OCR", "🚨 OCR échoué : Impossible d'obtenir les données.")
        reset_interface()  # Important : réinitialiser l'interface
        return

    show_image_preview(enhanced_path)  # indispensable pour voir la photo en interface

    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, json.dumps(ocr_result, indent=2, ensure_ascii=False))

    # Extraction structurée AVANT MongoDB pour pouvoir l'utiliser
    parsed = extraire_elements(ocr_result)
    if parsed.get("not_invoice"):
        messagebox.showwarning("Pas une facture", "❗ L'image ne semble pas être une facture valide.")
        return

    ticket_number = parsed.get("ticket_number", f"TEMP-{datetime.now().strftime('%Y%m%d%H%M%S')}")
    date_invoice = parsed.get("date", datetime.today().strftime("%Y-%m-%d"))
    total = parsed.get("total", 0.0)
    payment_method = parsed.get("payment_method", "Inconnu")
    has_discount = parsed.get("has_discount", "Non")
    articles = parsed.get("articles", [])
    vendor = parsed.get("vendor", "Client Caisse")

    if check_existing_ticket_mongo(ticket_number):
        messagebox.showwarning("Doublon Mongo détecté", "❗ Cette facture semble déjà enregistrée en MongoDB.")
        return
    # Enregistrement brut dans MongoDB (maintenant avec parsed défini)
    insert_invoice_mongo(
        ticket_number=ticket_number,
        vendor=vendor,
        client_name="Client Caisse",  # Valeur statique ou extraite dynamiquement si disponible
        date_invoice=date_invoice,
        total=total,
        payment_method=payment_method,
        has_discount=has_discount,
        ocr_result=ocr_result
    )

    if check_existing_ticket(ticket_number, date_invoice, articles):
        messagebox.showwarning("Doublon détecté", "❗ Cette facture semble déjà enregistrée.")
        return

    insert_invoice_sqlite(user_id, ticket_number, vendor, date_invoice, payment_method, total, has_discount)
    for article in articles:
        insert_article_sqlite(
            ticket_number,
            article["name"],
            article["price_unit"],
            article["quantity"]
        )


    display_text = f"🧾 Ticket n°{ticket_number}\n📅 Date : {date_invoice}\n🏪 Magasin : {vendor}\n💳 Paiement : {payment_method}\n💶 Total : {total} €"
    if has_discount == "Oui":
        display_text += "\n🎁 Remise détectée"
    display_text += "\n🛒 Articles :"
    for article in articles:
        display_text += f"\n - {article['name']} x {article['quantity']} = {article['price_unit']} €"  # ✅ Correction



    ocr_result_text.set(display_text)
    articles_count = len(articles)
    result_label.config(text=f"✅ Facture enregistrée - Ticket : {ticket_number}, Articles : {len(articles)}, Total : {total} €")
    winsound.Beep(1000, 200)  # fréquence 1000 Hz, durée 200 ms

    # Réinitialiser automatiquement après 10 secondes
    root.after(10000, reset_interface)


def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("Images ou PDF", "*.jpg *.jpeg *.png *.pdf")])
    if file_path:
        file_path_var.set(file_path)
        image_path = convert_pdf_to_images(file_path)[0] if file_path.lower().endswith(".pdf") else file_path
        show_image_preview(image_path)
        process_invoice(image_path)

def capture_and_process():
    image_path = capture_image()
    if image_path:
        file_path_var.set(image_path)
        show_image_preview(image_path)
        process_invoice(image_path)

# Interface utilisateur

scrollbar = tk.Scrollbar(root, command=text_output.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_output.config(yscrollcommand=scrollbar.set)

tk.Button(root, text="📷 Prendre une photo", command=capture_and_process, bg="#4682B4", fg="white").pack(pady=5)
tk.Button(root, text="📤 Importer une image ou PDF", command=upload_file, bg="#32CD32", fg="white").pack(pady=5)
tk.Button(root, text="🔄 Nouveau scan", command=reset_interface, bg="#FFA500", fg="white").pack(pady=5)

tk.Label(root, textvariable=file_path_var, wraplength=700, fg="gray").pack()
tk.Label(root, text="📝 Résultat OCR :", font=("Arial", 12, "bold")).pack(pady=10)
tk.Label(root, textvariable=ocr_result_text, wraplength=850, justify="left", font=("Courier", 10)).pack()

root.mainloop()
