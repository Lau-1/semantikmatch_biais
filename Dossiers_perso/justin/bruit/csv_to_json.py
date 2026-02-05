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

    # 1. Lecture du CSV
    try:
        # On lit le fichier. Si des colonnes manquent, on ne plante pas.
        df = pd.read_csv(input_path, sep=';')
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier '{input_path}' est introuvable.")
        return
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du CSV : {e}")
        return

    json_output = {}

    for index, row in df.iterrows():
        # Création de la clé (ex: "CV 298 Original")
        cv_name = str(row['Name']) # On force en string au cas où
        key_name = f"{cv_name} {extraction_type.capitalize()}"

        # --- A. Traitement des Expériences Professionnelles ---
        prof_exp_raw = row.get('Professional Experiences-value')
        prof_experiences = []

        if pd.notna(prof_exp_raw) and str(prof_exp_raw).strip() != "null":
            try:
                prof_experiences = json.loads(prof_exp_raw)
            except json.JSONDecodeError:
                # Si le JSON est cassé, on laisse une liste vide
                prof_experiences = []

        # --- B. Traitement des Études (Correction importante ici) ---
        studies_raw = row.get('Studies-value')
        studies_final_list = []

        if pd.notna(studies_raw) and str(studies_raw).strip() != "null":
            try:
                parsed_studies = json.loads(studies_raw)

                # CAS 1: C'est un dictionnaire qui contient une clé "studies" (ex: CV 298)
                if isinstance(parsed_studies, dict) and "studies" in parsed_studies:
                    studies_final_list = parsed_studies["studies"]

                # CAS 2: C'est directement une liste (ex: CV 296)
                elif isinstance(parsed_studies, list):
                    studies_final_list = parsed_studies

                # CAS 3: C'est un objet unique, on le met dans une liste
                elif isinstance(parsed_studies, dict):
                    studies_final_list = [parsed_studies]

            except json.JSONDecodeError:
                pass

        # --- C. Traitement des Intérêts ---
        interests_raw = row.get('Interests-value')
        interests_list = []

        if pd.notna(interests_raw) and str(interests_raw).strip() != "null":
            try:
                interests_data = json.loads(interests_raw)
                if isinstance(interests_data, list):
                    # On extrait juste le titre pour avoir une liste de strings propre
                    interests_list = [
                        item.get('title') for item in interests_data
                        if isinstance(item, dict) and item.get('title')
                    ]
            except json.JSONDecodeError:
                pass

        # Construction de l'objet final
        # Note: On garde "List of studies" comme une vraie liste d'objets maintenant
        json_output[key_name] = {
            "List of professional experiences": prof_experiences,
            "List of studies": studies_final_list,
            "List of personal interests": interests_list
        }

    # Création du dossier si besoin
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

    # Sauvegarde
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_output, f, indent=4, ensure_ascii=False)
        print(f"✅ Succès ! Fichier généré : {output_path} ({len(json_output)} entrées)")
    except Exception as e:
        print(f"❌ Erreur lors de l'écriture du JSON : {e}")

if __name__ == "__main__":
    # Assure-toi que le fichier 'cv_filtres.csv' existe bien avant de lancer
    transform_cv_data(
        input_path='cv_filtres.csv',
        output_path='cv_filtre.json',
        extraction_type='original'
    )
