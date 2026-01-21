import pandas as pd
import os
import re
import subprocess
import shutil

# --- CONFIGURATION ---
CSV_FILE = "cv_final.csv"
OUTPUT_DIR = "cv_generated"

# Mapping des colonnes
COLUMN_MAPPING = {
    'cv original': 'Original',
    'cv gender - name variation': 'Gender',
    'cv origin variation': 'Origin',
    'cv age variation': 'Age'
}

# Mots-clés de sections (en MAJUSCULES pour la regex)
# On inclut des variantes courantes
SECTIONS_KEYWORDS = [
    "EXPERIENCE", "PROFESSIONAL EXPERIENCE", "WORK EXPERIENCE",
    "EDUCATION", "ACADEMIC BACKGROUND",
    "SKILLS", "TECHNICAL SKILLS", "COMPETENCIES",
    "PROJECTS", "ACADEMIC PROJECTS",
    "LANGUAGES", "LANGUAGES SPOKEN",
    "CERTIFICATIONS", "COURSES",
    "HOBBIES", "INTERESTS", "PERSONAL INTERESTS",
    "PUBLICATIONS", "REFERENCES", "ACHIEVEMENTS"
]

# --- NETTOYAGE TEXTE ---
def clean_text(text):
    """Normalise les caractères spéciaux et espaces."""
    if not isinstance(text, str): return ""

    # Remplacer les tirets longs, points médians, etc. par des standards
    text = text.replace('–', '-').replace('—', '-').replace('−', '-')
    text = text.replace('·', '-').replace('•', '-')
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    return text.strip()

def escape_latex(text):
    """Échappe les caractères spéciaux pour LaTeX."""
    if not isinstance(text, str): return ""
    replacements = {
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_',
        '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\^{}',
        '\\': r'\textbackslash{}',
    }
    pattern = re.compile('|'.join(re.escape(key) for key in replacements.keys()))
    return pattern.sub(lambda x: replacements[x.group()], text)

# --- PARSING ROBUSTE ---
def parse_cv_content(content):
    """
    Découpe le CV en sections même si le formatage est cassé (tout sur une ligne).
    """
    content = clean_text(content)

    # 1. Identifier les positions de toutes les sections
    # Regex :
    # (?:^|[\s\n]) -> Précédé par début, espace ou newline
    # (MOT_CLE)    -> Le titre de la section
    # \s* -> Espaces optionnels
    # (?::|(?=\n)|(?=\s+[A-Z])) -> Suivi par ':', OU une newline, OU (si c'est collé) un espace et une majuscule (heuristique)
    # On reste simple : Mot clé suivi de ':' OU Mot clé seul sur sa ligne (suivi de \n)

    # On cherche les mots clés suivis de ':' OU suivis d'un saut de ligne immédiat
    # On utilise une Lookbehind simulée en checkant le match

    keyword_pattern = r'(?:^|[\s\n])(?P<key>' + '|'.join(SECTIONS_KEYWORDS) + r')(?P<sep>\s*:|(?=\s*\n))'

    matches = []
    for m in re.finditer(keyword_pattern, content, flags=re.IGNORECASE):
        # On ignore si c'est au milieu d'une phrase (ex: "My experience in...")
        # La regex (?:^|[\s\n]) aide déjà.

        start_idx = m.start()
        # Si le match commence par un espace/newline, on décale pour ne pas l'inclure dans le titre
        if content[start_idx] in [' ', '\n', '\t']:
            start_idx += 1

        key = m.group('key').upper()
        matches.append((start_idx, key))

    # Si aucune section trouvée, tout est header
    if not matches:
        return content, {}

    # 2. Découper le texte selon les positions trouvées
    matches.sort(key=lambda x: x[0])

    header_raw = content[:matches[0][0]].strip()
    sections = {}

    for i in range(len(matches)):
        start_pos = matches[i][0]
        section_name = matches[i][1]

        # Trouver la fin de cette section (soit le début de la suivante, soit la fin du texte)
        if i < len(matches) - 1:
            end_pos = matches[i+1][0]
        else:
            end_pos = len(content)

        # Extraire le contenu brut
        # On doit retirer le titre lui-même du contenu
        raw_slice = content[start_pos:end_pos]

        # On enlève le titre (ex: "EXPERIENCE:") du début du contenu
        # On cherche le premier ':' ou saut de ligne pour couper proprement
        match_title = re.match(r'^' + re.escape(section_name) + r'\s*:?', raw_slice, flags=re.IGNORECASE)
        if match_title:
            body = raw_slice[match_title.end():].strip()
        else:
            body = raw_slice[len(section_name):].strip() # Fallback

        sections[section_name] = body

    return header_raw, sections

