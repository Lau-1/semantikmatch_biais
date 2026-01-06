import pandas as pd
from fpdf import FPDF
import os

def clean_text(text):
    """Nettoie le texte pour éviter les erreurs d'encodage Latin-1."""
    if not isinstance(text, str): return ""
    replacements = {
        '\u2013': '-', '\u2014': '-', '\u2019': "'",
        '\u2018': "'", '\u201c': '"', '\u201d': '"', '\u2022': '*'
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text.encode('latin-1', 'replace').decode('latin-1')

def create_pdf(content, file_path):
    """Génère un PDF simple à partir d'un texte donné."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    text = clean_text(content)
    lines = text.split('\n')

    # Titre ou première ligne en gras
    pdf.set_font("Arial", 'B', 14)
    if lines:
        pdf.multi_cell(0, 10, lines[0])
        pdf.ln(4)

    # Corps du texte
    pdf.set_font("Arial", size=11)
    for line in lines[1:]:
        if line.isupper() and len(line) > 3:
            pdf.ln(3)
            pdf.set_font("Arial", 'B', 11)
            pdf.multi_cell(0, 7, line)
            pdf.set_font("Arial", size=11)
        else:
            pdf.multi_cell(0, 6, line)

    pdf.output(file_path)

def process_all_cvs(csv_path):
    # Vérification de l'existence du fichier CSV
    if not os.path.exists(csv_path):
        print(f"Erreur : Le fichier {csv_path} est introuvable.")
        return

    df = pd.read_csv(csv_path)

    # Dossier racine principal
    base_folder = "CV_Generes"

    # Configuration : Colonne CSV -> (Nom du sous-dossier, Suffixe du fichier)
    mapping = {
        'cv original': ('CV_Original', 'Original'),
        'cv gender - name variation': ('CV_Genre', 'Gender'),
        'cv origin variation': ('CV_Origin', 'Origin'),
        'cv age variation': ('CV_Age', 'Age')
    }

    print(f"Début de la génération dans le dossier '{base_folder}'...")

    for col_name, (sub_folder_name, suffix) in mapping.items():
        # Construction du chemin : CV_Generes / CV_Original
        target_dir = os.path.join(base_folder, sub_folder_name)

        # Création du dossier s'il n'existe pas (exist_ok=True évite les erreurs)
        os.makedirs(target_dir, exist_ok=True)

        count = 0
        for _, row in df.iterrows():
            cv_id = row['id']

            # Génération du PDF si la colonne contient des données
            if pd.notna(row[col_name]):
                # Nom du fichier : CV1 Original.pdf
                file_name = f"CV{cv_id} {suffix}.pdf"
                file_path = os.path.join(target_dir, file_name)

                create_pdf(row[col_name], file_path)
                count += 1

        print(f" -> {count} CVs générés dans {sub_folder_name}")

    print("\nOpération terminée ! L'architecture suivante a été créée :")
    print(f"📂 {base_folder}")
    for _, (name, _) in mapping.items():
        print(f" ├── 📂 {name} (contient les PDF)")

if __name__ == "__main__":
    process_all_cvs('cv/data/cv.csv')
