import json
import re
import os

# --- Configuration des noms de fichiers ---
FILE_EXPERIENCES = "experiences.json"
FILE_INTERESTS = "interests.json"
FILE_STUDIES = "studies.json"
FILE_OUTPUT = "merged.json"

def load_json(filename):
    """Charge un fichier JSON."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erreur : Le fichier {filename} est introuvable.")
        return {}
    except json.JSONDecodeError:
        print(f"Erreur : Le fichier {filename} n'est pas un JSON valide.")
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

def get_cv_number(filename):
    """
    Extrait le numéro du CV pour le tri.
    """
    match = re.search(r'CV(\d+)', filename)
    if match:
        return int(match.group(1))
    return 0

def main():
    # 1. Chargement des données
    data_exp = load_json(FILE_EXPERIENCES)
    data_int = load_json(FILE_INTERESTS)
    data_edu = load_json(FILE_STUDIES)

    if not data_exp or not data_int or not data_edu:
        print("Annulation : Impossible de charger toutes les données.")
        return

    # 2. Identification de toutes les clés uniques
    all_keys = set(data_exp.keys()) | set(data_int.keys()) | set(data_edu.keys())

    merged_output = {}

    for original_key in all_keys:
        new_key = os.path.splitext(original_key)[0]

        merged_output[new_key] = {}

        # 3. Fusion des Expériences
        if original_key in data_exp:
            merged_output[new_key]["List of professional experiences"] = extract_list(data_exp[original_key], "experiences")
        else:
            merged_output[new_key]["List of professional experiences"] = []

        # 4. Fusion des Études
        if original_key in data_edu:
            merged_output[new_key]["List of studies"] = extract_studies(data_edu[original_key])
        else:
            merged_output[new_key]["List of studies"] = []

        # 5. Fusion des Intérêts
        if original_key in data_int:
            merged_output[new_key]["List of personal interests"] = extract_list(data_int[original_key], "interests")
        else:
            merged_output[new_key]["List of personal interests"] = []

    # 6. Tri des clés par numéro de CV
    sorted_keys = sorted(merged_output.keys(), key=get_cv_number)

    sorted_output = {k: merged_output[k] for k in sorted_keys}

    # 7. Sauvegarde du résultat
    with open(FILE_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(sorted_output, f, indent=4, ensure_ascii=False)

    print(f"Fusion terminée avec succès ! Le fichier '{FILE_OUTPUT}' a été créé (trié par numéro).")

if __name__ == "__main__":
    main()
