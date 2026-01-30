import json
import re
import os

# --- CONFIGURATION STATIQUE ---
# Mapping des fichiers sources vers les clés du JSON final
INPUT_FILES_MAP = {
    "original.json": "Original",
    "gender.json": "Gender",
    "origin.json": "Origin",
    "age.json": "Age"
}

# Structure finale des données
FINAL_DATA_TEMPLATE = {
    "experiences": {},
    "studies": {},
    "interests": {}
}

# --- FONCTIONS UTILITAIRES ---

def get_normalized_cv_id(key_string):
    """
    Transforme 'CV 000 Age' ou 'CV 298 Original' en 'CV0' ou 'CV298'.
    """
    match = re.search(r"CV\s*(\d+)", key_string, re.IGNORECASE)
    if match:
        number = int(match.group(1))
        return f"CV{number}"
    return key_string.split()[0]

def run_jointure(run_name):
    """
    Fonction principale appelée par le main.py
    :param run_name: Le nom du dossier (ex: "run1")
    """
    # 1. Définition des chemins dynamiques basés sur la run choisie
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Entrée : On va chercher dans le dossier généré par l'étape précédente
    input_dir = os.path.join(base_dir, 'resultats_csv_to_json', run_name)

    # Sortie : On crée un dossier pour la jointure
    output_root = os.path.join(base_dir, 'resultats_jointure_json')
    output_dir = os.path.join(output_root, run_name)

    print(f"\n--- Démarrage de la jointure pour : {run_name} ---")
    print(f"Lecture depuis : {input_dir}")

    # Vérification du dossier source
    if not os.path.exists(input_dir):
        print(f"❌ ERREUR : Le dossier source '{input_dir}' n'existe pas.")
        print("Avez-vous lancé l'étape 'CSV to JSON' pour cette run avant ?")
        return

    # Création du dossier de sortie
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Dossier de sortie créé : {output_dir}")

    # Réinitialisation de la structure de données pour cette exécution
    # On utilise une copie pour éviter de garder les données des runs précédentes en mémoire
    current_data = {
        "experiences": {},
        "studies": {},
        "interests": {}
    }

    files_found = False

    # Traitement des fichiers
    for filename, source_label in INPUT_FILES_MAP.items():
        file_path = os.path.join(input_dir, filename)

        if not os.path.exists(file_path):
            print(f"⚠️  Fichier introuvable : {filename} (Ignoré)")
            continue

        files_found = True
        print(f"Traitement de {filename}...")

        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                content = json.load(f)
            except json.JSONDecodeError:
                print(f"❌ ERREUR JSON : Impossible de lire {filename}")
                continue

            for raw_cv_key, cv_data in content.items():
                cv_id = get_normalized_cv_id(raw_cv_key)

                # Experiences
                if cv_id not in current_data["experiences"]:
                    current_data["experiences"][cv_id] = {}
                current_data["experiences"][cv_id][source_label] = cv_data.get("List of professional experiences", [])

                # Studies
                if cv_id not in current_data["studies"]:
                    current_data["studies"][cv_id] = {}
                current_data["studies"][cv_id][source_label] = cv_data.get("List of studies", [])

                # Interests
                if cv_id not in current_data["interests"]:
                    current_data["interests"][cv_id] = {}
                current_data["interests"][cv_id][source_label] = cv_data.get("List of personal interests", [])

    if not files_found:
        print("❌ Aucun fichier source n'a été traité.")
        return

    # Écriture des résultats
    output_files_config = {
        "experiences": "experiences.json",
        "studies": "studies.json",
        "interests": "interests.json"
    }

    print("-" * 30)
    for category, filename in output_files_config.items():
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(current_data[category], f, indent=4, ensure_ascii=False)
        print(f"✅ Succès : {filename}")

    print("-" * 30)
    print(f"Terminé. Résultats disponibles dans : {output_dir}")

# Le bloc ci-dessous permet de tester le fichier seul si besoin (ex: python jointure_json.py)
if __name__ == "__main__":
    # Valeur par défaut pour test manuel
    run_test = "run1"
    run_jointure(run_test)
