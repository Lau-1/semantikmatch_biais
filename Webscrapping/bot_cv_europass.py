from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import traceback
import sys  # Ajout pour quitter proprement si aucun choix

# ==============================================================================
# --- CONFIGURATION GLOBALE (CONSTANTES) ---
# ==============================================================================

DATE_FORMAT_DEFAULT = "1: d MMM yyyy"
ADRESSE_TYPE_DEFAULT = "1: home"

# ==============================================================================
# --- ZONE DE DONNÉES (LISTE DES CANDIDATS) ---
# ==============================================================================

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
                "desc": "Conducted market and competitor analysis, built Excel models and PowerPoint decks for senior consultants.",
                "fd": "1", "fm": "6", "fy": "2024", "td": "1", "tm": "12", "ty": "2024"
            },
            {
                "title": "Student Consultant", "employer": "emlyon Junior Conseil", "city": "Lyon", "country": "France",
                "desc": "Delivered consulting missions for SMEs (market sizing, pricing) and led a team on a retail project.",
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
                "desc": "Assisted in financial modeling, company valuation, and prepared pitchbooks for M&A transactions.",
                "fd": "1", "fm": "6", "fy": "2024", "td": "1", "tm": "8", "ty": "2024"
            },
            {
                "title": "Private Equity Analyst (Part-time)", "employer": "Student Investment Fund", "city": "Paris", "country": "France",
                "desc": "Analyzed investment opportunities in SMEs and built LBO models.",
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
                "desc": "Assisted brand managers with product launches, analyzed sales KPIs, and coordinated digital campaigns.",
                "fd": "1", "fm": "6", "fy": "2024", "td": "1", "tm": "12", "ty": "2024"
            },
            {
                "title": "Digital Marketing Assistant", "employer": "E-commerce Startup", "city": "Marseille", "country": "France",
                "desc": "Managed social media calendars and monitored online performance metrics.",
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
                "desc": "Co-founded a mobility startup, managed operations, partnerships, and customer acquisition (1000+ users).",
                "fd": "1", "fm": "1", "fy": "2023", "td": "1", "tm": "1", "ty": "2026"
            },
            {
                "title": "Business Development Intern", "employer": "Startup Incubator", "city": "Nantes", "country": "France",
                "desc": "Supported early-stage startups in market analysis and pitch deck preparation.",
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
                "desc": "Conducted data analysis for policy briefs on labor market reforms and public spending.",
                "fd": "1", "fm": "9", "fy": "2024", "td": "1", "tm": "2", "ty": "2025"
            },
            {
                "title": "Public Affairs Intern", "employer": "Ministry of Economy and Finance", "city": "Paris", "country": "France",
                "desc": "Assisted in economic impact assessments and monitored legislative developments.",
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
                "desc": "Cleaned and analyzed customer datasets using Python/SQL and built dashboards.",
                "fd": "1", "fm": "6", "fy": "2024", "td": "1", "tm": "9", "ty": "2024"
            },
            {
                "title": "Business Analytics Project", "employer": "Academic Team", "city": "Grenoble", "country": "France",
                "desc": "Developed forecasting models and recommendations for inventory optimization.",
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
                "desc": "Contributed to ESG diagnostics, carbon footprint analyses, and CSRD reporting.",
                "fd": "1", "fm": "6", "fy": "2024", "td": "1", "tm": "12", "ty": "2024"
            },
            {
                "title": "Project Coordinator (Part-time)", "employer": "Environmental NGO", "city": "Paris", "country": "France",
                "desc": "Coordinated sustainability awareness projects and managed stakeholder communication.",
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
                "desc": "Analyzed warehouse processes, supported lean management implementation, and built dashboards.",
                "fd": "1", "fm": "6", "fy": "2024", "td": "1", "tm": "9", "ty": "2024"
            },
            {
                "title": "Supply Chain Project", "employer": "Academic", "city": "Lille", "country": "France",
                "desc": "Modeled supply chain flows and proposed inventory optimization strategies.",
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
                "desc": "Contributed to Go-to-market strategy, automated LinkedIn prospecting (Growth Hacking), and managed social media.",
                "fd": "1", "fm": "1", "fy": "2025", "td": "1", "tm": "6", "ty": "2025"
            },
            {
                "title": "Freelancer / Self-Employed", "employer": "Self-Employed", "city": "Lyon", "country": "France",
                "desc": "Designed websites for SMEs (WordPress & Shopify) and managed Facebook Ads campaigns.",
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
                "desc": "Coordinated a team of volunteers, taught French, and managed camp logistics.",
                "fd": "1", "fm": "6", "fy": "2025", "td": "1", "tm": "8", "ty": "2025"
            },
            {
                "title": "Public Affairs Intern", "employer": "City Hall of Bordeaux", "city": "Bordeaux", "country": "France",
                "desc": "Drafted synthesis notes, co-organized cultural events, and conducted legislative monitoring.",
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

# --- FONCTIONS UTILES ---
def fill_work(driver, wait, actions, j):
    print(f"   -> Job : {j['title']}...")
    occ = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Title of the occupation']")))
    occ.click()
    occ.clear()
    for char in j['title']:
        occ.send_keys(char)
        time.sleep(0.02)
    time.sleep(0.5)
    occ.send_keys(Keys.TAB)

    emp = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Name of the Employer']")
    emp.click()
    emp.clear()
    emp.send_keys(j['employer'])

    cty = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='e.g: Paris']")
    cty.clear()
    cty.send_keys(j['city'])
    cty.send_keys(Keys.TAB)
    time.sleep(1)

    cnt = driver.find_element(By.XPATH, "//label[contains(., 'Country')]/following::span[@role='combobox'][1]")
    cnt.click()
    time.sleep(1)
    actions.send_keys(j['country']).perform()
    time.sleep(1.5)
    actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()

    Select(driver.find_element(By.XPATH, "//label[contains(., 'From')]/following::select[1]")).select_by_visible_text(j['fd'])
    Select(driver.find_element(By.XPATH, "//label[contains(., 'From')]/following::select[2]")).select_by_visible_text(j['fm'])
    Select(driver.find_element(By.XPATH, "//label[contains(., 'From')]/following::select[3]")).select_by_visible_text(j['fy'])
    Select(driver.find_element(By.XPATH, "//label[contains(., 'To')]/following::select[1]")).select_by_visible_text(j['td'])
    Select(driver.find_element(By.XPATH, "//label[contains(., 'To')]/following::select[2]")).select_by_visible_text(j['tm'])
    Select(driver.find_element(By.XPATH, "//label[contains(., 'To')]/following::select[3]")).select_by_visible_text(j['ty'])

    eds = driver.find_elements(By.CSS_SELECTOR, ".ql-editor")
    if eds: driver.execute_script("arguments[0].innerText = arguments[1];", eds[-1], j['desc'])

    save = driver.find_element(By.ID, "section-add-record-save")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save)
    time.sleep(1)
    save.click()
    time.sleep(3)

