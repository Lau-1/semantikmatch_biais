import pandas as pd
import re
import os
import subprocess
import shutil
import sys

# --- CONFIGURATION ---
INPUT_CSV = 'data.csv'
OUTPUT_DIR = 'cv_moderncv_output'

SECTION_KEYWORDS = [
    "EDUCATION",
    "PROFESSIONAL EXPERIENCE", "EXPERIENCE & PROJECTS", "EXPERIENCE & VOLUNTEERING",
    "SKILLS & LANGUAGES", "TECHNICAL SKILLS", "SKILLS",
    "LANGUAGES", "SOFT SKILLS",
    "INTERESTS"
]

def check_latex_requirements():
    """Vérifie pdflatex et moderncv."""
    if shutil.which('pdflatex') is None:
        print("❌ ERREUR CRITIQUE : 'pdflatex' n'est pas trouvé.")
        return False

    # Vérification optionnelle de la classe moderncv via kpsewhich (si disponible)
    if shutil.which('kpsewhich'):
        try:
            result = subprocess.run(['kpsewhich', 'moderncv.cls'], capture_output=True, text=True)
            if not result.stdout.strip():
                print("⚠️  ATTENTION : La classe 'moderncv.cls' semble absente.")
                print("   -> Si le script échoue, installez le package 'moderncv' via votre gestionnaire LaTeX (MiKTeX Console ou TeX Live Manager).")
        except:
            pass
    return True

def clean_text_for_latex(text):
    """Nettoie et échappe le texte pour éviter les erreurs de compilation."""
    if not isinstance(text, str): return ""

    # 1. Remplacement des caractères typographiques complexes par des simples
    text = text.replace('–', '-').replace('—', '-') # Tirets cadratins
    text = text.replace('’', "'").replace('“', '"').replace('”', '"')

    # 2. Échappement LaTeX standard
    chars = {
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_',
        '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'
    }
    pattern = re.compile('|'.join(re.escape(key) for key in chars.keys()))
    text = pattern.sub(lambda x: chars[x.group()], text)

    return text.strip()

def extract_contact_info(details_text):
    """Extrait email et tel, et nettoie l'adresse."""
    # Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', details_text)
    email = email_match.group(0) if email_match else ""

    # Téléphone
    phone_match = re.search(r'(?:\+33|0)\s*[1-9](?:[\s\.-]*\d{2}){4}', details_text)
    phone = phone_match.group(0) if phone_match else ""

    # Nettoyage pour obtenir l'adresse
    clean_details = details_text
    if email: clean_details = clean_details.replace(email, "")
    if phone: clean_details = clean_details.replace(phone, "")

    # Enlever les séparateurs de début/fin (tirets, virgules)
    clean_details = re.sub(r'^[\s\-–,]*', '', clean_details)
    clean_details = re.sub(r'[\s\-–,]*$', '', clean_details)

    return email, phone, clean_details.strip()

def format_moderncv_content(text):
    lines = text.strip().split('\n')
    formatted_lines = []

    # Regex améliorée : Cherche une date qui finit par une année ou 'Present'
    # Ex: "June - Aug 2025" ou "2023-2026"
    date_pattern = r'^((?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Summer|Winter|Spring|Fall)\s*)?[\d\s\-]*(?:Present|\d{4}))\s+(.*)'

    for line in lines:
        line = line.strip()
        if not line: continue

        if line.startswith("- ") or line.startswith("• "):
            clean_line = clean_text_for_latex(line[1:].strip())
            formatted_lines.append(f"\\cvlistitem{{{clean_line}}}")

        elif re.match(date_pattern, line):
            match = re.match(date_pattern, line)
            date_part = clean_text_for_latex(match.group(1).strip())
            title_part = clean_text_for_latex(match.group(2).strip())
            # Format ModernCV : {Date}{Titre}{}{}{}{}
            formatted_lines.append(f"\\cventry{{{date_part}}}{{{title_part}}}{{}}{{}}{{}}{{}}")

        else:
            formatted_lines.append(f"\\cvitem{{}}{{{clean_text_for_latex(line)}}}")

    return "\n".join(formatted_lines)

