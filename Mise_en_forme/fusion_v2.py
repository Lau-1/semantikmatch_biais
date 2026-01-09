import json
import re
import os

# --- Configuration ---
INPUT_DIR = "Runs_extraction"
OUTPUT_DIR = "Runs_fusion"

CATEGORIES = {
    "original": "original",
    "age": "age",
    "genre": "gender",
    "origin": "origin"
}

def load_json(filepath):
    """Charge un fichier JSON."""
    if not os.path.exists(filepath):
        # On ne print pas d'erreur ici pour éviter de spammer la console si un fichier manque,
        # on retourne juste un dict vide.
        return {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Erreur JSON : {filepath}")
        return {}

def extract_studies(entry):
    if isinstance(entry, list):
        return entry

    if isinstance(entry, dict):
        if "education" in entry:
            return entry["education"]
        if "studies" in entry:
            return entry["studies"]
        if "university" in entry:
            return entry
        if "error" in entry:
            raw_text = entry.get("raw_text", "")
            match = re.search(r'(\{.*\})', raw_text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            return []
    return []

def extract_list(entry, key_name):
    """Extrait une liste simple depuis une clé (pour experiences ou interests)."""
    if isinstance(entry, dict) and key_name in entry:
        return entry[key_name]
    return []

def get_cv_number(key_name):
    """Extrait le numéro du CV pour le tri."""
    match = re.search(r'CV(\d+)', key_name)
    if match:
        return int(match.group(1))
    return 0

def process_category_merge(run_path, prefix):
    """
    Fusionne les 3 fichiers (experiences, interests, studies) pour un préfixe donné.
    """
    file_exp = os.path.join(run_path, f"{prefix}_experiences.json")
    file_int = os.path.join(run_path, f"{prefix}_interests.json")
    file_stu = os.path.join(run_path, f"{prefix}_studies.json")

    data_exp = load_json(file_exp)
    data_int = load_json(file_int)
    data_edu = load_json(file_stu)

    # Si aucun des 3 fichiers n'existe ou n'est chargé, on retourne None
    if not data_exp and not data_int and not data_edu:
        return None

    # Identification de toutes les clés uniques
    all_keys = set(data_exp.keys()) | set(data_int.keys()) | set(data_edu.keys())
    merged_output = {}

    for original_key in all_keys:
        # Nettoyage de la clé (ex: CV1.pdf -> CV1)
        new_key = os.path.splitext(original_key)[0]
        merged_output[new_key] = {}

        # 1. Expériences
        if original_key in data_exp:
            merged_output[new_key]["List of professional experiences"] = extract_list(data_exp[original_key], "experiences")
        else:
            merged_output[new_key]["List of professional experiences"] = []

        # 2. Études
        if original_key in data_edu:
            merged_output[new_key]["List of studies"] = extract_studies(data_edu[original_key])
        else:
            merged_output[new_key]["List of studies"] = []

        # 3. Intérêts
        if original_key in data_int:
            merged_output[new_key]["List of personal interests"] = extract_list(data_int[original_key], "interests")
        else:
            merged_output[new_key]["List of personal interests"] = []

    # Tri par numéro de CV
    sorted_keys = sorted(merged_output.keys(), key=get_cv_number)
    return {k: merged_output[k] for k in sorted_keys}

def main():
    # Vérification dossier source
    if not os.path.exists(INPUT_DIR):
        print(f"Erreur : Le dossier '{INPUT_DIR}' n'existe pas.")
        return

    # Création du dossier racine de sortie
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Liste des sous-dossiers (run1, run2, etc.)
    subdirs = [d for d in os.listdir(INPUT_DIR) if os.path.isdir(os.path.join(INPUT_DIR, d))]
    subdirs.sort() # Pour traiter run1, run2 dans l'ordre

    print(f"Début du traitement des dossiers dans '{INPUT_DIR}'...\n")

    for run_folder in subdirs:
        print(f"--- Traitement de {run_folder} ---")

        # Chemins d'entrée et de sortie spécifiques au run
        input_run_path = os.path.join(INPUT_DIR, run_folder)
        output_run_path = os.path.join(OUTPUT_DIR, run_folder)

        # Création du sous-dossier dans runs_fusion/runX
        if not os.path.exists(output_run_path):
            os.makedirs(output_run_path)

        # Boucle sur les 4 catégories (original, age, genre, origin)
        for input_prefix, output_name in CATEGORIES.items():

            merged_data = process_category_merge(input_run_path, input_prefix)

            if merged_data:
                output_file = os.path.join(output_run_path, f"{output_name}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(merged_data, f, indent=4, ensure_ascii=False)
                print(f"   ✅ Créé : {output_name}.json")
            else:
                print(f"   ⚠️  Ignoré : Pas de données pour '{input_prefix}' dans {run_folder}")

    print(f"\nTerminé ! Tous les fichiers sont dans le dossier '{OUTPUT_DIR}'.")

if __name__ == "__main__":
    main()
