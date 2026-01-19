import pandas as pd
import re
import os
import subprocess
import shutil
import sys

# --- CONFIGURATION ---
INPUT_CSV = 'data.csv'
OUTPUT_DIR = 'cv_pdf_finaux'
COLONNE_CV = 'cv original'  # La colonne contenant le texte du CV

def check_latex_installed():
    """Vérifie si pdflatex est accessible."""
    if shutil.which('pdflatex') is None:
        print("❌ ERREUR : 'pdflatex' n'est pas trouvé.")
        print("Veuillez installer une distribution LaTeX (MiKTeX sur Windows, TeX Live sur Linux/Mac).")
        return False
    return True

def escape_latex(text):
    """Échappe les caractères spéciaux LaTeX."""
    if not isinstance(text, str): return ""
    chars = {
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_',
        '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'
    }
    pattern = re.compile('|'.join(re.escape(key) for key in chars.keys()))
    return pattern.sub(lambda x: chars[x.group()], text)

def format_section_content(text):
    """Formate le contenu des sections (gras pour les dates/titres, listes à puces)."""
    if not text: return ""
    lines = text.strip().split('\n')
    formatted = []
    in_itemize = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Détection des listes à puces (lignes commençant par - ou •)
        if line.startswith('- ') or line.startswith('• '):
            if not in_itemize:
                formatted.append(r"\begin{itemize}[leftmargin=*, noitemsep, topsep=0pt]")
                in_itemize = True
            clean_line = line[1:].strip()
            formatted.append(r"\item " + escape_latex(clean_line))
        else:
            if in_itemize:
                formatted.append(r"\end{itemize}")
                in_itemize = False

            # Mise en gras heuristique : lignes courtes contenant une année ou en majuscules
            is_date_line = re.search(r'\d{4}', line)
            if (is_date_line or line.isupper()) and len(line) < 80:
                formatted.append(r"\textbf{" + escape_latex(line) + r"} \\")
            else:
                formatted.append(escape_latex(line) + r" \\")

    if in_itemize:
        formatted.append(r"\end{itemize}")

    return "\n".join(formatted)

def parse_cv_text(text):
    """Découpe le texte brut du CV en sections logiques."""
    sections = {
        "HEADER": "",
        "EDUCATION": "",
        "EXPERIENCE": "",
        "SKILLS": "",
        "INTERESTS": ""
    }

    # Mots-clés pour le découpage (basé sur votre data.csv)
    keywords = ["EDUCATION", "PROFESSIONAL EXPERIENCE", "SKILLS", "PERSONAL INTERESTS"]
    pattern = r'(' + '|'.join(keywords) + r')'

    # Découpage du texte
    parts = re.split(pattern, text)

    # La première partie est l'en-tête (Nom, etc.)
    sections["HEADER"] = parts[0].strip()

    # Remplissage des autres sections
    current_key = None
    for i in range(1, len(parts), 2):
        key = parts[i]
        content = parts[i+1] if i+1 < len(parts) else ""

        if key == "EDUCATION":
            sections["EDUCATION"] = content
        elif key == "PROFESSIONAL EXPERIENCE":
            sections["EXPERIENCE"] = content
        elif key == "SKILLS":
            sections["SKILLS"] = content
        elif key == "PERSONAL INTERESTS":
            sections["INTERESTS"] = content

    return sections

def generate_latex(data):
    """Génère le code LaTeX complet."""

    # Traitement de l'en-tête (Nom et détails)
    header_lines = data["HEADER"].split('\n')
    name = escape_latex(header_lines[0]) if header_lines else "Candidat"
    details = " \\\\ ".join([escape_latex(l) for l in header_lines[1:]]) if len(header_lines) > 1 else ""

    template = r"""
\documentclass[a4paper,10pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[margin=2cm]{geometry}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{helvet}

% Police plus moderne
\renewcommand{\familydefault}{\sfdefault}

% Style des titres
\titleformat{\section}{\Large\bfseries\color{blue!60!black}}{}{0em}{}[\titlerule]
\titlespacing{\section}{0pt}{12pt}{8pt}

\begin{document}

% EN-TÊTE
\begin{center}
    {\Huge \textbf{VAR_NAME}} \\[0.5em]
    {\large VAR_DETAILS}
\end{center}

\vspace{0.5cm}

% EDUCATION
\section*{EDUCATION}
VAR_EDUCATION

% EXPÉRIENCE
\section*{PROFESSIONAL EXPERIENCE}
VAR_EXPERIENCE

% COMPÉTENCES
\section*{SKILLS}
VAR_SKILLS

% INTÉRÊTS
\section*{PERSONAL INTERESTS}
VAR_INTERESTS

\end{document}
    """

    # Remplacement des variables
    content = template.replace("VAR_NAME", name)
    content = content.replace("VAR_DETAILS", details)
    content = content.replace("VAR_EDUCATION", format_section_content(data["EDUCATION"]))
    content = content.replace("VAR_EXPERIENCE", format_section_content(data["EXPERIENCE"]))
    content = content.replace("VAR_SKILLS", format_section_content(data["SKILLS"]))
    content = content.replace("VAR_INTERESTS", format_section_content(data["INTERESTS"]))

    return content, name

def main():
    if not check_latex_installed():
        sys.exit(1)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Chargement CSV
    try:
        df = pd.read_csv(INPUT_CSV)
        # Nettoyage des noms de colonnes (enlève espaces inutiles)
        df.columns = [c.strip() for c in df.columns]
    except Exception as e:
        print(f"❌ Erreur lecture CSV : {e}")
        sys.exit(1)

    if COLONNE_CV not in df.columns:
        print(f"❌ Colonne '{COLONNE_CV}' introuvable. Colonnes dispos : {list(df.columns)}")
        sys.exit(1)

    print(f"🚀 Traitement de {len(df)} CVs...")

    for index, row in df.iterrows():
        raw_text = str(row[COLONNE_CV])

        # 1. Parsing
        parsed_data = parse_cv_text(raw_text)

        # 2. Génération LaTeX
        tex_content, safe_name = generate_latex(parsed_data)

        # Nettoyage du nom de fichier
        filename_base = f"CV_{index}_{re.sub(r'[^a-zA-Z0-9]', '_', safe_name)}"
        tex_file = os.path.join(OUTPUT_DIR, f"{filename_base}.tex")
        pdf_file = f"{filename_base}.pdf"

        # 3. Écriture
        with open(tex_file, "w", encoding='utf-8') as f:
            f.write(tex_content)

        # 4. Compilation
        try:
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-output-directory", OUTPUT_DIR, tex_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                check=True
            )
            print(f"✅ Généré : {pdf_file}")
        except subprocess.CalledProcessError:
            print(f"⚠️ Erreur compilation pour : {safe_name}")

        # Nettoyage fichiers temporaires
        for ext in ['.aux', '.log', '.out']:
            temp_file = os.path.join(OUTPUT_DIR, f"{filename_base}{ext}")
            if os.path.exists(temp_file):
                os.remove(temp_file)

    print("\n🎉 Terminé ! Les PDF sont dans le dossier 'cv_pdf_finaux'.")

if __name__ == "__main__":
    main()
