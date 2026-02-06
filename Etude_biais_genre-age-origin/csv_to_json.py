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
        # On force le type string pour éviter que pandas interprète mal certaines colonnes
        df = pd.read_csv(input_path, sep=';', dtype=str)
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier '{input_path}' est introuvable.")
        return
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du CSV : {e}")
        return

    json_output = {}

    for index, row in df.iterrows():
        # 1. Création de la clé dynamique (ex: "CV Jean Original" ou "CV Jean Origin")
        cv_name = row.get('Name', f"CV_{index}")
        if pd.isna(cv_name):
            cv_name = f"CV_{index}"

        # On met une majuscule au type (original -> Original)
        key_name = f"{cv_name} {extraction_type.capitalize()}"

        # --- 2. Traitement des expériences professionnelles ---
        prof_exp_raw = row.get('Professional Experiences-value')
        prof_experiences = []

        if pd.notna(prof_exp_raw) and prof_exp_raw != "null":
            try:
                data = json.loads(prof_exp_raw)
                if isinstance(data, list):
                    prof_experiences = data
                elif isinstance(data, dict):
                    prof_experiences = [data]
            except json.JSONDecodeError:
                pass # On laisse la liste vide en cas d'erreur

        # --- 3. Traitement des études (CORRECTION MAJEURE) ---
        studies_raw = row.get('Studies-value')
        studies_list_final = [] # On veut une liste d'objets au final

        if pd.notna(studies_raw) and studies_raw != "null" and studies_raw != "[]":
            try:
                studies_data = json.loads(studies_raw)

                # Cas 1 : C'est directement une liste [{"dates":...}, {"dates":...}]
                if isinstance(studies_data, list):
                    studies_list_final = studies_data

                # Cas 2 : C'est un dictionnaire (ex: {"studies": [...]})
                elif isinstance(studies_data, dict):
                    # Sous-cas A : Contient la clé "studies" qui est une liste
                    if "studies" in studies_data and isinstance(studies_data["studies"], list):
                        studies_list_final = studies_data["studies"]
                    # Sous-cas B : C'est un objet étude unique sans clé parente
                    else:
                        studies_list_final = [studies_data]

            except json.JSONDecodeError:
                pass

        # --- 4. Traitement des intérêts personnels ---
        interests_raw = row.get('Interests-value')
        interests_list = []

        if pd.notna(interests_raw) and interests_raw != "null":
            try:
                interests_data = json.loads(interests_raw)
                if isinstance(interests_data, list):
                    # On ne garde que le titre pour faire une liste simple de strings
                    interests_list = [
                        item.get('title') for item in interests_data
                        if isinstance(item, dict) and item.get('title')
                    ]
            except json.JSONDecodeError:
                pass

        # Construction de l'objet final pour ce CV
        json_output[key_name] = {
            "List of professional experiences": prof_experiences,
            "List of studies": studies_list_final,
            "List of personal interests": interests_list
        }

    # Création du dossier parent si nécessaire
    if os.path.dirname(output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Sauvegarde dans le fichier JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, indent=4, ensure_ascii=False)

    print(f"✅ Succès ! Fichier généré : {output_path} ({len(json_output)} entrées)")

if __name__ == "__main__":
    # Petit test par défaut si on lance ce fichier directement
    print("Veuillez lancer main.py pour utiliser le menu interactif.")
