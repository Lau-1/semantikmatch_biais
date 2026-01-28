import os

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

# --- 2. DÉFINITION DES 6 TEMPLATES ---

# --- 2. DÉFINITION DES TEMPLATES (AVEC LE NOUVEAU TEMPLATE 0) ---

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

output_dir = "CV_BOOKS_OUTPUT"
os.makedirs(output_dir, exist_ok=True)

LISTE_CANDIDATS = [
    # --- CANDIDAT 1 : Clara MOREL ---
    {
        "infos": {
            "prenom": "Clara",
            "nom": "MOREL",
            "description": "Analytical and structured student with a strong interest in strategy and organizational performance.",
            "genre": "Female",
            "nationalite": "French",
            "email": "clara.morel@email.com",
            "phone_pays": "France",
            "phone_num": "645218934",
            "ville": "Lyon",
            "pays": "France"
        },
        "jobs": [
            {
                "title": "Strategy Analyst Intern", "employer": "Roland Berger", "city": "Paris", "country": "France",
                "desc": "Conducted market and competitor analysis for industrialclients. Built Excel models and PowerPoint decks for seniorconsultants. Participated in client interviews and synthesis workshops.",
                "fd": "1", "fm": "6", "fy": "2024", "td": "1", "tm": "12", "ty": "2024"
            },
            {
                "title": "Student Consultant", "employer": "emlyon Junior Conseil", "city": "Lyon", "country": "France",
                "desc": "Delivered consulting missions for SMEs (market sizing, pricing). Led a team of 4 students on a retail optimization project.",
                "fd": "1", "fm": "9", "fy": "2023", "td": "1", "tm": "5", "ty": "2024"
            }
        ],
        "education": [
            {
                "title": "Bachelor in Management (Global BBA)", "org": "emlyon business school", "city": "Lyon", "country": "France",
                "fd": "1", "fm": "9", "fy": "2022", "td": "1", "tm": "6", "ty": "2025"
            },
            {
                "title": "Baccalauréat (Maths & Economics)", "org": "Lycée du Parc", "city": "Lyon", "country": "France",
                "fd": "1", "fm": "9", "fy": "2021", "td": "1", "tm": "6", "ty": "2022"
            }
        ],
        "skills": [
            {"title": "Business & Strategy", "desc": "Market Analysis, Competitive Intelligence, Problem Solving."},
            {"title": "IT Skills", "desc": "Excel (Advanced), PowerPoint (Expert)."}
        ],
        "languages": [
            {"title": "English", "desc": "C1 Level"},
            {"title": "Spanish", "desc": "B2 Level"}
        ],
        "interests": [
            {"title": "Debating", "desc": "National competitions."},
            {"title": "Sports", "desc": "Long-distance running."},
            {"title": "Culture", "desc": "Economic podcasts."}
        ]
    },

    # --- CANDIDAT 2 : Hugo LEMAIRE ---
    {
        "infos": {
            "prenom": "Hugo",
            "nom": "LEMAIRE",
            "description": "Finance-oriented economics student with a strong quantitative background aiming for investment banking.",
            "genre": "Male",
            "nationalite": "French",
            "email": "hugo.lemaire@email.com",
            "phone_pays": "France",
            "phone_num": "678124409",
            "ville": "Paris",
            "pays": "France"
        },
        "jobs": [
            {
                "title": "Corporate Finance Intern", "employer": "Société Générale CIB", "city": "Paris", "country": "France",
                "desc": "Assisted in financial modeling and company valuation. Prepared pitchbooks and market analysis for M&A transactions. Conducted comparable companies and precedent transactions analyses.",
                "fd": "1", "fm": "6", "fy": "2024", "td": "1", "tm": "8", "ty": "2024"
            },
            {
                "title": "Private Equity Analyst (Part-time)", "employer": "Student Investment Fund", "city": "Paris", "country": "France",
                "desc": "Analyzed investment opportunities in SMEs. Built LBO models and investment memos.",
                "fd": "1", "fm": "1", "fy": "2024", "td": "1", "tm": "5", "ty": "2024"
            }
        ],
        "education": [
            {
                "title": "Bachelor in Economics", "org": "University Paris-Dauphine", "city": "Paris", "country": "France",
                "fd": "1", "fm": "9", "fy": "2021", "td": "1", "tm": "6", "ty": "2024"
            },
            {
                "title": "Baccalauréat (Maths & Physics)", "org": "Lycée Saint-Louis", "city": "Paris", "country": "France",
                "fd": "1", "fm": "9", "fy": "2020", "td": "1", "tm": "6", "ty": "2021"
            }
        ],
        "skills": [
            {"title": "Finance", "desc": "Valuation, Financial Modeling, Accounting."},
            {"title": "IT Skills", "desc": "Excel (Advanced), VBA (Intermediate)."}
        ],
        "languages": [
            {"title": "English", "desc": "C1 - IELTS 7.5"},
            {"title": "French", "desc": "Native"}
        ],
        "interests": [
            {"title": "Investing", "desc": "Stock market investing."},
            {"title": "Sports", "desc": "Chess, marathon training."}
        ]
    },

    # --- CANDIDAT 3 : Sarah BENALI ---
    {
        "infos": {
            "prenom": "Sarah",
            "nom": "BENALI",
            "description": "Creative and analytical marketing student with strong interest in brand strategy and consumer behavior.",
            "genre": "Female",
            "nationalite": "French",
            "email": "sarah.benali@email.com",
            "phone_pays": "France",
            "phone_num": "691335672",
            "ville": "Marseille",
            "pays": "France"
        },
        "jobs": [
            {
                "title": "Marketing Intern", "employer": "L'Oréal France", "city": "Paris", "country": "France",
                "desc": "Assisted brand managers in the preparation and launch of new skincare products. Analyzed sales performance and campaign KPIs using Excel and internal dashboards. Coordinated with creative agencies and influencers for digital campaigns. Conducted competitive analysis and consumer trend monitoring.",
                "fd": "1", "fm": "6", "fy": "2024", "td": "1", "tm": "12", "ty": "2024"
            },
            {
                "title": "Digital Marketing Assistant", "employer": "E-commerce Startup", "city": "Marseille", "country": "France",
                "desc": "Managed social media content calendars (Instagram, TikTok). Monitored online performance metrics and engagement rates. Supported SEO optimization and newsletter campaigns.",
                "fd": "1", "fm": "9", "fy": "2023", "td": "1", "tm": "5", "ty": "2024"
            }
        ],
        "education": [
            {
                "title": "Bachelor in Business Administration", "org": "KEDGE Business School", "city": "Marseille", "country": "France",
                "fd": "1", "fm": "9", "fy": "2022", "td": "1", "tm": "6", "ty": "2025"
            },
            {
                "title": "Baccalauréat (Economics)", "org": "Lycée Thiers", "city": "Marseille", "country": "France",
                "fd": "1", "fm": "9", "fy": "2021", "td": "1", "tm": "6", "ty": "2022"
            }
        ],
        "skills": [
            {"title": "Marketing", "desc": "Brand Strategy, Market Research, Campaign Analysis."},
            {"title": "IT Skills", "desc": "Excel (Advanced), Power BI, Google Analytics, Canva."}
        ],
        "languages": [
            {"title": "English", "desc": "C1 - TOEIC 945"},
            {"title": "Arabic", "desc": "Native"}
        ],
        "interests": [
            {"title": "Photography", "desc": "Lifestyle and travel portfolio on Instagram."},
            {"title": "Trends", "desc": "Fashion, consumer trends, contemporary art."}
        ]
    },

    # --- CANDIDAT 4 : Thomas GIRARD ---
    {
        "infos": {
            "prenom": "Thomas",
            "nom": "GIRARD",
            "description": "Entrepreneurial-minded student with practical experience in startup co-founding and business development.",
            "genre": "Male",
            "nationalite": "French",
            "email": "thomas.girard@email.com",
            "phone_pays": "France",
            "phone_num": "622489105",
            "ville": "Nantes",
            "pays": "France"
        },
        "jobs": [
            {
                "title": "Co-founder & Operations Manager", "employer": "GreenMove (Student Startup)", "city": "Nantes", "country": "France",
                "desc": "Co-founded a sustainable mobility startup offering shared electric bikes for students. Managed daily operations and partnerships with local institutions. Built financial forecasts and monitored monthly cash flow. Led customer acquisition campaigns, reaching over 1,000 registered users.",
                "fd": "1", "fm": "1", "fy": "2023", "td": "1", "tm": "1", "ty": "2026"
            },
            {
                "title": "Business Development Intern", "employer": "Startup Incubator", "city": "Nantes", "country": "France",
                "desc": "Supported early-stage startups in market analysis and go-to-market strategy. Assisted entrepreneurs in preparing pitch decks for investors. Participated in mentoring sessions and demo days.",
                "fd": "1", "fm": "6", "fy": "2023", "td": "1", "tm": "8", "ty": "2023"
            }
        ],
        "education": [
            {
                "title": "Bachelor in Economics & Management", "org": "University of Nantes", "city": "Nantes", "country": "France",
                "fd": "1", "fm": "9", "fy": "2021", "td": "1", "tm": "6", "ty": "2024"
            },
            {
                "title": "Baccalauréat (Maths & Economics)", "org": "Lycée Clémenceau", "city": "Nantes", "country": "France",
                "fd": "1", "fm": "9", "fy": "2020", "td": "1", "tm": "6", "ty": "2021"
            }
        ],
        "skills": [
            {"title": "Entrepreneurship", "desc": "Business Development, Financial Forecasting, Project Management."},
            {"title": "IT Skills", "desc": "Excel (Advanced), Notion, Trello."}
        ],
        "languages": [
            {"title": "English", "desc": "C1 Level"},
            {"title": "French", "desc": "Native"}
        ],
        "interests": [
            {"title": "Entrepreneurship", "desc": "Startup communities and innovation events."},
            {"title": "Sports", "desc": "Competitive sailing (6 years)."}
        ]
    },

    # --- CANDIDAT 5 : Inès ROBERT ---
    {
        "infos": {
            "prenom": "Inès",
            "nom": "ROBERT",
            "description": "Economics student interested in public policy, management, and economic regulation with think tank experience.",
            "genre": "Female",
            "nationalite": "French",
            "email": "ines.robert@email.com",
            "phone_pays": "France",
            "phone_num": "637841962",
            "ville": "Paris",
            "pays": "France"
        },
        "jobs": [
            {
                "title": "Policy Research Assistant", "employer": "French Economic Think Tank", "city": "Paris", "country": "France",
                "desc": "Conducted literature reviews and data analysis for policy briefs. Contributed to reports on labor market reforms and public spending efficiency. Participated in stakeholder interviews and policy workshops.",
                "fd": "1", "fm": "9", "fy": "2024", "td": "1", "tm": "2", "ty": "2025"
            },
            {
                "title": "Public Affairs Intern", "employer": "Ministry of Economy and Finance", "city": "Paris", "country": "France",
                "desc": "Assisted senior analysts in economic impact assessments. Prepared briefing notes and synthesis documents for internal use. Monitored legislative developments related to economic policy.",
                "fd": "1", "fm": "6", "fy": "2024", "td": "1", "tm": "8", "ty": "2024"
            }
        ],
        "education": [
            {
                "title": "Bachelor in Economics & Social Sciences", "org": "Sciences Po Paris", "city": "Paris", "country": "France",
                "fd": "1", "fm": "9", "fy": "2022", "td": "1", "tm": "6", "ty": "2025"
            },
            {
                "title": "Baccalauréat (Economics)", "org": "Lycée Henri-IV", "city": "Paris", "country": "France",
                "fd": "1", "fm": "9", "fy": "2021", "td": "1", "tm": "6", "ty": "2022"
            }
        ],
        "skills": [
            {"title": "Public Policy", "desc": "Policy Evaluation, Economic Analysis, Report Writing."},
            {"title": "IT Skills", "desc": "Excel (Advanced), Stata (Intermediate)."}
        ],
        "languages": [
            {"title": "English", "desc": "C1 Level"},
            {"title": "German", "desc": "B2 Level"}
        ],
        "interests": [
            {"title": "Public Debate", "desc": "Economic conferences and policy forums."},
            {"title": "Volunteering", "desc": "Tutor for underprivileged high school students."}
        ]
    },

    # --- CANDIDAT 6 : Louis CARON ---
    {
        "infos": {
            "prenom": "Louis",
            "nom": "CARON",
            "description": "Quantitative-oriented student with a background in applied mathematics, statistics, and business analytics.",
            "genre": "Male",
            "nationalite": "French",
            "email": "louis.caron@email.com",
            "phone_pays": "France",
            "phone_num": "659027741",
            "ville": "Grenoble",
            "pays": "France"
        },
        "jobs": [
            {
                "title": "Data Analyst Intern", "employer": "Retail Analytics Company", "city": "Lyon", "country": "France",
                "desc": "Cleaned and analyzed large customer datasets using Python and SQL. Built dashboards to support marketing and pricing decisions. Presented insights to non-technical stakeholders.",
                "fd": "1", "fm": "6", "fy": "2024", "td": "1", "tm": "9", "ty": "2024"
            },
            {
                "title": "Business Analytics Project", "employer": "Academic Team", "city": "Grenoble", "country": "France",
                "desc": "Worked in a team to analyze sales performance for a retail chain. Developed forecasting models and recommendations for inventory optimization.",
                "fd": "1", "fm": "1", "fy": "2024", "td": "1", "tm": "5", "ty": "2024"
            }
        ],
        "education": [
            {
                "title": "Bachelor in Applied Mathematics & Economics", "org": "Université Grenoble Alpes", "city": "Grenoble", "country": "France",
                "fd": "1", "fm": "9", "fy": "2021", "td": "1", "tm": "6", "ty": "2024"
            },
            {
                "title": "Baccalauréat (Maths & Physics)", "org": "Lycée Champollion", "city": "Grenoble", "country": "France",
                "fd": "1", "fm": "9", "fy": "2020", "td": "1", "tm": "6", "ty": "2021"
            }
        ],
        "skills": [
            {"title": "Data & Analytics", "desc": "Statistical Analysis, Data Visualization, Predictive Modeling."},
            {"title": "IT Skills", "desc": "Python (Pandas, NumPy), SQL, Excel (Advanced), Power BI."}
        ],
        "languages": [
            {"title": "English", "desc": "C1 Level"},
            {"title": "French", "desc": "Native"}
        ],
        "interests": [
            {"title": "Data Visualization", "desc": "Transforming complex data into clear insights."},
            {"title": "Sports", "desc": "Hiking and trail running."}
        ]
    },

    # --- CANDIDAT 7 : Amélie DUBOIS ---
    {
        "infos": {
            "prenom": "Amélie",
            "nom": "DUBOIS",
            "description": "Sustainability-oriented student specializing in corporate responsibility, ESG analysis, and strategic transformation.",
            "genre": "Female",
            "nationalite": "French",
            "email": "amelie.dubois@email.com",
            "phone_pays": "France",
            "phone_num": "614885329",
            "ville": "Paris",
            "pays": "France"
        },
        "jobs": [
            {
                "title": "Sustainability Consulting Intern", "employer": "EY Climate Change & Sustainability Services", "city": "Paris", "country": "France",
                "desc": "Contributed to ESG diagnostics and carbon footprint analyses for corporate clients. Assisted in the preparation of sustainability reports aligned with CSRD standards. Conducted benchmarking on sustainable business practices across industries.",
                "fd": "1", "fm": "6", "fy": "2024", "td": "1", "tm": "12", "ty": "2024"
            },
            {
                "title": "Project Coordinator (Part-time)", "employer": "Environmental NGO", "city": "Paris", "country": "France",
                "desc": "Coordinated sustainability awareness projects with universities. Managed project timelines, budgets, and stakeholder communication. Prepared impact assessment reports.",
                "fd": "1", "fm": "9", "fy": "2023", "td": "1", "tm": "5", "ty": "2024"
            }
        ],
        "education": [
            {
                "title": "Bachelor in Management & Sustainability", "org": "Paris School of Economics", "city": "Paris", "country": "France",
                "fd": "1", "fm": "9", "fy": "2022", "td": "1", "tm": "6", "ty": "2025"
            },
            {
                "title": "Baccalauréat (Economics)", "org": "Lycée Louis-le-Grand", "city": "Paris", "country": "France",
                "fd": "1", "fm": "9", "fy": "2021", "td": "1", "tm": "6", "ty": "2022"
            }
        ],
        "skills": [
            {"title": "Sustainability", "desc": "ESG Analysis, Sustainable Finance, Strategic Benchmarking."},
            {"title": "IT Skills", "desc": "Excel (Advanced), Power BI, ESG reporting tools."}
        ],
        "languages": [
            {"title": "English", "desc": "C1 Level"},
            {"title": "Italian", "desc": "B2 Level"}
        ],
        "interests": [
            {"title": "Environmental Engagement", "desc": "Climate-related student initiatives."},
            {"title": "Wellness", "desc": "Yoga and mindfulness."}
        ]
    },

    # --- CANDIDAT 8 : Maxime PETIT ---
    {
        "infos": {
            "prenom": "Maxime",
            "nom": "PETIT",
            "description": "Operations-focused student with a background in industrial engineering, supply chain optimization, and lean management.",
            "genre": "Male",
            "nationalite": "French",
            "email": "maxime.petit@email.com",
            "phone_pays": "France",
            "phone_num": "673610488",
            "ville": "Lille",
            "pays": "France"
        },
        "jobs": [
            {
                "title": "Operations Intern", "employer": "Decathlon Logistics", "city": "Lille", "country": "France",
                "desc": "Analyzed warehouse processes and identified efficiency improvement areas. Supported the implementation of lean management tools. Built performance dashboards to monitor key operational indicators.",
                "fd": "1", "fm": "6", "fy": "2024", "td": "1", "tm": "9", "ty": "2024"
            },
            {
                "title": "Supply Chain Project", "employer": "Academic", "city": "Lille", "country": "France",
                "desc": "Modeled supply chain flows and demand forecasts for a retail company. Proposed inventory optimization strategies to reduce stockouts.",
                "fd": "1", "fm": "2", "fy": "2024", "td": "1", "tm": "5", "ty": "2024"
            }
        ],
        "education": [
            {
                "title": "Bachelor in Industrial Engineering & Management", "org": "IMT Nord Europe", "city": "Lille", "country": "France",
                "fd": "1", "fm": "9", "fy": "2021", "td": "1", "tm": "6", "ty": "2024"
            },
            {
                "title": "Baccalauréat (Maths & Engineering)", "org": "Lycée Faidherbe", "city": "Lille", "country": "France",
                "fd": "1", "fm": "9", "fy": "2020", "td": "1", "tm": "6", "ty": "2021"
            }
        ],
        "skills": [
            {"title": "Operations", "desc": "Process Optimization, Lean Management, Supply Chain Analysis."},
            {"title": "IT Skills", "desc": "Excel (Advanced), Python (Basics), Power BI."}
        ],
        "languages": [
            {"title": "English", "desc": "C1 Level"},
            {"title": "French", "desc": "Native"}
        ],
        "interests": [
            {"title": "Innovation", "desc": "Industry 4.0 and automation."},
            {"title": "Sports", "desc": "Competitive basketball."}
        ]
    },

    # --- CANDIDAT 9 : Thomas LEGRAND ---
    {
        "infos": {
            "prenom": "Thomas",
            "nom": "LEGRAND",
            "description": "Creative and proactive student passionate about digital growth levers, with experience in startups and freelancing.",
            "genre": "Male",
            "nationalite": "French",
            "email": "thomas.legrand@email.com",
            "phone_pays": "France",
            "phone_num": "698765432",
            "ville": "Lyon",
            "pays": "France"
        },
        "jobs": [
            {
                "title": "CEO's Right Hand / Executive Intern", "employer": "'PayFast' FinTech", "city": "Paris", "country": "France",
                "desc": "Contributed to the Go-to-market strategy for the launch of a new B2B offer. Growth Hacking: Automating LinkedIn prospecting (+30 qualified leads/week). Video content creation and social media management.",
                "fd": "1", "fm": "1", "fy": "2025", "td": "1", "tm": "6", "ty": "2025"
            },
            {
                "title": "Freelancer / Self-Employed", "employer": "Self-Employed", "city": "Lyon", "country": "France",
                "desc": "Designed websites for 5 local SMEs (WordPress & Shopify). Managed Facebook Ads campaigns (Budget €2k, ROI x3). Full client relationship management: Briefing, quoting, and invoicing.",
                "fd": "1", "fm": "1", "fy": "2024", "td": "1", "tm": "1", "ty": "2026"
            }
        ],
        "education": [
            {
                "title": "Bachelor in Digital Project Management", "org": "IUT Lyon 1 / École du Web", "city": "Lyon", "country": "France",
                "fd": "1", "fm": "9", "fy": "2023", "td": "1", "tm": "6", "ty": "2026"
            }
        ],
        "skills": [
            {"title": "Web Development", "desc": "HTML/CSS, WordPress, Shopify, Notion."},
            {"title": "Data & Marketing", "desc": "Python (Data Analysis), Google Analytics (GA4), HubSpot."},
            {"title": "Design", "desc": "Adobe Creative Suite (Photoshop, Premiere Pro)."}
        ],
        "languages": [
            {"title": "English", "desc": "B2+ Fluent Professional"},
            {"title": "Chinese", "desc": "A2 Beginner"}
        ],
        "interests": [
            {"title": "Travel", "desc": "Backpacking road-trip in Southeast Asia."},
            {"title": "Sports", "desc": "Running (Paris Half-Marathon)."},
            {"title": "Tech", "desc": "Tech Blogger (AI and NoCode)."}
        ]
    },

    # --- CANDIDAT 10 : Camille MARTIN ---
    {
        "infos": {
            "prenom": "Camille",
            "nom": "MARTIN",
            "description": "Trilingual Political Science student driven by geopolitical issues, with international and humanitarian experience.",
            "genre": "Female",
            "nationalite": "French",
            "email": "camille.martin@email.com",
            "phone_pays": "France",
            "phone_num": "655443322",
            "ville": "Bordeaux",
            "pays": "France"
        },
        "jobs": [
            {
                "title": "International Humanitarian Mission", "employer": "NGO 'Education For All'", "city": "Dakar", "country": "Senegal",
                "desc": "Coordinated a multicultural team of 5 international volunteers. Taught French and provided tutoring (primary and middle school levels). Managed camp logistics and relations with local stakeholders.",
                "fd": "1", "fm": "6", "fy": "2025", "td": "1", "tm": "8", "ty": "2025"
            },
            {
                "title": "Public Affairs Intern", "employer": "City Hall of Bordeaux", "city": "Bordeaux", "country": "France",
                "desc": "Drafted synthesis notes for elected officials and press releases. Co-organized cultural and civic events (Budget: €50k). Conducted legislative monitoring on environmental topics.",
                "fd": "1", "fm": "1", "fy": "2024", "td": "1", "tm": "12", "ty": "2025"
            }
        ],
        "education": [
            {
                "title": "Bachelor in Political Science", "org": "University of Bordeaux", "city": "Bordeaux", "country": "France",
                "fd": "1", "fm": "9", "fy": "2023", "td": "1", "tm": "6", "ty": "2026"
            }
        ],
        "skills": [
            {"title": "Soft Skills", "desc": "Public Speaking, Intercultural Communication, Conflict Resolution, Synthesis."},
            {"title": "Analysis", "desc": "Legislative monitoring, Event organization."}
        ],
        "languages": [
            {"title": "English", "desc": "C1 - IELTS 7.5"},
            {"title": "German", "desc": "B2/C1 Advanced"},
            {"title": "Arabic", "desc": "A1 Basic"}
        ],
        "interests": [
            {"title": "Geopolitics", "desc": "Member of MUN (Model United Nations)."},
            {"title": "Scouting", "desc": "Team Leader (3 years)."},
            {"title": "Culture", "desc": "Russian literature and South American cinema."}
        ]
    }
]

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
