from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# --- DONNÉES ---
DATA_PRENOM = "Thomas"
DATA_NOM = "Anderson"
DATA_DATE_FORMAT = "1: d MMM yyyy"
DATA_DESCRIPTION = "Développeur Python passionné par l'automatisation."
DATA_GENRE_TEXT = "Male"
DATA_NATIONALITE = "French"
DATA_PHONE_PAYS = "France"
DATA_PHONE_NUM = "612345678"
DATA_EMAIL = "thomas.anderson@matrix.com"
DATA_VILLE = "Paris"
DATA_PAYS_ADRESSE = "France"

# --- JOBS ---
WORK1_TITLE = "Senior Software Engineer"
WORK1_EMPLOYER = "Matrix Corp"
WORK1_CITY = "London"
WORK1_COUNTRY = "United Kingdom"
WORK1_DESC = "Lead development of automated agents."
WORK1_FROM_DAY, WORK1_FROM_MONTH, WORK1_FROM_YEAR = "1", "1", "2023"
WORK1_TO_DAY, WORK1_TO_MONTH, WORK1_TO_YEAR = "1", "1", "2025"

WORK2_TITLE = "Junior Developer"
WORK2_EMPLOYER = "Nebuchadnezzar Inc"
WORK2_CITY = "Paris"
WORK2_COUNTRY = "France"
WORK2_DESC = "Maintenance of legacy systems."
WORK2_FROM_DAY, WORK2_FROM_MONTH, WORK2_FROM_YEAR = "1", "6", "2020"
WORK2_TO_DAY, WORK2_TO_MONTH, WORK2_TO_YEAR = "1", "12", "2022"

# --- FORMATION 1 (Master) ---
EDU1_TITLE = "Master in Computer Science"
EDU1_ORG = "University of Technology"
EDU1_CITY = "Compiegne"
EDU1_COUNTRY = "France"
EDU1_FROM_DAY, EDU1_FROM_MONTH, EDU1_FROM_YEAR = "1", "9", "2015"
EDU1_TO_DAY, EDU1_TO_MONTH, EDU1_TO_YEAR = "1", "6", "2020"

# --- FORMATION 2 (Bachelor) ---
EDU2_TITLE = "Bachelor of Science"
EDU2_ORG = "University of Paris"
EDU2_CITY = "Paris"
EDU2_COUNTRY = "France"
EDU2_FROM_DAY, EDU2_FROM_MONTH, EDU2_FROM_YEAR = "1", "9", "2012"
EDU2_TO_DAY, EDU2_TO_MONTH, EDU2_TO_YEAR = "1", "6", "2015"

# --- SETUP ---
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.maximize_window()
wait = WebDriverWait(driver, 30)
actions = ActionChains(driver)

# --- FONCTIONS ---
def fill_work(title, employer, city, country, desc, fd, fm, fy, td, tm, ty):
    print(f"   -> Job : {title}...")
    occ = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Title of the occupation']")))
    occ.click()
    occ.clear()
    for char in title:
        occ.send_keys(char)
        time.sleep(0.05)
    time.sleep(0.5)
    occ.send_keys(Keys.TAB)

    emp = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Name of the Employer']")
    emp.click()
    emp.clear()
    emp.send_keys(employer)

    cty = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='e.g: Paris']")
    cty.clear()
    cty.send_keys(city)
    cty.send_keys(Keys.TAB)
    time.sleep(1)

    cnt = driver.find_element(By.XPATH, "//label[contains(., 'Country')]/following::span[@role='combobox'][1]")
    cnt.click()
    time.sleep(1)
    actions.send_keys(country).perform()
    time.sleep(2)
    actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()

    Select(driver.find_element(By.XPATH, "//label[contains(., 'From')]/following::select[1]")).select_by_visible_text(fd)
    Select(driver.find_element(By.XPATH, "//label[contains(., 'From')]/following::select[2]")).select_by_visible_text(fm)
    Select(driver.find_element(By.XPATH, "//label[contains(., 'From')]/following::select[3]")).select_by_visible_text(fy)
    Select(driver.find_element(By.XPATH, "//label[contains(., 'To')]/following::select[1]")).select_by_visible_text(td)
    Select(driver.find_element(By.XPATH, "//label[contains(., 'To')]/following::select[2]")).select_by_visible_text(tm)
    Select(driver.find_element(By.XPATH, "//label[contains(., 'To')]/following::select[3]")).select_by_visible_text(ty)

    eds = driver.find_elements(By.CSS_SELECTOR, ".ql-editor")
    if eds: driver.execute_script("arguments[0].innerText = arguments[1];", eds[-1], desc)

    save = driver.find_element(By.ID, "section-add-record-save")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save)
    time.sleep(1)
    save.click()
    time.sleep(3)

