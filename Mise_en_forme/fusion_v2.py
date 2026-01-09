import json
import re
import os

# --- Configuration ---
INPUT_DIR = "Runs_extraction"
OUTPUT_DIR = "runs_fusion"

# Mapping : Préfixe du fichier source -> Nom du fichier de sortie
CATEGORIES = {
    "original": "original",
    "age": "age",
    "genre": "gender",
    "origin": "origin"
}

def load_json(filepath):
    """Charge un fichier JSON."""
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Erreur JSON : {filepath}")
        return {}

def extract_studies(entry):
    """
    Extrait les études.
    Gère les cas complexes : Liste, String, Dict conteneur, ou Dict "objet étude".
    """
    # 1. C'est déjà une liste -> parfait
    if isinstance(entry, list):
        return entry

    # 2. C'est une string simple -> on l'enveloppe
    if isinstance(entry, str):
        return [entry]

    # 3. C'est un dictionnaire
    if isinstance(entry, dict):
        # Cas A : Le dictionnaire est un CONTENEUR (ex: {"education": [...]})
        # On vérifie d'abord ces clés
        wrapper_keys = ["education", "studies", "academic_background"]
        for key in wrapper_keys:
            if key in entry:
                val = entry[key]
                if isinstance(val, list):
                    return val
                if isinstance(val, str):
                    return [val]
                if isinstance(val, dict):
                    return [val] # Un seul objet étude dans la clé

        # Cas B : Le dictionnaire EST l'étude (contient "university", "degree"...)
        # C'est ici qu'on corrige : on garde tout l'objet 'entry'
        if "university" in entry:
            return [entry]

        # Cas C : Gestion des erreurs de parsing LLM
        if "error" in entry:
            raw_text = entry.get("raw_text", "")
            match = re.search(r'(\{.*\})', raw_text, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(1))
                    return extract_studies(parsed)
                except json.JSONDecodeError:
                    pass
            return []

    return []

def extract_experiences(entry):
    """Extrait les expériences."""
    if isinstance(entry, list):
        return entry

    if isinstance(entry, str):
        return [entry]

    if isinstance(entry, dict):
        # Pour les expériences, on cherche généralement une liste dans une clé
        keys_to_check = ["experiences", "professional_experiences", "work_experience", "career"]
        for key in keys_to_check:
            if key in entry:
                val = entry[key]
                if isinstance(val, str):
                    return [val]
                return val
    return []

def extract_interests(entry):
    """Extrait les intérêts."""
    if isinstance(entry, list):
        return entry

    if isinstance(entry, str):
        return [entry]

    if isinstance(entry, dict):
        keys_to_check = ["interests", "personal_interests", "hobbies", "activities"]
        for key in keys_to_check:
            if key in entry:
                val = entry[key]
                if isinstance(val, str):
                    return [val]
                return val
    return []

def get_cv_number(key_name):
    """Extrait le numéro du CV pour le tri."""
    match = re.search(r'CV(\d+)', key_name)
    if match:
        return int(match.group(1))
    return 0

def process_category_merge(run_path, prefix):
    """
    Fusionne les 3 fichiers pour un préfixe donné.
    """
    file_exp = os.path.join(run_path, f"{prefix}_experiences.json")
    file_int = os.path.join(run_path, f"{prefix}_interests.json")
    file_stu = os.path.join(run_path, f"{prefix}_studies.json")

    data_exp = load_json(file_exp)
    data_int = load_json(file_int)
    data_edu = load_json(file_stu)

    if not data_exp and not data_int and not data_edu:
        return None

    all_keys = set(data_exp.keys()) | set(data_int.keys()) | set(data_edu.keys())
    merged_output = {}

    for original_key in all_keys:
        new_key = os.path.splitext(original_key)[0]
        merged_output[new_key] = {}

        # 1. Expériences
        if original_key in data_exp:
            merged_output[new_key]["List of professional experiences"] = extract_experiences(data_exp[original_key])
        else:
            merged_output[new_key]["List of professional experiences"] = []

        # 2. Études
        if original_key in data_edu:
            merged_output[new_key]["List of studies"] = extract_studies(data_edu[original_key])
        else:
            merged_output[new_key]["List of studies"] = []

        # 3. Intérêts
        if original_key in data_int:
            merged_output[new_key]["List of personal interests"] = extract_interests(data_int[original_key])
        else:
            merged_output[new_key]["List of personal interests"] = []

    # Tri par numéro de CV
    sorted_keys = sorted(merged_output.keys(), key=get_cv_number)
    return {k: merged_output[k] for k in sorted_keys}

def main():
    if not os.path.exists(INPUT_DIR):
        print(f"Erreur : Le dossier '{INPUT_DIR}' n'existe pas.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    subdirs = [d for d in os.listdir(INPUT_DIR) if os.path.isdir(os.path.join(INPUT_DIR, d))]
    subdirs.sort()

    print(f"Début du traitement des dossiers dans '{INPUT_DIR}'...\n")

    for run_folder in subdirs:
        print(f"--- Traitement de {run_folder} ---")

        input_run_path = os.path.join(INPUT_DIR, run_folder)
        output_run_path = os.path.join(OUTPUT_DIR, run_folder)

        if not os.path.exists(output_run_path):
            os.makedirs(output_run_path)

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