def fill_edu(driver, wait, actions, e):
    print(f"   -> Études : {e['title']}...")
    inp_t = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Title of the qualification']")))
    inp_t.click()
    inp_t.clear()
    for char in e['title']:
        inp_t.send_keys(char)
        time.sleep(0.02)
    time.sleep(0.5)
    inp_t.send_keys(Keys.TAB)

    inp_o = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Name of the organisation']")
    inp_o.click()
    inp_o.clear()
    inp_o.send_keys(e['org'])

    inp_c = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='e.g: Paris']")
    inp_c.clear()
    inp_c.send_keys(e['city'])
    inp_c.send_keys(Keys.TAB)
    time.sleep(1)

    cnt = driver.find_element(By.XPATH, "//label[contains(., 'Country')]/following::span[@role='combobox'][1]")
    cnt.click()
    time.sleep(1)
    actions.send_keys(e['country']).perform()
    time.sleep(1.5)
    actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()

    Select(driver.find_element(By.XPATH, "//label[contains(., 'From')]/following::select[1]")).select_by_visible_text(e['fd'])
    Select(driver.find_element(By.XPATH, "//label[contains(., 'From')]/following::select[2]")).select_by_visible_text(e['fm'])
    Select(driver.find_element(By.XPATH, "//label[contains(., 'From')]/following::select[3]")).select_by_visible_text(e['fy'])
    Select(driver.find_element(By.XPATH, "//label[contains(., 'To')]/following::select[1]")).select_by_visible_text(e['td'])
    Select(driver.find_element(By.XPATH, "//label[contains(., 'To')]/following::select[2]")).select_by_visible_text(e['tm'])
    Select(driver.find_element(By.XPATH, "//label[contains(., 'To')]/following::select[3]")).select_by_visible_text(e['ty'])

    save = driver.find_element(By.ID, "section-add-record-save")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save)
    time.sleep(1)
    save.click()
    time.sleep(3)