def fill_edu(title, org, city, country, fd, fm, fy, td, tm, ty):
    print(f"   -> Études : {title}...")
    inp_t = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Title of the qualification']")))
    inp_t.click()
    inp_t.clear()
    for char in title:
        inp_t.send_keys(char)
        time.sleep(0.05)
    time.sleep(0.5)
    inp_t.send_keys(Keys.TAB)

    inp_o = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Name of the organisation']")
    inp_o.click()
    inp_o.clear()
    inp_o.send_keys(org)

    inp_c = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='e.g: Paris']")
    inp_c.clear()
    inp_c.send_keys(city)
    inp_c.send_keys(Keys.TAB)
    time.sleep(1)

    cnt = driver.find_element(By.XPATH, "//label[contains(., 'Country')]/following::span[@role='combobox'][1]")
    cnt.click()
    time.sleep(1)
    actions.send_keys(country).perform()
    time.sleep(2)
    actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()

    Select(driver.find_element(By.XPATH, "//label[contains(., 'From')]/following::select[1]")).select_by_visible_text(fd)
    Select(driver.find_element(By.XPATH, "//label[contains(., 'From')]/following::select[2]")).select_by_visible_text(fm)
    Select(driver.find_element(By.XPATH, "//label[contains(., 'From')]/following::select[3]")).select_by_visible_text(fy)
    Select(driver.find_element(By.XPATH, "//label[contains(., 'To')]/following::select[1]")).select_by_visible_text(td)
    Select(driver.find_element(By.XPATH, "//label[contains(., 'To')]/following::select[2]")).select_by_visible_text(tm)
    Select(driver.find_element(By.XPATH, "//label[contains(., 'To')]/following::select[3]")).select_by_visible_text(ty)

    save = driver.find_element(By.ID, "section-add-record-save")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save)
    time.sleep(1)
    save.click()
    time.sleep(3)

def fill_other(other_title, other_desc):
    print(f"   -> Remplissage other : {other_title}...")
    # 1. Champ TITRE (On cible le premier input après le label 'Title')
    inp_title = wait.until(EC.visibility_of_element_located((By.XPATH, "//label[contains(., 'Title')]/following::input[1]")))
    inp_title.click()
    inp_title.clear()
    inp_title.send_keys(other_title)

    # 2. Champ DESCRIPTION (Editeur de texte riche)
    editor = driver.find_elements(By.CSS_SELECTOR, ".ql-editor")
    if editor:
        driver.execute_script("arguments[0].innerText = arguments[1];", editor[-1], other_desc)

    # 3. SAUVEGARDER
    save_btn = driver.find_element(By.ID, "section-add-record-save")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_btn)
    time.sleep(1)
    save_btn.click()
    time.sleep(3) # Attente de la sauvegarde