def main():
    if not check_latex_requirements():
        sys.exit(1)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if not os.path.exists(INPUT_CSV):
        print("⚠️ 'data.csv' introuvable. Veuillez relancer le script de génération de données.")
        sys.exit(1)

    df = pd.read_csv(INPUT_CSV)
    print(f"🚀 Traitement de {len(df)} CVs (Mode Debug Actif)...")

    # Template ModernCV robuste
    latex_template = r"""
    \documentclass[11pt,a4paper,sans]{moderncv}
    \moderncvstyle{classic}
    \moderncvcolor{blue}
    \usepackage[utf8]{inputenc}
    \usepackage[scale=0.75]{geometry}

    % Infos
    \firstname{VAR_FIRSTNAME}
    \familyname{VAR_LASTNAME}
    \title{VAR_TITLE}
    \address{VAR_ADDRESS}{}{} % Format 3 arguments (standard récent)
    \mobile{VAR_PHONE}
    \email{VAR_EMAIL}

    \begin{document}
    \makecvtitle
    VAR_BODY
    \end{document}
    """

    for index, row in df.iterrows():
        try:
            text = row['cv original']
            lines = text.split('\n')
            full_name = clean_text_for_latex(lines[0].strip())

            # Nom/Prénom
            name_parts = full_name.split(' ')
            if len(name_parts) > 1:
                lastname = name_parts[-1]
                firstname = " ".join(name_parts[:-1])
            else:
                lastname = full_name
                firstname = ""

            # Titre & Contact
            title_line = ""
            details_raw = ""
            if len(lines) > 1:
                if any(x in lines[1] for x in ["Candidate", "Student", "Grande École"]):
                    title_line = clean_text_for_latex(lines[1].strip())
                    if len(lines) > 2: details_raw = lines[2].strip()
                else:
                    details_raw = lines[1].strip()

            email, phone, address = extract_contact_info(details_raw)
            address = clean_text_for_latex(address)

            # Sections
            pattern = r'\n(' + '|'.join(SECTION_KEYWORDS) + r')\n'
            parts = re.split(pattern, text, flags=re.IGNORECASE)

            body_content = ""
            for i in range(1, len(parts), 2):
                section_title = clean_text_for_latex(parts[i].strip().title())
                section_content = parts[i+1]
                formatted_content = format_moderncv_content(section_content)
                body_content += f"\\section{{{section_title}}}\n{formatted_content}\n"

            # Remplissage
            final_tex = latex_template.replace("VAR_FIRSTNAME", firstname)
            final_tex = final_tex.replace("VAR_LASTNAME", lastname)
            final_tex = final_tex.replace("VAR_TITLE", title_line)
            final_tex = final_tex.replace("VAR_ADDRESS", address)
            final_tex = final_tex.replace("VAR_PHONE", phone)
            final_tex = final_tex.replace("VAR_EMAIL", email)
            final_tex = final_tex.replace("VAR_BODY", body_content)

            # Fichiers
            safe_name = re.sub(r'[^a-zA-Z0-9]', '_', full_name)
            filename_base = f"ModernCV_{safe_name}"
            tex_file = os.path.join(OUTPUT_DIR, f"{filename_base}.tex")

            with open(tex_file, "w", encoding='utf-8') as f:
                f.write(final_tex)

            # Compilation avec capture d'erreur
            process = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-output-directory", OUTPUT_DIR, tex_file],
                capture_output=True, # Capture stdout et stderr
                text=True
            )

            if process.returncode == 0:
                print(f"✅ Succès : {filename_base}.pdf")
                # Nettoyage
                for ext in ['.log', '.aux', '.out']:
                    temp = os.path.join(OUTPUT_DIR, f"{filename_base}{ext}")
                    if os.path.exists(temp): os.remove(temp)
            else:
                print(f"❌ Échec pour {full_name}")
                # Affiche les 10 dernières lignes du log d'erreur pour comprendre
                print("--- Extrait de l'erreur LaTeX ---")
                print("\n".join(process.stdout.splitlines()[-15:])) # Souvent l'erreur est à la fin de stdout/log
                print("---------------------------------")

        except Exception as e:
            print(f"⚠️ Erreur script python pour {index}: {e}")

    print(f"\nTerminé. Vérifiez le dossier '{OUTPUT_DIR}'")

if __name__ == "__main__":
    main()