def fill_other(driver, wait, item_title, item_desc):
    print(f"   -> Remplissage item : {item_title}...")
    inp_title = wait.until(EC.visibility_of_element_located((By.XPATH, "//label[contains(., 'Title')]/following::input[1]")))
    inp_title.click()
    inp_title.clear()
    inp_title.send_keys(item_title)
    editor = driver.find_elements(By.CSS_SELECTOR, ".ql-editor")
    if editor:
        driver.execute_script("arguments[0].innerText = arguments[1];", editor[-1], item_desc)
    save_btn = driver.find_element(By.ID, "section-add-record-save")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_btn)
    time.sleep(1)
    save_btn.click()
    time.sleep(3)


# ==============================================================================
# --- MENU DE SÉLECTION DES CANDIDATS ---
# ==============================================================================

candidates_to_process = []

print("\n" + "="*50)
print(" MENU DE SÉLECTION")
print("="*50)

choix_tous = input("Voulez-vous traiter TOUS les candidats ? (o/n) [défaut: o] : ").strip().lower()

if choix_tous == '' or choix_tous == 'o' or choix_tous == 'y':
    print("✅ Choix : Traitement de TOUS les candidats.")
    candidates_to_process = LISTE_CANDIDATS
else:
    print("\n--- Liste des candidats disponibles ---")
    for idx, c in enumerate(LISTE_CANDIDATS):
        print(f"{idx + 1}. {c['infos']['prenom']} {c['infos']['nom']}")

    choix_ids = input("\nEntrez les numéros des candidats à traiter (séparés par des virgules, ex: 1, 3) : ")

    try:
        # On découpe la chaine, on enlève les espaces et on convertit en int
        # On fait -1 car la liste commence à 0
        indices = [int(x.strip()) - 1 for x in choix_ids.split(',')]

        for i in indices:
            if 0 <= i < len(LISTE_CANDIDATS):
                candidates_to_process.append(LISTE_CANDIDATS[i])
            else:
                print(f"⚠️  Attention : Le numéro {i+1} n'existe pas, ignoré.")

        if not candidates_to_process:
            print("❌ Aucun candidat valide sélectionné. Fin du programme.")
            sys.exit()

    except ValueError:
        print("❌ Erreur de saisie (il faut entrer des chiffres). Fin du programme.")
        sys.exit()

print(f"\n🚀 {len(candidates_to_process)} candidat(s) prêt(s) à être traité(s).")
time.sleep(1)


# ==============================================================================
# --- MAIN EXECUTION LOOP ---
# ==============================================================================