# --- MAIN ---
try:
    # 1. NAVIGATION
    url = "https://europa.eu/europass/eportfolio/screen/cv-editor/legacy-cv-editor?lang=en"
    print(f"🌍 Connexion à {url}...")
    driver.get(url)
    try: wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Accept')] | //a[contains(text(), 'Accepter')]"))).click()
    except: pass
    try: driver.execute_script("arguments[0].click();", wait.until(EC.presence_of_element_located((By.ID, "action-button-from-scratch"))))
    except: pass
    time.sleep(4)
    try: driver.find_element(By.TAG_NAME, "body").click()
    except: pass
    for i in range(25):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.05)
        if "standard" in driver.switch_to.active_element.text.lower():
            driver.switch_to.active_element.send_keys(Keys.ENTER)
            break

    # 2. PROFIL
    print("\n⏳ Profil...")
    time.sleep(5)
    try: Select(wait.until(EC.presence_of_element_located((By.ID, "cv-date-format-picker")))).select_by_value(DATA_DATE_FORMAT)
    except: pass
    try:
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='e.g. John']").send_keys(DATA_PRENOM)
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='e.g. Doe']").send_keys(DATA_NOM)
        driver.execute_script("arguments[0].innerText = arguments[1];", driver.find_element(By.CSS_SELECTOR, ".ql-editor"), DATA_DESCRIPTION)
        Select(driver.find_element(By.ID, "perso-info-sex")).select_by_visible_text(DATA_GENRE_TEXT)
    except: pass

    # Nationalité
    try:
        span_nat = wait.until(EC.element_to_be_clickable((By.ID, "perso-info-nationality-input-0")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", span_nat)
        span_nat.click()
        actions.send_keys(DATA_NATIONALITE).perform()
        time.sleep(2)
        actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
    except: pass

    # Contact
    try:
        driver.find_element(By.ID, "perso-info-email-input-0").send_keys(DATA_EMAIL)
        Select(driver.find_element(By.ID, "perso-info-phone-type-input-0")).select_by_value("3: mobile")
        time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span[aria-label='profile.personal-information.phone-aria']"))).click()
        time.sleep(1)
        actions.send_keys(DATA_PHONE_PAYS).perform()
        time.sleep(2)
        actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
        driver.find_element(By.ID, "perso-info-phone-form-0").send_keys(DATA_PHONE_NUM)
        Select(driver.find_element(By.ID, "perso-info-address-type-0")).select_by_value("1: home")
        driver.find_element(By.ID, "perso-info-city-0").send_keys(DATA_VILLE)
        driver.find_element(By.ID, "perso-info-city-0").send_keys(Keys.TAB)
        time.sleep(1)
        cnt = driver.find_element(By.ID, "perso-info-country-0")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cnt)
        cnt.click()
        time.sleep(1)
        actions.send_keys(DATA_PAYS_ADRESSE).perform()
        time.sleep(2)
        actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
    except: pass

    try:
        btn = driver.find_element(By.ID, "section-add-record-save")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        btn.click()
        time.sleep(5)
    except: pass

    # 3. WORK 1
    print("\n💼 Work 1...")
    wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(., 'Add new section')]"))).click()
    time.sleep(2)
    Select(wait.until(EC.presence_of_element_located((By.ID, "new-section-banner-select")))).select_by_value("1: work-experience")
    driver.find_element(By.ID, "add-section").click()
    time.sleep(3)
    fill_work(WORK1_TITLE, WORK1_EMPLOYER, WORK1_CITY, WORK1_COUNTRY, WORK1_DESC, WORK1_FROM_DAY, WORK1_FROM_MONTH, WORK1_FROM_YEAR, WORK1_TO_DAY, WORK1_TO_MONTH, WORK1_TO_YEAR)

    # 4. WORK 2
    print("\n💼 Work 2...")
    # Ici, on utilise une XPath STRICTE pour ne pas confondre avec "Add new section"
    add_in = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Add new']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_in)
    add_in.click()
    time.sleep(3)
    fill_work(WORK2_TITLE, WORK2_EMPLOYER, WORK2_CITY, WORK2_COUNTRY, WORK2_DESC, WORK2_FROM_DAY, WORK2_FROM_MONTH, WORK2_FROM_YEAR, WORK2_TO_DAY, WORK2_TO_MONTH, WORK2_TO_YEAR)

    # 5. EDUCATION 1
    print("\n🎓 Education 1...")
    add_main = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Add new section')]")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_main)
    add_main.click()
    time.sleep(2)

    # ID dropdown "1" pour Education
    Select(wait.until(EC.visibility_of_element_located((By.ID, "new-section-banner-select")))).select_by_value("1: education-training")
    driver.find_element(By.ID, "add-section").click()
    time.sleep(3)
    fill_edu(EDU1_TITLE, EDU1_ORG, EDU1_CITY, EDU1_COUNTRY, EDU1_FROM_DAY, EDU1_FROM_MONTH, EDU1_FROM_YEAR, EDU1_TO_DAY, EDU1_TO_MONTH, EDU1_TO_YEAR)

    # 6. EDUCATION 2
    print("\n🎓 Education 2...")
    # On cherche TOUS les boutons "Add new" stricts (sans "Add new section")
    add_news = driver.find_elements(By.XPATH, "//span[normalize-space()='Add new']")
    if add_news:
        # On prend le dernier (celui de la section Education, qui est la dernière créée)
        last_btn = add_news[-1]
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", last_btn)
        last_btn.click()
        time.sleep(3)
        fill_edu(EDU2_TITLE, EDU2_ORG, EDU2_CITY, EDU2_COUNTRY, EDU2_FROM_DAY, EDU2_FROM_MONTH, EDU2_FROM_YEAR, EDU2_TO_DAY, EDU2_TO_MONTH, EDU2_TO_YEAR)
    else:
        print("❌ Impossible de trouver le bouton Add new pour Education 2")

    # ==========================================
    # 7. CRÉATION DE LA SECTION "SKILLS"
    # ==========================================
    print("\n➕ Création de la section 'Skills'...")

    # 1. Clic sur le gros bouton "Add new section" en bas
    add_sec_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Add new section')]")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_sec_btn)
    add_sec_btn.click()
    time.sleep(2)

    # 2. Sélection de "Other" (Index 15)
    select_elem = wait.until(EC.visibility_of_element_located((By.ID, "new-section-banner-select")))
    sel = Select(select_elem)
    try:
        sel.select_by_value("15: custom-section")
    except:
        sel.select_by_visible_text("Other")
    time.sleep(1)

    # 3. Nommer la section "Skills"
    print("   -> Renommage de la section en 'Skills'...")
    title_sec = wait.until(EC.visibility_of_element_located((By.ID, "new-section-banner-title")))
    title_sec.clear()
    title_sec.send_keys("Skills")
    time.sleep(1)

    # 4. Valider la création de la section
    driver.find_element(By.ID, "add-section").click()
    time.sleep(3)

    # ==========================================
    # 8. AJOUT DES COMPÉTENCES (SKILLS)
    # ==========================================

    # --- SKILL 1 (Formulaire déjà ouvert) ---
    fill_other("Python Development", "Automation scripts, Web Scraping (Selenium), Data Analysis.")

    # --- SKILL 2 ---
    print("   -> Clic sur 'Add new' pour le 2ème skill...")

    # On cherche tous les boutons "Add new"
    add_news = driver.find_elements(By.XPATH, "//span[normalize-space()='Add new']")
    if add_news:
        # On prend le DERNIER bouton de la page (celui de la section Skills)
        last_btn = add_news[-1]
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", last_btn)
        last_btn.click()
        time.sleep(2)

        # On remplit le 2ème skill
        fill_other("DevOps Tools", "Docker, CI/CD pipelines, Git version control.")
    else:
        print("❌ Erreur : Bouton 'Add new' introuvable.")


    # ==========================================
    # 9. CRÉATION DE LA SECTION "LANGUAGES"
    # ==========================================
    print("\n➕ Création de la section 'Languages'...")

    # 1. Clic sur le gros bouton "Add new section" en bas
    add_sec_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Add new section')]")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_sec_btn)
    add_sec_btn.click()
    time.sleep(2)

    # 2. Sélection de "Other" (Index 15)
    select_elem = wait.until(EC.visibility_of_element_located((By.ID, "new-section-banner-select")))
    sel = Select(select_elem)
    try:
        sel.select_by_value("15: custom-section")
    except:
        sel.select_by_visible_text("Other")
    time.sleep(1)

    # 3. Nommer la section "Languages"
    print("   -> Renommage de la section en 'Languages'...")
    title_sec = wait.until(EC.visibility_of_element_located((By.ID, "new-section-banner-title")))
    title_sec.clear()
    title_sec.send_keys("Languages")
    time.sleep(1)

    # 4. Valider la création de la section
    driver.find_element(By.ID, "add-section").click()
    time.sleep(3)

    # ==========================================
    # 10. AJOUT DES LANGUES (LANGUAGES)
    # ==========================================

    # --- LANGUAGE 1 (Formulaire déjà ouvert) ---
    fill_other("French", "Mother Tongue")

    # --- LANGUAGE 2 ---
    print("   -> Clic sur 'Add new' pour le 2ème language...")

    # On cherche tous les boutons "Add new"
    add_news = driver.find_elements(By.XPATH, "//span[normalize-space()='Add new']")
    if add_news:
        # On prend le DERNIER bouton de la page (celui de la section Languages)
        last_btn = add_news[-1]
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", last_btn)
        last_btn.click()
        time.sleep(2)

        # On remplit le 2ème language
        fill_other("English", "Strong User - C1 Level")
    else:
        print("❌ Erreur : Bouton 'Add new' introuvable.")

    # --- LANGUAGE 3 ---
    print("   -> Clic sur 'Add new' pour le 3ème language...")

    # On cherche tous les boutons "Add new"
    add_news = driver.find_elements(By.XPATH, "//span[normalize-space()='Add new']")
    if add_news:
        # On prend le DERNIER bouton de la page (celui de la section Languages)
        last_btn = add_news[-1]
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", last_btn)
        last_btn.click()
        time.sleep(2)

        # On remplit le 3ème language
        fill_other("German", "Basic User - A2 Level")
    else:
        print("❌ Erreur : Bouton 'Add new' introuvable.")

 # ==========================================
    # 11. CRÉATION DE LA SECTION "INTERESTS"
    # ==========================================
    print("\n➕ Création de la section 'Interests'...")

    # 1. Clic sur le gros bouton "Add new section" en bas
    add_sec_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Add new section')]")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_sec_btn)
    add_sec_btn.click()
    time.sleep(2)

    # 2. Sélection de "Other" (Index 15 ou texte)
    select_elem = wait.until(EC.visibility_of_element_located((By.ID, "new-section-banner-select")))
    sel = Select(select_elem)
    try:
        sel.select_by_value("15: custom-section")
    except:
        sel.select_by_visible_text("Other")
    time.sleep(1)

    # 3. Nommer la section "Interests"
    print("   -> Renommage de la section en 'Interests'...")
    title_sec = wait.until(EC.visibility_of_element_located((By.ID, "new-section-banner-title")))
    title_sec.clear()
    title_sec.send_keys("Interests")
    time.sleep(1)

    # 4. Valider la création de la section
    driver.find_element(By.ID, "add-section").click()
    time.sleep(3)

    # ==========================================
    # 12. AJOUT DES INTÉRÊTS (INTERESTS)
    # ==========================================

    # --- INTEREST 1 : Tech (Formulaire déjà ouvert) ---
    fill_other("Open Source", "Active contributor to Python libraries on GitHub.")

    # --- INTEREST 2 : Sport ---
    print("   -> Clic sur 'Add new' pour le 2ème intérêt...")
    add_news = driver.find_elements(By.XPATH, "//span[normalize-space()='Add new']")
    if add_news:
        last_btn = add_news[-1] # Le dernier bouton est celui de la section Interests
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", last_btn)
        last_btn.click()
        time.sleep(2)

        fill_other("Hiking", "Trekking in the Alps and Pyrenees.")

    # --- INTEREST 3 : Hobby ---
    print("   -> Clic sur 'Add new' pour le 3ème intérêt...")
    add_news = driver.find_elements(By.XPATH, "//span[normalize-space()='Add new']")
    if add_news:
        last_btn = add_news[-1]
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", last_btn)
        last_btn.click()
        time.sleep(2)

        fill_other("Photography", "Street photography and digital editing.")

    # ==========================================
    # 13. CLIC SUR LE BOUTON "NEXT"
    # ==========================================
    print("\n➡️ Clic sur 'Next' pour passer au design...")

    # On cherche un bouton (ou un lien) qui contient le texte "Next"
    # L'utilisation de contains(., 'Next') permet de trouver le bouton même si le texte est dans un span enfant
    next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next')] | //a[contains(., 'Next')]")))

    # On scroll vers le bouton pour être sûr qu'il est visible
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
    time.sleep(1)

    # On clique
    next_btn.click()

    print("   -> Page suivante chargée (Choix du design).")
    time.sleep(5) # On attend que la page de design se charge

    print("\n🎉 TERMINÉ ! CV Complet (Jobs, Diplômes, Skills, Langues, Intérêts).")
    time.sleep(600)

except Exception as e:
    print(f"❌ ERREUR : {e}")
    time.sleep(600)
finally:
    driver.quit()
