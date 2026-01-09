import json
import re
import os

# --- Dossiers racine ---
EXTRACTION_BASE_DIR = "Extraction/data"
OUTPUT_BASE_DIR = "Mise_en_forme/data"

BIAISES = ["age", "genre", "origin"]

def load_json(filename):
    """Charge un fichier JSON."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Fichier introuvable : {filename}")
        return {}
    except json.JSONDecodeError:
        print(f"⚠️ JSON invalide : {filename}")
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
    if isinstance(entry, dict) and key_name in entry:
        return entry[key_name]
    return []

def get_cv_number(filename):
    match = re.search(r'CV(\d+)', filename)
    return int(match.group(1)) if match else 0

def merge_single_bias(run_dir, run_name, bias):
    exp_file = os.path.join(run_dir, f"{bias}_experiences.json")
    int_file = os.path.join(run_dir, f"{bias}_interests.json")
    stu_file = os.path.join(run_dir, f"{bias}_studies.json")

    data_exp = load_json(exp_file)
    data_int = load_json(int_file)
    data_edu = load_json(stu_file)

    if not data_exp or not data_int or not data_edu:
        print(f"⏭️  Skip {run_name} / {bias} (fichiers manquants)")
        return

    all_keys = set(data_exp) | set(data_int) | set(data_edu)
    merged_output = {}

    for original_key in all_keys:
        new_key = os.path.splitext(original_key)[0]
        merged_output[new_key] = {
            "List of professional experiences": extract_list(data_exp.get(original_key, {}), "experiences"),
            "List of studies": extract_studies(data_edu.get(original_key, {})),
            "List of personal interests": extract_list(data_int.get(original_key, {}), "interests"),
        }

    sorted_keys = sorted(merged_output.keys(), key=get_cv_number)
    sorted_output = {k: merged_output[k] for k in sorted_keys}

    output_run_dir = os.path.join(OUTPUT_BASE_DIR, run_name)
    os.makedirs(output_run_dir, exist_ok=True)

    output_file = os.path.join(output_run_dir, f"{bias}_merged.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sorted_output, f, indent=4, ensure_ascii=False)

    print(f"✅ {output_file} créé")

def main():
    for run_name in os.listdir(EXTRACTION_BASE_DIR):
        run_dir = os.path.join(EXTRACTION_BASE_DIR, run_name)

        if not os.path.isdir(run_dir) or not run_name.lower().startswith("run_"):
            continue

        print(f"\n📂 Traitement de {run_name}")

        for bias in BIAISES:
            merge_single_bias(run_dir, run_name, bias)

if __name__ == "__main__":
    main()
