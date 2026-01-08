import json
import re

def get_base_cv_name(full_name):
    # Utilise une regex pour extraire uniquement le "CV" suivi du chiffre (ex: CV99)
    match = re.search(r'(CV\d+)', full_name)
    return match.group(1) if match else full_name

def create_comparison_files(files_map):
    # Dictionnaires pour stocker les données regroupées
    # Structure cible : merged_data[categorie][cv_id][source] = payload
    categories = [
        "List of professional experiences",
        "List of personal interests",
        "List of studies"
    ]
    
    merged_data = {cat: {} for cat in categories}

    # 1. Chargement et regroupement
    for source_label, file_path in files_map.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                
                for full_name, payload_dict in content.items():
                    cv_id = get_base_cv_name(full_name)
                    
                    for cat in categories:
                        if cat in payload_dict:
                            if cv_id not in merged_data[cat]:
                                merged_data[cat][cv_id] = {}
                            
                            # On stocke la valeur correspondante à la source
                            merged_data[cat][cv_id][source_label] = payload_dict[cat]
        except FileNotFoundError:
            print(f"Erreur : Le fichier {file_path} est introuvable.")
            continue

    # 2. Écriture des 3 fichiers JSON
    for cat in categories:
        # Tri par ID de CV (CV0, CV1, CV2...)
        sorted_cv_data = dict(sorted(merged_data[cat].items(), key=lambda x: int(re.search(r'\d+', x[0]).group())))
        
        file_name = f"{cat.lower().replace(' ', '_')}.json"
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(sorted_cv_data, f, indent=4, ensure_ascii=False)
        
        print(f"Fichier de jointure créé : {file_name}")

# --- CONFIGURATION ---
fichiers_sources = {
    "Original": "json/data/run_3/result/original.json",
    "Gender": "json/data/run_3/result/gender.json",
    "Origin": "json/data/run_3/result/origin.json",
    "Age": "json/data/run_3/result/age.json"
}

create_comparison_files(fichiers_sources)