# ocr-ticketdecaisse

🚗 Présentation du projet
Cette application permet aux utilisateurs de capturer ou d'importer des tickets de caisse pour en extraire automatiquement les données pertinentes à l'aide d'un modèle OCR avancé (Pixtral - Mistral AI). L'objectif principal est de fournir aux utilisateurs une vision claire des pièces automobiles remplacées dans leur véhicule, et aux marques de mieux comprendre leurs consommateurs.

🎯 Fonctionnalités Principales
📸 Capture / Upload de Tickets : Support des images JPG, PNG et des documents PDF.

🖥️ OCR Avancé (Pixtral) : Extraction fiable des données textuelles, même sur des tickets légèrement abîmés.

⚙️ Nettoyage et Amélioration des images : Traitement automatique des images pour une meilleure extraction OCR.

📂 Stockage double :

NoSQL (MongoDB) : Archivage complet des données brutes.

SQL (SQLite) : Stockage structuré pour analyses avancées.

🛠️ Gestion des données manquantes : Date actuelle par défaut, calcul automatique du total manquant.

🚦 Prévention des doublons : Vérification avancée des tickets déjà enregistrés.

📊 Interface claire : Prévisualisation et affichage des résultats OCR en temps réel.
