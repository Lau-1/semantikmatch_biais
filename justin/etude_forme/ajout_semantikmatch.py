from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# --- CONFIGURATION ---
EMAIL = "stephane@semantikmatch.com"
PASSWORD = "SemantikmatchEnsai26*"
URL = "https://v1.semantikmatch.com/"
DOSSIER_PARENT = "100cv_good"

def run_batch_upload():
    if not os.path.exists(DOSSIER_PARENT):
        print(f"❌ Erreur : Chemin introuvable : {DOSSIER_PARENT}")
        return

    subfolders = [f.path for f in os.scandir(DOSSIER_PARENT) if f.is_dir()]
    subfolders.sort()
    print(f"📂 {len(subfolders)} dossiers détectés.")

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 20)

    try:
        # 1. Connexion
        driver.get(URL)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='email']"))).send_keys(EMAIL)
        driver.find_element(By.CLASS_NAME, "submitButton").click()
        wait.until(EC.element_to_be_clickable((By.ID, "password"))).send_keys(PASSWORD)
        driver.find_element(By.ID, "kc-login").click()

        # 2. Navigation Étude
        time.sleep(2)
        dropdown_trigger = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class, 'select') and contains(text(), 'Telecom Paris')]")
        ))
        dropdown_trigger.click()
        study_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Bias study on CV v2')]")))
        driver.execute_script("arguments[0].click();", study_option)

        # 3. BOUCLE D'UPLOAD
        for i, path in enumerate(subfolders):
            nom = os.path.basename(path)
            print(f"🚀 [{i+1}/{len(subfolders)}] Traitement de : {nom}")

            # --- SÉLECTEUR DE BOUTON INTELLIGENT ---
            # Il cherche le bouton "Ajouter un candidat" peu importe sa classe (empty-state ou primary)
            xpath_bouton = "//button[contains(., 'Ajouter un candidat')]"

            print("trouvé")

            btn_add = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_bouton)))
            driver.execute_script("arguments[0].click();", btn_add)

            print("clic")

            # 4. Envoi du dossier
            file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
            file_input.send_keys(path)

            # 5. Clic sur Importer
            try:
                btn_importer = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Importer') or contains(., 'Importer')]")
                ))
                btn_importer.click()
                print(f"✅ Import lancé pour {nom}")
            except:
                print(f"⚠️ Bouton Importer non trouvé, tentative de continuer...")

            # Attente pour l'upload (ajuste selon la vitesse de connexion)
            time.sleep(1)

            # Fermeture de sécurité
            try:
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            except:
                pass

        print("\n🎉 Félicitations ! Les 100 dossiers sont importés.")

    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    run_batch_upload()
