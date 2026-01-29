import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Etude_forme.profils import LISTE_CANDIDATS

# --- 1. FONCTIONS UTILITAIRES ---

def escape_tex(text):
    """Échappe les caractères spéciaux LaTeX (&, %, $)."""
    if not isinstance(text, str): return text
    return text.replace("&", "\\&").replace("%", "\\%").replace("$", "\\$")

def format_date(m, y):
    """Formate la date en MM/YYYY."""
    return f"{int(m):02d}/{y}"

def prepare_data(candidat):
    """
    Prépare les blocs de texte (Expérience, Education, Skills)
    pour qu'ils soient prêts à être injectés dans les templates.
    """
    infos = {k: escape_tex(v) for k, v in candidat['infos'].items()}

    # --- EXPERIENCE (BLOCK) ---
    exp_items = []
    for job in candidat['jobs']:
        desc = escape_tex(job['desc'])
        title = escape_tex(job['title'])
        emp = escape_tex(job['employer'])
        city = escape_tex(job['city'])
        dates = f"{format_date(job['fm'], job['fy'])} -- {format_date(job['tm'], job['ty'])}"

        # Format générique pour les listes
        item = f"\\textbf{{{title}}} | {emp} \\hfill {city} \\\\\n"
        item += f"\\textit{{{dates}}}\n"
        item += f"\\begin{{itemize}}[noitemsep,topsep=0pt,leftmargin=*]\n    \\item {desc}\n\\end{{itemize}}"
        exp_items.append(item)
    exp_block = "\\vspace{8pt}\n".join(exp_items)

    # --- EDUCATION (BLOCK) ---
    edu_items = []
    for edu in candidat['education']:
        title = escape_tex(edu['title'])
        org = escape_tex(edu['org'])
        dates = f"{edu['fy']} -- {edu['ty']}"
        item = f"\\textbf{{{title}}} \\hfill {dates} \\\\\n{org}, {escape_tex(edu['city'])}"
        edu_items.append(item)
    edu_block = "\\vspace{5pt}\\\\\n".join(edu_items)

    # --- LISTES SIMPLES (Skills, Langues, Intérêts) ---
    # Pour Sidebar (avec sauts de ligne)
    skills_sidebar = "\\\\\n".join([escape_tex(s['title']) for s in candidat['skills']])
    lang_sidebar = "\\\\\n".join([f"{escape_tex(l['title'])} ({escape_tex(l['desc'])})" for l in candidat['languages']])

    # Pour Corps de texte (Listes à puces ou phrases)
    skills_list_items = "\n".join([f"\\item \\textbf{{{escape_tex(s['title'])}}}: {escape_tex(s['desc'])}" for s in candidat['skills']])
    lang_list_items = "\n".join([f"\\item \\textbf{{{escape_tex(l['title'])}}}: {escape_tex(l['desc'])}" for l in candidat['languages']])

    interests_list = []
    for i in candidat['interests']:
        title = escape_tex(i['title'])
        desc = escape_tex(i.get('desc', ''))
        if desc:
            interests_list.append(f"\\textbf{{{title}}} ({desc})")
        else:
            interests_list.append(f"\\textbf{{{title}}}")

    interests_str = ", ".join(interests_list) + "."


    return {
        "infos": infos,
        "exp_block": exp_block,
        "edu_block": edu_block,
        "skills_sidebar": skills_sidebar,
        "lang_sidebar": lang_sidebar,
        "skills_list": skills_list_items,
        "lang_list": lang_list_items,
        "interests_str": interests_str
    }

# --- 2. DÉFINITION DES 6 + 1 TEMPLATES ---

