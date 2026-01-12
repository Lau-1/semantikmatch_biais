import json
import re
import os

# --- Configuration ---
INPUT_DIR = "Extract_via_semantikmatch"
OUTPUT_DIR = "Runs_jointure"

# Configuration des fichiers attendus dans chaque dossier "run"
# Clé = Nom de la variante (utilisé dans le JSON final), Valeur = Nom du fichier source
FILES_MAPPING = {
    "Age": "age.json",
    "Gender": "gender.json", # Attention à bien matcher le nom généré par le script précédent
    "Origin": "origin.json",
    "Original": "original.json"
}

def transform_run(run_input_path, run_output_path):
    """
    Traite un sous-dossier spécifique (ex: run1) et génère les 3 fichiers consolidés.
    """

    # 1. Préparation des chemins de fichiers pour ce run
    file_paths = {}
    for variant_name, filename in FILES_MAPPING.items():
        full_path = os.path.join(run_input_path, filename)
        # On ne traite que si le fichier existe
        if os.path.exists(full_path):
            file_paths[variant_name] = full_path
        else:
            print(f"   ⚠️  Fichier manquant : {filename} dans {run_input_path}")

    if not file_paths:
        print(f"   ❌ Aucun fichier valide trouvé dans {run_input_path}. Passage au suivant.")
        return

    # 2. Structure pour stocker les données consolidées
    consolidated_data = {
        "studies": {},
        "experiences": {},
        "interests": {}
    }

    section_mapping = {
        "List of studies": "studies",
        "List of professional experiences": "experiences",
        "List of personal interests": "interests"
    }

    # 3. Lecture et Fusion des données
    for variant_name, file_path in file_paths.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for key, content in data.items():
                # Extraction de l'ID du CV (ex: "CV0", "CV1.pdf" -> "CV1")
                match = re.search(r"(CV\d+)", key)
                if match:
                    cv_id = match.group(1)
                else:
                    cv_id = key.split()[0] # Fallback

                # Répartition dans les 3 catégories
                for input_key, output_category in section_mapping.items():
                    if cv_id not in consolidated_data[output_category]:
                        consolidated_data[output_category][cv_id] = {}

                    item_data = content.get(input_key, [])
                    consolidated_data[output_category][cv_id][variant_name] = item_data

        except json.JSONDecodeError:
            print(f"   ❌ Erreur JSON dans {file_path}")
            continue

    # 4. Sauvegarde des 3 fichiers de sortie
    if not os.path.exists(run_output_path):
        os.makedirs(run_output_path)

    output_files = ["studies.json", "experiences.json", "interests.json"]

    for filename in output_files:
        category = filename.replace(".json", "")
        output_file_path = os.path.join(run_output_path, filename)

        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(consolidated_data[category], f, indent=4, ensure_ascii=False)

        # Petit log discret pour dire que c'est fait
        # print(f"      -> Généré : {filename}")

def main():
    # Vérification du dossier source
    if not os.path.exists(INPUT_DIR):
        print(f"Erreur : Le dossier '{INPUT_DIR}' est introuvable.")
        return

    # Création du dossier racine de sortie
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Récupération des sous-dossiers (run1, run2...)
    subdirs = [d for d in os.listdir(INPUT_DIR) if os.path.isdir(os.path.join(INPUT_DIR, d))]
    subdirs.sort()

    print(f"Début de la jointure depuis '{INPUT_DIR}' vers '{OUTPUT_DIR}'...\n")

    for run_folder in subdirs:
        print(f"--- Traitement de {run_folder} ---")

        input_run_path = os.path.join(INPUT_DIR, run_folder)
        output_run_path = os.path.join(OUTPUT_DIR, run_folder)

        transform_run(input_run_path, output_run_path)
        print(f"   ✅ {run_folder} terminé.")

    print(f"\nTransformation terminée avec succès ! Vérifiez le dossier '{OUTPUT_DIR}'.")

if __name__ == "__main__":
    main()
