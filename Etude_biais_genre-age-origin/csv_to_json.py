import pandas as pd
import json
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, 'run1/'))

# Configuration des noms de fichiers
input_file = f"{project_root}/extraction_original.csv"
output_file = f"{project_root}/output.json"

def transform_cv_data(input_path, output_path):
    # Lecture du CSV avec le séparateur ';'
    try:
        df = pd.read_csv(input_path, sep=';')
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{input_path}' est introuvable.")
        return

    json_output = {}

    for index, row in df.iterrows():
        # 1. Création de la clé "CV XXX Original"
        cv_name = row['Name']
        key_name = f"{cv_name} Original"

        # 2. Traitement des expériences professionnelles
        # Le CSV contient une string JSON représentant une liste de dictionnaires
        prof_exp_raw = row['Professional Experience-value']
        prof_experiences = []
        if pd.notna(prof_exp_raw):
            try:
                prof_experiences = json.loads(prof_exp_raw)
            except json.JSONDecodeError:
                prof_experiences = []

        # 3. Traitement des études
        # Le CSV contient une liste, mais le format de sortie demande un objet unique (dictionnaire)
        studies_raw = row['Studies-value']
        studies_obj = {}
        if pd.notna(studies_raw):
            try:
                studies_list = json.loads(studies_raw)
                # On prend le premier élément de la liste s'il existe (le plus récent généralement)
                if isinstance(studies_list, list) and len(studies_list) > 0:
                    studies_obj = studies_list[0]
                elif isinstance(studies_list, dict):
                    studies_obj = studies_list
            except json.JSONDecodeError:
                pass

        # 4. Traitement des intérêts personnels
        # Le CSV contient une liste d'objets {"desc": ..., "title": ...}
        # On veut une liste simple de strings contenant uniquement les titres
        interests_raw = row['Interests-value']
        interests_list = []
        if pd.notna(interests_raw):
            try:
                interests_data = json.loads(interests_raw)
                if isinstance(interests_data, list):
                    interests_list = [item.get('title') for item in interests_data if item.get('title')]
            except json.JSONDecodeError:
                pass

        # Construction de l'objet final pour ce CV
        json_output[key_name] = {
            "List of professional experiences": prof_experiences,
            "List of studies": studies_obj,
            "List of personal interests": interests_list
        }

    # Sauvegarde dans le fichier JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, indent=4, ensure_ascii=False)

    print(f"Succès ! Le fichier '{output_path}' a été généré avec {len(json_output)} entrées.")

if __name__ == "__main__":
    transform_cv_data(input_file, output_file)