TEMPLATES = {
    # ---------------------------------------------------------
    # T0: SIMPLE BASE (NOIR & BLANC, STRICT MINIMUM)
    # ---------------------------------------------------------
    "0_Simple_Base": {
        "preamble": r"""
\documentclass[a4paper,11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[margin=2.5cm]{geometry}
\usepackage{enumitem}
\pagestyle{empty}
\begin{document}
""",
        "body": r"""
\begin{{center}}
    {{\LARGE \textbf{{{infos[prenom]} {infos[nom]}}}}} \\ \vspace{{5pt}}
    {infos[ville]}, {infos[pays]} $\cdot$ {infos[phone_num]} $\cdot$ {infos[email]}
\end{{center}}

\vspace{{10pt}}
\hrule
\vspace{{10pt}}

\section*{{Profile}}
{infos[description]}

\section*{{Professional Experience}}
{exp_block}

\section*{{Education}}
{edu_block}

\section*{{Skills \& Languages}}
\begin{{itemize}}[noitemsep]
{lang_list}
{skills_list}
\end{{itemize}}

\section*{{Interests}}
{interests_str}
"""
    },

    # ---------------------------------------------------------
    # T1: CLASSIC BLUE
    # ---------------------------------------------------------
    "1_Classic": {
        "preamble": r"""
\documentclass[a4paper,10pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[default]{lato}
\usepackage[left=2cm,right=2cm,top=2cm,bottom=2cm]{geometry}
\usepackage{titlesec}
\usepackage{xcolor}
\usepackage{enumitem}
\definecolor{primary}{RGB}{0, 51, 102}
\titleformat{\section}{\Large\bfseries\color{primary}}{}{0em}{}[\titlerule]
\titlespacing{\section}{0pt}{12pt}{8pt}
\pagestyle{empty}
\begin{document}
""",
        "body": r"""
\begin{{center}}
    {{\Huge \textbf{{{infos[prenom]} {infos[nom]}}}}} \\ \vspace{{5pt}}
    {{\large \textit{{{infos[description]}}}}} \\ \vspace{{5pt}}
    {infos[ville]}, {infos[pays]} | {infos[phone_num]} | {infos[email]}
\end{{center}}
\vspace{{10pt}}

\section*{{Experience}}
{exp_block}

\section*{{Education}}
{edu_block}

\section*{{Skills \& Languages}}
\begin{{itemize}}[noitemsep,topsep=0pt]
{lang_list}
{skills_list}
\end{{itemize}}

\section*{{Interests}}
{interests_str}
"""
    },

    # ---------------------------------------------------------
    # T2: MODERN SIDEBAR (ROBUSTE TIKZ)
    # ---------------------------------------------------------
    "2_Modern_Sidebar": {
        "preamble": r"""
\documentclass[a4paper,10pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[default]{lato}
\usepackage[left=0cm,top=0cm,right=0cm,bottom=0cm]{geometry}
\usepackage{tikz}
\usepackage{xcolor}
\usepackage{enumitem}
\usepackage{setspace}
\definecolor{sidebarcolor}{RGB}{240, 240, 240}
\definecolor{textgray}{RGB}{60, 60, 60}
\pagestyle{empty}
\begin{document}
""",
        "body": r"""
\begin{{tikzpicture}}[remember picture,overlay]
    \fill[sidebarcolor] (current page.north west) rectangle ++(7cm,-\paperheight);
\end{{tikzpicture}}

\noindent
\begin{{minipage}}[t]{{6.5cm}}
    \vspace{{1.5cm}}
    \begin{{flushright}}
        \setstretch{{1.2}}
        {{\Huge \textbf{{{infos[prenom]}}}}}\\[5pt]
        {{\Huge \textbf{{{infos[nom]}}}}}\\[20pt]

        \textbf{{\uppercase{{Contact}}}}\\
        {infos[email]}\\
        {infos[phone_num]}\\
        {infos[ville]}\\[20pt]

        \textbf{{\uppercase{{Languages}}}}\\
        {lang_sidebar}\\[20pt]

        \textbf{{\uppercase{{Skills}}}}\\
        {skills_sidebar}\\[20pt]

        \textbf{{\uppercase{{Interests}}}}\\
        {interests_str}
    \end{{flushright}}
\end{{minipage}}%
\hspace{{1cm}}%
\begin{{minipage}}[t]{{12.5cm}}
    \vspace{{1.5cm}}
    \color{{textgray}}

    \section*{{\uppercase{{Profile}}}}
    \vspace{{-10pt}}\hrule\vspace{{10pt}}
    {infos[description]}

    \vspace{{15pt}}
    \section*{{\uppercase{{Experience}}}}
    \vspace{{-10pt}}\hrule\vspace{{10pt}}
    {exp_block}

    \vspace{{15pt}}
    \section*{{\uppercase{{Education}}}}
    \vspace{{-10pt}}\hrule\vspace{{10pt}}
    {edu_block}
\end{{minipage}}
"""
    },

    # ---------------------------------------------------------
    # T3: ELEGANT SERIF
    # ---------------------------------------------------------
    "3_Elegant_Serif": {
        "preamble": r"""
\documentclass[a4paper,11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{palatino}
\usepackage[left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm]{geometry}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{enumitem}
\definecolor{accent}{RGB}{128, 0, 0}
\titleformat{\section}{\Large\scshape\raggedright\color{accent}}{}{0em}{}[\titlerule]
\titlespacing{\section}{0pt}{15pt}{10pt}
\pagestyle{empty}
\begin{document}
""",
        "body": r"""
\begin{{center}}
    {{\huge \textsc{{{infos[prenom]} {infos[nom]}}}}} \\ \vspace{{5pt}}
    {{\small {infos[ville]} $\cdot$ {infos[phone_num]} $\cdot$ {infos[email]}}}
\end{{center}}
\vspace{{10pt}}

\section{{Profile}}
{infos[description]}

\section{{Professional Experience}}
{exp_block}

\section{{Education}}
{edu_block}

\section{{Skills \& Languages}}
\begin{{itemize}}[noitemsep]
{lang_list}
{skills_list}
\end{{itemize}}

\section{{Interests}}
{interests_str}
"""
    },

    # ---------------------------------------------------------
    # T4: MINIMALIST TECH
    # ---------------------------------------------------------
    "4_Minimalist_Tech": {
        "preamble": r"""
\documentclass[a4paper,10pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{geometry}
\usepackage{enumitem}
\geometry{margin=1.5cm}
\usepackage{titlesec}
\titleformat{\section}{\large\bfseries\uppercase}{}{0em}{}[\titlerule]
\titlespacing{\section}{0pt}{10pt}{5pt}
\pagestyle{empty}
\begin{document}
""",
        "body": r"""
\noindent {{\LARGE \textbf{{{infos[prenom]} {infos[nom]}}}}} \\
{infos[ville]}, {infos[pays]} | {infos[phone_num]} | {infos[email]}

\vspace{{10pt}}
\noindent \textbf{{SUMMARY}} \\
{infos[description]}

\section{{EXPERIENCE}}
{exp_block}

\section{{EDUCATION}}
{edu_block}

\section{{SKILLS \& LANGUAGES}}
\begin{{itemize}}[noitemsep]
{lang_list}
{skills_list}
\end{{itemize}}

\section{{INTERESTS}}
{interests_str}
"""
    },

    # ---------------------------------------------------------
    # T5: HEADER BOX (VERT)
    # ---------------------------------------------------------
    "5_Header_Box": {
        "preamble": r"""
\documentclass[a4paper,10pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[default]{lato}
\usepackage[top=0cm,bottom=2cm,left=2cm,right=2cm]{geometry}
\usepackage{xcolor}
\usepackage{tcolorbox}
\usepackage{enumitem}
\definecolor{headercol}{RGB}{23, 75, 60}
\pagestyle{empty}
\begin{document}
""",
        "body": r"""
\begin{{tcolorbox}}[colback=headercol,colframe=headercol,sharp corners, width=\paperwidth, enlarge left by=-2cm, height=3.5cm, valign=center]
    \centering
    \color{{white}}
    {{\Huge \textbf{{{infos[prenom]} {infos[nom]}}}}} \\[5pt]
    {{\large {infos[description]}}} \\[5pt]
    {infos[ville]} $\bullet$ {infos[phone_num]} $\bullet$ {infos[email]}
\end{{tcolorbox}}

\vspace{{0.5cm}}

\section*{{Experience}}
{exp_block}

\section*{{Education}}
{edu_block}

\section*{{Skills \& Languages}}
\begin{{itemize}}[noitemsep,topsep=0pt]
{lang_list}
{skills_list}
\end{{itemize}}

\section*{{Interests}}
{interests_str}
"""
    },

    # ---------------------------------------------------------
    # T6: COMPACT HORIZONTAL
    # ---------------------------------------------------------
    "6_Compact_Lines": {
        "preamble": r"""
\documentclass[a4paper,10pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[margin=1.8cm]{geometry}
\usepackage{titling}
\usepackage{enumitem}
\setlength{\parindent}{0pt}
\pagestyle{empty}
\begin{document}
""",
        "body": r"""
{{\huge \textbf{{{infos[prenom]} {infos[nom]}}}}}\\[5pt]
{infos[ville]} \hfill {infos[email]} \\
{infos[phone_num]} \hfill {infos[nationalite]}

\vspace{{10pt}}
\hrule
\vspace{{10pt}}

\textbf{{PROFILE}} \\
{infos[description]}

\vspace{{10pt}}
\hrule
\vspace{{10pt}}

\textbf{{EXPERIENCE}} \\
{exp_block}

\vspace{{10pt}}
\hrule
\vspace{{10pt}}

\textbf{{EDUCATION}} \\
{edu_block}

\vspace{{10pt}}
\hrule
\vspace{{10pt}}

\textbf{{SKILLS \& LANGUAGES}} \\
\begin{{itemize}}[noitemsep,topsep=0pt]
{lang_list}
{skills_list}
\end{{itemize}}

\vspace{{10pt}}
\hrule
\vspace{{10pt}}

\textbf{{INTERESTS}} \\
{interests_str}
"""
    }
}

# --- 3. EXÉCUTION DU SCRIPT ---

script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "scripts_latex")
os.makedirs(output_dir, exist_ok=True)

print("Génération des fichiers LaTeX en cours...")

for t_name, t_content in TEMPLATES.items():
    full_latex = t_content["preamble"].strip() + "\n"

    for i, candidat in enumerate(LISTE_CANDIDATS):
        # Préparation des données pour ce candidat
        data = prepare_data(candidat)

        # Injection dans le template
        # On utilise **data pour passer le dictionnaire comme arguments nommés
        full_latex += t_content["body"].format(**data)

        # Ajout du saut de page sauf pour le dernier
        if i < len(LISTE_CANDIDATS) - 1:
            full_latex += "\n\\newpage\n"

    full_latex += "\n\\end{document}"

    # Écriture du fichier
    filename = f"{output_dir}/CV_Book_{t_name}.tex"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_latex)

    print(f" -> {filename} créé.")

print("\nTerminé ! Vous avez 6 fichiers .tex contenant chacun les 10 CVs.")