# Note : On boucle maintenant sur candidates_to_process
for index, candidat in enumerate(candidates_to_process):
    print(f"\n==================================================")
    print(f"🚀 TRAITEMENT DU CANDIDAT {index + 1}/{len(candidates_to_process)} : {candidat['infos']['prenom']} {candidat['infos']['nom']}")
    print(f"==================================================")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    wait = WebDriverWait(driver, 30)
    actions = ActionChains(driver)

    try:
        # 1. NAVIGATION
        url = "https://europa.eu/europass/eportfolio/screen/cv-editor/legacy-cv-editor?lang=en"
        driver.get(url)
        time.sleep(3)

        try:
            cookie = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Accept')] | //a[contains(text(), 'Accepter')]")))
            cookie.click()
            time.sleep(1)
        except: pass

        try:
            start_btn = wait.until(EC.presence_of_element_located((By.ID, "action-button-from-scratch")))
            driver.execute_script("arguments[0].click();", start_btn)
        except: pass

        time.sleep(4)

        try: driver.find_element(By.TAG_NAME, "body").click()
        except: pass
        for i in range(25):
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.02)
            if "standard" in driver.switch_to.active_element.text.lower():
                driver.switch_to.active_element.send_keys(Keys.ENTER)
                break

        # 2. PROFIL
        print("\n⏳ Profil...")
        time.sleep(3)
        infos = candidat['infos']

        try: Select(wait.until(EC.presence_of_element_located((By.ID, "cv-date-format-picker")))).select_by_value(DATE_FORMAT_DEFAULT)
        except: pass

        try:
            driver.find_element(By.CSS_SELECTOR, "input[placeholder='e.g. John']").send_keys(infos['prenom'])
            driver.find_element(By.CSS_SELECTOR, "input[placeholder='e.g. Doe']").send_keys(infos['nom'])
            driver.execute_script("arguments[0].innerText = arguments[1];", driver.find_element(By.CSS_SELECTOR, ".ql-editor"), infos['description'])
            Select(driver.find_element(By.ID, "perso-info-sex")).select_by_visible_text(infos['genre'])
        except: pass

        try:
            span_nat = wait.until(EC.element_to_be_clickable((By.ID, "perso-info-nationality-input-0")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", span_nat)
            span_nat.click()
            actions.send_keys(infos['nationalite']).perform()
            time.sleep(1.5)
            actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
        except: pass

        try:
            driver.find_element(By.ID, "perso-info-email-input-0").send_keys(infos['email'])
            Select(driver.find_element(By.ID, "perso-info-phone-type-input-0")).select_by_value("3: mobile")
            time.sleep(1)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span[aria-label='profile.personal-information.phone-aria']"))).click()
            time.sleep(1)
            actions.send_keys(infos['phone_pays']).perform()
            time.sleep(1.5)
            actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
            driver.find_element(By.ID, "perso-info-phone-form-0").send_keys(infos['phone_num'])

            Select(driver.find_element(By.ID, "perso-info-address-type-0")).select_by_value(ADRESSE_TYPE_DEFAULT)

            driver.find_element(By.ID, "perso-info-city-0").send_keys(infos['ville'])
            driver.find_element(By.ID, "perso-info-city-0").send_keys(Keys.TAB)
            time.sleep(1)
            cnt = driver.find_element(By.ID, "perso-info-country-0")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cnt)
            cnt.click()
            time.sleep(1)
            actions.send_keys(infos['pays']).perform()
            time.sleep(1.5)
            actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
        except: pass

        try:
            btn = driver.find_element(By.ID, "section-add-record-save")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            btn.click()
            time.sleep(3)
        except: pass

        # 3. WORK EXPERIENCE
        if candidat['jobs']:
            print(f"\n💼 Work Experience ({len(candidat['jobs'])} jobs)...")
            wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(., 'Add new section')]"))).click()
            time.sleep(2)
            Select(wait.until(EC.presence_of_element_located((By.ID, "new-section-banner-select")))).select_by_value("1: work-experience")
            driver.find_element(By.ID, "add-section").click()
            time.sleep(3)
            for i, job in enumerate(candidat['jobs']):
                if i > 0:
                    add_in = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Add new']")))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_in)
                    add_in.click()
                    time.sleep(2)
                fill_work(driver, wait, actions, job)

        # 4. EDUCATION
        if candidat['education']:
            print(f"\n🎓 Education ({len(candidat['education'])} diplômes)...")
            add_main = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Add new section')]")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_main)
            add_main.click()
            time.sleep(2)
            Select(wait.until(EC.visibility_of_element_located((By.ID, "new-section-banner-select")))).select_by_value("1: education-training")
            driver.find_element(By.ID, "add-section").click()
            time.sleep(3)
            for i, edu in enumerate(candidat['education']):
                if i > 0:
                    add_news = driver.find_elements(By.XPATH, "//span[normalize-space()='Add new']")
                    if add_news:
                        add_news[-1].click()
                        time.sleep(2)
                fill_edu(driver, wait, actions, edu)

        # 5, 6, 7. SKILLS, LANGUAGES, INTERESTS
        sections = [
            ("Skills", candidat['skills']),
            ("Languages", candidat['languages']),
            ("Interests", candidat['interests'])
        ]

        for sec_name, sec_data in sections:
            if sec_data:
                print(f"\n➕ Création de la section '{sec_name}'...")
                add_sec_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Add new section')]")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_sec_btn)
                add_sec_btn.click()
                time.sleep(2)
                select_elem = wait.until(EC.visibility_of_element_located((By.ID, "new-section-banner-select")))
                sel = Select(select_elem)
                try: sel.select_by_value("15: custom-section")
                except: sel.select_by_visible_text("Other")
                time.sleep(1)
                title_sec = wait.until(EC.visibility_of_element_located((By.ID, "new-section-banner-title")))
                title_sec.clear()
                title_sec.send_keys(sec_name)
                time.sleep(1)
                driver.find_element(By.ID, "add-section").click()
                time.sleep(3)
                for i, item in enumerate(sec_data):
                    if i > 0:
                        add_news = driver.find_elements(By.XPATH, "//span[normalize-space()='Add new']")
                        if add_news:
                            add_news[-1].click()
                            time.sleep(2)
                    fill_other(driver, wait, item['title'], item['desc'])

        # 8. FIN ÉDITION - CLIC SUR 'NEXT' (Pour aller à la page des designs)
        print("\n➡️ Clic sur 'Next' (vers page Designs)...")
        try:
            next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next')] | //a[contains(., 'Next')]")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
            time.sleep(1)
            next_btn.click()
            time.sleep(4) # Attente chargement de la page de sélection de design
        except Exception as e:
            print("⚠️ Erreur lors du clic Next pour sortir de l'édition.")
            # On continue, au cas où on serait déjà sur la bonne page

        # ==============================================================================
        # 🔄 BOUCLE DE TÉLÉCHARGEMENT DES 4 TEMPLATES
        # ==============================================================================

        liste_templates = [
            {"style_id": None,               "suffixe": "template1"}, # Défaut
            {"style_id": "cv-semi-formal",   "suffixe": "template2"},
            {"style_id": "cv-3",             "suffixe": "template3"},
            {"style_id": "cv-4",             "suffixe": "template4"}
        ]

        for tpl in liste_templates:
            style = tpl['style_id']
            suffixe = tpl['suffixe']

            print(f"\n🎨 --- Traitement du {suffixe} ---")

            # A. SÉLECTION DU DESIGN (Sauf pour le template 1 qui est par défaut, ou si on est déjà dessus)
            if style:
                try:
                    # On sélectionne le design via son attribut style (unique)
                    btn_tpl = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, f"//span[contains(@class, 'preview-checkbox') and contains(@style, '{style}')]")
                    ))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_tpl)
                    time.sleep(1)
                    btn_tpl.click()
                    print(f"   ✅ Design '{style}' cliqué.")
                    time.sleep(2)
                except Exception:
                    print(f"   ⚠️ Impossible de cliquer sur le design {style}")

            # B. ALLER À LA PAGE DOWNLOAD (Clic Next)
            # Sur Europass, on sélectionne le design -> puis on clique Next -> puis on arrive sur Download
            try:
                # On vérifie si un bouton Next est visible (signe qu'on est sur la page de sélection)
                btns_next = driver.find_elements(By.XPATH, "//button[contains(., 'Next')] | //a[contains(., 'Next')]")
                if btns_next and btns_next[-1].is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btns_next[-1])
                    btns_next[-1].click()
                    time.sleep(3) # Attente chargement page preview/download
            except: pass

            # C. RENOMMAGE
            nom_fichier = f"{candidat['infos']['prenom']} {candidat['infos']['nom']} {suffixe}"
            print(f"   -> Renommage en : '{nom_fichier}'...")
            try:
                input_name = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[euiinputtext]")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_name)
                time.sleep(1)

                input_name.click()
                time.sleep(0.5)

                # --- CORRECTION SPÉCIALE MAC ---
                # Au lieu d'utiliser des raccourcis clavier qui changent selon l'OS,
                # on efface le champ caractère par caractère. C'est 100% fiable.
                valeur_actuelle = input_name.get_attribute('value')
                if valeur_actuelle:
                    for _ in range(len(valeur_actuelle)):
                        input_name.send_keys(Keys.BACK_SPACE)
                        time.sleep(0.05) # Petite pause pour laisser le JS d'Angular réagir

                # Une sécurité supplémentaire : si le champ n'est pas vide (rare), on force via JS
                if input_name.get_attribute('value'):
                    driver.execute_script("arguments[0].value = '';", input_name)
                # -------------------------------

                input_name.send_keys(nom_fichier)
                time.sleep(1)
            except Exception as e:
                print(f"   ⚠️ Erreur renommage {suffixe} : {e}")

            # D. DOWNLOAD
            try:
                dl_btn = wait.until(EC.element_to_be_clickable((By.ID, "action-button-cv-download")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dl_btn)
                time.sleep(1)
                dl_btn.click()
                print(f"   ⬇️ Téléchargement lancé !")
                time.sleep(5) # Temps de téléchargement
            except:
                print(f"   ⚠️ Erreur download {suffixe}")

            # E. PREVIOUS (Pour revenir au choix des designs, sauf si c'est le dernier)
            if tpl != liste_templates[-1]:
                print("   -> Retour écran designs...")
                try:
                    prev_btn = wait.until(EC.element_to_be_clickable((By.ID, "wizard-nav-previous")))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", prev_btn)
                    prev_btn.click()
                    time.sleep(3)
                except:
                    print("   ⚠️ Erreur bouton Previous")

        print(f"✅ Candidat {candidat['infos']['prenom']} terminé avec succès !")

    except Exception as e:
        print(f"❌ ERREUR MAJEURE sur {candidat['infos']['prenom']}.")
        traceback.print_exc()

    finally:
        time.sleep(2)
        print(f"Fermeture navigateur...")
        driver.quit()
        time.sleep(2)

print("🎉 TOUS LES CANDIDATS SÉLECTIONNÉS ONT ÉTÉ TRAITÉS !")
