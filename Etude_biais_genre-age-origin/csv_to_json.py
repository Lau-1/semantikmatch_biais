import pandas as pd
import json
import os

def transform_cv_data(input_path, output_path, extraction_type):
    """
    Transforme un CSV d'extraction en JSON formaté.
    :param input_path: Chemin vers le fichier CSV source
    :param output_path: Chemin vers le fichier JSON de sortie
    :param extraction_type: Le type d'extraction (original, origin, age, gender) pour nommer les clés
    """

    # Lecture du CSV avec le séparateur ';'
    try:
        df = pd.read_csv(input_path, sep=';')
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier '{input_path}' est introuvable.")
        return
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du CSV : {e}")
        return

    json_output = {}

    for index, row in df.iterrows():
        # 1. Création de la clé dynamique (ex: "CV Jean Original" ou "CV Jean Origin")
        cv_name = row['Name']
        # On met une majuscule au type (original -> Original)
        key_name = f"{cv_name} {extraction_type.capitalize()}"

        # 2. Traitement des expériences professionnelles
        prof_exp_raw = row.get('Professional Experience-value') # .get est plus sûr
        prof_experiences = []
        if pd.notna(prof_exp_raw):
            try:
                prof_experiences = json.loads(prof_exp_raw)
            except json.JSONDecodeError:
                prof_experiences = []

        # 3. Traitement des études
        studies_raw = row.get('Studies-value')
        studies_obj = {}
        if pd.notna(studies_raw):
            try:
                studies_list = json.loads(studies_raw)
                if isinstance(studies_list, list) and len(studies_list) > 0:
                    studies_obj = studies_list[0]
                elif isinstance(studies_list, dict):
                    studies_obj = studies_list
            except json.JSONDecodeError:
                pass

        # 4. Traitement des intérêts personnels
        interests_raw = row.get('Interests-value')
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

    # Création du dossier parent si nécessaire (géré par le main, mais sécurité supplémentaire)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Sauvegarde dans le fichier JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, indent=4, ensure_ascii=False)

    print(f"✅ Succès ! Fichier généré : {output_path} ({len(json_output)} entrées)")

if __name__ == "__main__":
    # Petit test par défaut si on lance ce fichier directement
    print("Veuillez lancer main.py pour utiliser le menu interactif.")
