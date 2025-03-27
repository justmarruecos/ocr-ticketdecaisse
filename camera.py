import cv2
import os

def capture_image(save_path="factures/captured_ticket.jpg"):
    cap = cv2.VideoCapture(0)  # Essaie avec 1 si 0 ne fonctionne pas

    if not cap.isOpened():
        print("❌ Erreur : Impossible d'accéder à la caméra.")
        return None

    print("📷 Caméra activée - Appuyez sur 'S' pour capturer, 'ESC' pour quitter")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Erreur : Impossible de lire la vidéo")
            break

        cv2.imshow("Capture Ticket - Appuyez sur 'S'", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):  # Capture quand on appuie sur 'S'
            cv2.imwrite(save_path, frame)
            print(f"✅ Image capturée et sauvegardée dans {save_path}")
            break
        elif key == 27:  # Quitter avec ESC
            print("❌ Capture annulée")
            break

    cap.release()
    cv2.destroyAllWindows()
    return save_path
