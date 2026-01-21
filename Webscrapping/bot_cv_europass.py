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

# ==============================================================================
# --- ZONE DE DONNÉES (LISTE DES CANDIDATS) ---
# ==============================================================================

LISTE_CANDIDATS = [
    # --- CANDIDAT 1 : Thomas Anderson ---
    {
        "infos": {
            "prenom": "Thomas",
            "nom": "Anderson",
            "description": "Développeur Python passionné par l'automatisation.",
            "genre": "Male",
            "nationalite": "French",
            "email": "thomas.anderson@matrix.com",
            "phone_pays": "France",
            "phone_num": "612345678",
            "adresse_type": "1: home",
            "ville": "Paris",
            "pays": "France",
            "date_format": "1: d MMM yyyy"
        },
        "jobs": [
            {
                "title": "Senior Software Engineer", "employer": "Matrix Corp", "city": "London", "country": "United Kingdom",
                "desc": "Lead development of automated agents.",
                "fd": "1", "fm": "1", "fy": "2023", "td": "1", "tm": "1", "ty": "2025"
            },
            {
                "title": "Junior Developer", "employer": "Nebuchadnezzar Inc", "city": "Paris", "country": "France",
                "desc": "Maintenance of legacy systems.",
                "fd": "1", "fm": "6", "fy": "2020", "td": "1", "tm": "12", "ty": "2022"
            }
        ],
        "education": [
            {
                "title": "Master in Computer Science", "org": "University of Technology", "city": "Compiegne", "country": "France",
                "fd": "1", "fm": "9", "fy": "2015", "td": "1", "tm": "6", "ty": "2020"
            },
            {
                "title": "Bachelor of Science", "org": "University of Paris", "city": "Paris", "country": "France",
                "fd": "1", "fm": "9", "fy": "2012", "td": "1", "tm": "6", "ty": "2015"
            }
        ],
        "skills": [
            {"title": "Python Development", "desc": "Automation scripts, Web Scraping (Selenium), Data Analysis."},
            {"title": "DevOps Tools", "desc": "Docker, CI/CD pipelines, Git version control."}
        ],
        "languages": [
            {"title": "French", "desc": "Mother Tongue"},
            {"title": "English", "desc": "Strong User - C1 Level"},
            {"title": "German", "desc": "Basic User - A2 Level"}
        ],
        "interests": [
            {"title": "Open Source", "desc": "Active contributor to Python libraries on GitHub."},
            {"title": "Hiking", "desc": "Trekking in the Alps and Pyrenees."},
            {"title": "Photography", "desc": "Street photography and digital editing."}
        ]
    },

    # --- CANDIDAT 2 : Sarah Connor ---
    {
        "infos": {
            "prenom": "Sarah",
            "nom": "Connor",
            "description": "Spécialiste en sécurité et survie.",
            "genre": "Female",
            "nationalite": "United States",
            "email": "sarah.connor@skynet.com",
            "phone_pays": "United States",
            "phone_num": "987654321",
            "adresse_type": "1: home",
            "ville": "Los Angeles",
            "pays": "United States",
            "date_format": "1: d MMM yyyy"
        },
        "jobs": [
            {
                "title": "Resistance Leader", "employer": "Humanity", "city": "Los Angeles", "country": "United States",
                "desc": "Fighting against the machines.",
                "fd": "1", "fm": "8", "fy": "1997", "td": "1", "tm": "1", "ty": "2020"
            }
        ],
        "education": [],
        "skills": [
            {"title": "Combat Tactics", "desc": "Guerrilla warfare, heavy weapons."},
            {"title": "Strategy", "desc": "Leadership and tactical planning."}
        ],
        "languages": [
            {"title": "English", "desc": "Mother Tongue"},
            {"title": "Spanish", "desc": "Conversational (B1)"}
        ],
        "interests": []
    }
]

# ==============================================================================
# --- FIN ZONE DE DONNÉES ---
# ==============================================================================


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

    # Pays
    cnt = driver.find_element(By.XPATH, "//label[contains(., 'Country')]/following::span[@role='combobox'][1]")
    cnt.click()
    time.sleep(1)
    actions.send_keys(j['country']).perform()
    time.sleep(1.5)
    actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()

    # Dates
    Select(driver.find_element(By.XPATH, "//label[contains(., 'From')]/following::select[1]")).select_by_visible_text(j['fd'])
    Select(driver.find_element(By.XPATH, "//label[contains(., 'From')]/following::select[2]")).select_by_visible_text(j['fm'])
    Select(driver.find_element(By.XPATH, "//label[contains(., 'From')]/following::select[3]")).select_by_visible_text(j['fy'])
    Select(driver.find_element(By.XPATH, "//label[contains(., 'To')]/following::select[1]")).select_by_visible_text(j['td'])
    Select(driver.find_element(By.XPATH, "//label[contains(., 'To')]/following::select[2]")).select_by_visible_text(j['tm'])
    Select(driver.find_element(By.XPATH, "//label[contains(., 'To')]/following::select[3]")).select_by_visible_text(j['ty'])

    # Description
    eds = driver.find_elements(By.CSS_SELECTOR, ".ql-editor")
    if eds: driver.execute_script("arguments[0].innerText = arguments[1];", eds[-1], j['desc'])

    # Save
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
# --- MAIN EXECUTION LOOP ---
# ==============================================================================

