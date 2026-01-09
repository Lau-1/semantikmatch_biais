import json
import re
import os

def transform_cv_files(file_paths, output_dir="."):
    """
    Transforme 4 fichiers JSON (Age, Gender, Origin, Original) en 3 fichiers consolidés
    (studies, experiences, interests) regroupés par CV.

    Args:
        file_paths (dict): Dictionnaire liant le nom de la variante au chemin du fichier.
                           Ex: {"Age": "age.json", "Gender": "gender.json", ...}
        output_dir (str): Dossier où sauvegarder les fichiers de sortie.
    """

    # Structure pour stocker les données consolidées
    # Format: { "CV0": { "Age": [...], "Original": [...] }, "CV1": ... }
    consolidated_data = {
        "studies": {},
        "experiences": {},
        "interests": {}
    }

    # Mapping entre les clés du JSON d'entrée et nos catégories de sortie
    section_mapping = {
        "List of studies": "studies",
        "List of professional experiences": "experiences",
        "List of personal interests": "interests"
    }

    print("Début du traitement des fichiers...")

    for variant_name, file_path in file_paths.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"Traitement de la variante : {variant_name} ({len(data)} entrées)")

            for key, content in data.items():
                # Extraction de l'ID du CV (ex: "CV0 Age" -> "CV0")
                # On utilise une expression régulière pour capturer CV suivi de chiffres
                match = re.search(r"(CV\d+)", key)

                if match:
                    cv_id = match.group(1)
                else:
                    # Fallback si la clé est juste "CV0" sans suffixe
                    cv_id = key.split()[0]

                # Pour chaque section (études, expériences, intérêts)
                for input_key, output_category in section_mapping.items():
                    # Initialisation de la clé CV si elle n'existe pas encore
                    if cv_id not in consolidated_data[output_category]:
                        consolidated_data[output_category][cv_id] = {}

                    # Récupération de la donnée (liste vide si absente)
                    item_data = content.get(input_key, [])

                    # Ajout dans la structure finale sous le nom de la variante
                    consolidated_data[output_category][cv_id][variant_name] = item_data

        except FileNotFoundError:
            print(f"Erreur : Le fichier {file_path} est introuvable.")
            return
        except json.JSONDecodeError:
            print(f"Erreur : Le fichier {file_path} n'est pas un JSON valide.")
            return

    # Sauvegarde des 3 fichiers de sortie
    output_files = ["studies.json", "experiences.json", "interests.json"]

    for filename in output_files:
        category = filename.replace(".json", "") # "studies", "experiences"...
        output_path = os.path.join(output_dir, filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(consolidated_data[category], f, indent=4, ensure_ascii=False)

        print(f"Fichier généré : {output_path}")

    print("Transformation terminée avec succès.")

# --- Exemple d'utilisation ---

# Définissez ici les chemins vers vos 4 fichiers
files_config = {
    "Age": "age.json",
    "Gender": "gender.json",
    "Origin": "origin.json",
    "Original": "original.json"
}

# Appel de la fonction (décommentez pour exécuter si vous avez les fichiers en local)
#
transform_cv_files(files_config)