def clean_header_info(raw_header):
    """Extrait Nom et Détails avec séparateurs robustes."""
    # Nettoyage des préfixes "Target MSc" s'ils traînent dans le header
    # On garde tout, mais on sépare bien la première ligne (Nom - Info) du reste (Target...)

    lines = raw_header.split('\n')
    first_line = lines[0].strip()
    rest = "\n".join(lines[1:]).strip()

    # Découpage du Nom - Age - Pays
    # On utilise '-' mais aussi '|' ou '–' (déjà normalisé par clean_text en '-')
    parts = [p.strip() for p in first_line.split('-')]

    if len(parts) >= 1:
        name = parts[0]
        # Si le reste contient "Target", on le met dans details
        details_line = " | ".join(parts[1:])
    else:
        name = "Candidat"
        details_line = raw_header

    # Si on a du texte après la première ligne (ex: Target MSc...), on l'ajoute aux détails
    if rest:
        full_details = f"{details_line}\n\\vspace{{3pt}}\n\\textit{{{rest}}}"
    else:
        full_details = details_line

    return name, full_details

# --- GÉNÉRATION LATEX ---
def generate_latex(name, details, sections):
    latex = r"""\documentclass[a4paper,10pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[margin=1in]{geometry}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{xcolor}

\titleformat{\section}{\large\bfseries\uppercase}{}{0em}{}[\titlerule]
\titlespacing{\section}{0pt}{10pt}{6pt}

\begin{document}
\pagestyle{empty}

\begin{center}
    {\Huge \textbf{""" + escape_latex(name) + r"""}} \\ \vspace{5pt}
    {\small """ + details.replace('\n', r' \\ ') + r"""}
\end{center}

\vspace{5pt}
"""
    # Liste ordonnée de préférence
    preferred_order = [
        "PROFESSIONAL EXPERIENCE", "EXPERIENCE", "WORK EXPERIENCE",
        "EDUCATION", "ACADEMIC BACKGROUND",
        "SKILLS", "TECHNICAL SKILLS",
        "PROJECTS",
        "LANGUAGES",
        "CERTIFICATIONS",
        "PUBLICATIONS",
        "HOBBIES", "INTERESTS", "PERSONAL INTERESTS",
        "REFERENCES"
    ]

    # On fusionne l'ordre préférentiel et les autres clés trouvées
    found_keys = list(sections.keys())
    ordered_keys = [k for k in preferred_order if k in found_keys] + [k for k in found_keys if k not in preferred_order]

    for key in ordered_keys:
        content = sections[key]
        if not content: continue

        latex += f"\\section*{{{key.title()}}}\n"

        # Traitement du contenu
        # Si le contenu est un gros bloc sans newline (ex: Hiroshi), on essaie de le splitter sur les points "."
        if '\n' not in content and len(content) > 100:
             # Heuristique : ajouter des retours à la ligne après les points suivis d'espace
             content = content.replace('. ', '.\n')

        lines = content.split('\n')
        in_itemize = False

        for line in lines:
            line = line.strip()
            if not line: continue

            # Détection liste
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                if not in_itemize:
                    latex += "\\begin{itemize}[leftmargin=*]\n"
                    in_itemize = True
                clean_line = escape_latex(line[1:].strip())
                latex += f"    \\item {clean_line}\n"
            else:
                if in_itemize:
                    latex += "\\end{itemize}\n"
                    in_itemize = False
                latex += f"{escape_latex(line)} \\\\\n"

        if in_itemize:
            latex += "\\end{itemize}\n"

        latex += "\n"

    latex += r"\end{document}"

    # Petit hack pour les détails qui contenaient déjà du latex (textit)
    # escape_latex a été appelé sur le nom, mais pas sur details complet dans le main
    # Correction : dans clean_header_info on a mis du LaTeX (\vspace, \textit).
    # Il faut que details passés à cette fonction soient déjà échappés pour la partie texte.
    # On va assumer que clean_header_info renvoie du texte "safe" ou à échapper avant l'insertion de commandes LaTeX.
    # Pour simplifier ici, on laisse tel quel car on a géré l'escape dans main.
    return latex