for index, candidat in enumerate(LISTE_CANDIDATS):
    print(f"\n==================================================")
    print(f"🚀 TRAITEMENT DU CANDIDAT {index + 1}/{len(LISTE_CANDIDATS)} : {candidat['infos']['prenom']} {candidat['infos']['nom']}")
    print(f"==================================================")

    # On recrée un driver tout neuf pour chaque candidat
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    wait = WebDriverWait(driver, 30)
    actions = ActionChains(driver)

    try:
        # 1. NAVIGATION
        url = "https://europa.eu/europass/eportfolio/screen/cv-editor/legacy-cv-editor?lang=en"
        driver.get(url)
        time.sleep(3) # Attente chargement page

        # Gestion des popups (Cookies + Start from Scratch)
        # On insiste un peu car c'est souvent là que ça plante au 2ème tour
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

        # Fermer la modale tuto si elle apparaît (clic sur body + TAB)
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

        try: Select(wait.until(EC.presence_of_element_located((By.ID, "cv-date-format-picker")))).select_by_value(infos['date_format'])
        except: pass
        try:
            driver.find_element(By.CSS_SELECTOR, "input[placeholder='e.g. John']").send_keys(infos['prenom'])
            driver.find_element(By.CSS_SELECTOR, "input[placeholder='e.g. Doe']").send_keys(infos['nom'])
            driver.execute_script("arguments[0].innerText = arguments[1];", driver.find_element(By.CSS_SELECTOR, ".ql-editor"), infos['description'])
            Select(driver.find_element(By.ID, "perso-info-sex")).select_by_visible_text(infos['genre'])
        except: pass

        # Nationalité
        try:
            span_nat = wait.until(EC.element_to_be_clickable((By.ID, "perso-info-nationality-input-0")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", span_nat)
            span_nat.click()
            actions.send_keys(infos['nationalite']).perform()
            time.sleep(1.5)
            actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
        except: pass

        # Contact
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
            Select(driver.find_element(By.ID, "perso-info-address-type-0")).select_by_value(infos['adresse_type'])
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

        # 5. SKILLS
        if candidat['skills']:
            print(f"\n➕ Création de la section 'Skills'...")
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
            title_sec.send_keys("Skills")
            time.sleep(1)
            driver.find_element(By.ID, "add-section").click()
            time.sleep(3)

            for i, skill in enumerate(candidat['skills']):
                if i > 0:
                    add_news = driver.find_elements(By.XPATH, "//span[normalize-space()='Add new']")
                    if add_news:
                        add_news[-1].click()
                        time.sleep(2)
                fill_other(driver, wait, skill['title'], skill['desc'])

        # 6. LANGUAGES
        if candidat['languages']:
            print(f"\n➕ Création de la section 'Languages'...")
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
            title_sec.send_keys("Languages")
            time.sleep(1)
            driver.find_element(By.ID, "add-section").click()
            time.sleep(3)

            for i, lang in enumerate(candidat['languages']):
                if i > 0:
                    add_news = driver.find_elements(By.XPATH, "//span[normalize-space()='Add new']")
                    if add_news:
                        add_news[-1].click()
                        time.sleep(2)
                fill_other(driver, wait, lang['title'], lang['desc'])

        # 7. INTERESTS
        if candidat['interests']:
            print(f"\n➕ Création de la section 'Interests'...")
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
            title_sec.send_keys("Interests")
            time.sleep(1)
            driver.find_element(By.ID, "add-section").click()
            time.sleep(3)

            for i, interest in enumerate(candidat['interests']):
                if i > 0:
                    add_news = driver.find_elements(By.XPATH, "//span[normalize-space()='Add new']")
                    if add_news:
                        add_news[-1].click()
                        time.sleep(2)
                fill_other(driver, wait, interest['title'], interest['desc'])

        # 8. NEXT
        print("\n➡️ Clic sur 'Next'...")
        next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next')] | //a[contains(., 'Next')]")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
        time.sleep(1)
        next_btn.click()

        print(f"✅ Candidat {candidat['infos']['prenom']} traité !")

    except Exception as e:
        print(f"❌ ERREUR sur {candidat['infos']['prenom']}.")
        print("Détail de l'erreur :")
        traceback.print_exc()

    finally:
        time.sleep(3)
        print(f"Fermeture du navigateur pour {candidat['infos']['prenom']} et passage au suivant...")
        driver.quit()
        time.sleep(2) # Petite pause technique avant le prochain tour

print("🎉 TOUS LES CANDIDATS ONT ÉTÉ TRAITÉS !")
