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
    df = pd.read_csv(csv_path)

    # Configuration des colonnes et des dossiers racines correspondants
    mapping = {
        'cv original': ('CV_Original', 'Original'),
        'cv gender - name variation': ('CV_Genre', 'Gender'),
        'cv origin variation': ('CV_Origin', 'Origin'),
        'cv age variation': ('CV_Age', 'Age')
    }

    for col_name, (root_dir, suffix) in mapping.items():
        # Création du dossier principal (ex: CV_Original)
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)

        for _, row in df.iterrows():
            cv_id = row['id']

            # Nom du sous-dossier avec ESPACE (ex: CV1 Original)
            sub_folder_name = f"CV{cv_id} {suffix}"
            sub_folder_path = os.path.join(root_dir, sub_folder_name)

            if not os.path.exists(sub_folder_path):
                os.makedirs(sub_folder_path)

            # Nom du fichier PDF
            file_name = f"CV{cv_id} {suffix}.pdf"
            file_path = os.path.join(sub_folder_path, file_name)

            # Génération du PDF si la case n'est pas vide
            if pd.notna(row[col_name]):
                create_pdf(row[col_name], file_path)

    print("Opération terminée ! Tous les dossiers et PDFs ont été créés.")

if __name__ == "__main__":
    process_all_cvs('cv/cv.csv')