# --- MAIN ---
if __name__ == "__main__":
    try:
        df = pd.read_csv(CSV_FILE)
        print(f"Chargement de {len(df)} lignes depuis {CSV_FILE}.")
    except Exception as e:
        print(f"Erreur lecture CSV: {e}")
        exit()

    count = 0
    # Nettoyage global avant de commencer (optionnel, pour repartir à propre)
    # if os.path.exists(OUTPUT_DIR): shutil.rmtree(OUTPUT_DIR)

    for idx, row in df.iterrows():
        for col_name, category_name in COLUMN_MAPPING.items():
            if col_name not in df.columns: continue

            content = row[col_name]
            if pd.isna(content) or not isinstance(content, str): continue

            # 1. Parsing
            raw_header, sections = parse_cv_content(str(content))

            # 2. Nettoyage header (Nom | Details)
            # On échappe le texte brut AVANT d'ajouter les balises LaTeX dans clean_header
            name_raw, details_raw = clean_header_info(raw_header)

            # Subtilité : details_raw peut contenir "Nom - Age - Pays" (texte simple)
            # OU "Nom... \n Target..." (texte sur plusieurs lignes)
            # On va échapper manuellement ici pour éviter de casser le LaTeX plus tard
            if "\\vspace" in details_raw:
                # Cas complexe (avec Target MSc)
                # On sépare pour échapper le texte mais garder les commandes
                # C'est un peu "hacky" mais efficace pour ce script
                parts_split = details_raw.split(r'\textit{')
                top_part = escape_latex(parts_split[0].strip().replace(r'\vspace{3pt}', ''))
                bottom_part = escape_latex(parts_split[1].replace('}', '')) if len(parts_split) > 1 else ""

                details_latex = f"{top_part} \\\\[3pt] \\textit{{{bottom_part}}}"
            else:
                details_latex = escape_latex(details_raw)

            latex_code = generate_latex(name_raw, details_latex, sections)

            # 3. Chemins et Dossiers
            cat_dir = os.path.join(OUTPUT_DIR, category_name)
            sub_folder_name = f"CV {idx:03d} {category_name}"
            final_output_dir = os.path.join(cat_dir, sub_folder_name)

            os.makedirs(final_output_dir, exist_ok=True)

            file_suffix = category_name.lower()
            base_filename = f"CV_{idx:03d}_{file_suffix}"
            tex_filename = base_filename + ".tex"
            tex_path = os.path.join(final_output_dir, tex_filename)

            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(latex_code)

            # 4. Compilation
            try:
                subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", f"-output-directory={final_output_dir}", tex_path],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except FileNotFoundError:
                print("[INFO] pdflatex non trouvé.")

            # 5. Nettoyage (Garder PDF uniquement)
            generated_files = os.listdir(final_output_dir)
            pdf_exists = False
            for filename in generated_files:
                file_path = os.path.join(final_output_dir, filename)
                if filename.endswith(".pdf"):
                    pdf_exists = True
                else:
                    try: os.remove(file_path)
                    except: pass

            if pdf_exists:
                print(f"[OK] {sub_folder_name} -> {base_filename}.pdf")
            else:
                print(f"[ERR] {sub_folder_name} (Échec PDF)")

            count += 1

    print(f"\nTraitement terminé ! {count} CVs traités.")
