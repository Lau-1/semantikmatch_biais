import os
import glob
from csv_to_json import transform_cv_data

def get_available_runs(base_path):
    """Liste tous les dossiers commençant par 'run' dans le répertoire courant."""
    runs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d)) and d.startswith('run')]
    runs.sort() # Pour avoir run1, run2, etc. dans l'ordre
    return runs

def main():
    # Répertoire racine (là où se trouve main.py et csv_to_json.py)
    base_path = os.path.dirname(os.path.abspath(__file__))

    # --- ÉTAPE 1 : CHOIX DE LA RUN ---
    runs = get_available_runs(base_path)

    if not runs:
        print("Aucun dossier 'run' trouvé dans ce répertoire.")
        return

    print("\n--- SÉLECTION DE LA RUN ---")
    for i, run in enumerate(runs):
        print(f"{i + 1}. {run}")

    while True:
        try:
            choice = int(input("\nChoisissez le numéro de la run : "))
            if 1 <= choice <= len(runs):
                selected_run = runs[choice - 1]
                break
            print("Choix invalide.")
        except ValueError:
            print("Veuillez entrer un nombre.")

    # --- ÉTAPE 2 : CHOIX DU TYPE ---
    types = ["original", "origin", "age", "gender"]

    print(f"\n--- SÉLECTION DU TYPE ({selected_run}) ---")
    for i, t in enumerate(types):
        print(f"{i + 1}. {t}")

    while True:
        try:
            choice = int(input("\nChoisissez le numéro du type : "))
            if 1 <= choice <= len(types):
                selected_type = types[choice - 1]
                break
            print("Choix invalide.")
        except ValueError:
            print("Veuillez entrer un nombre.")

    # --- ÉTAPE 3 : CONSTRUCTION DES CHEMINS ---

    # Fichier d'entrée : ex: ./run1/extraction_original.csv
    input_filename = f"extraction_{selected_type}.csv"
    input_path = os.path.join(base_path, selected_run, input_filename)

    # Dossier de sortie : ./résultats csv_to_json/run1/
    output_base_folder = os.path.join(base_path, "resultats csv_to_json")
    output_run_folder = os.path.join(output_base_folder, selected_run)

    # Fichier de sortie : ex: ./résultats csv_to_json/run1/original.json
    output_filename = f"{selected_type}.json"
    output_path = os.path.join(output_run_folder, output_filename)

    # --- ÉTAPE 4 : EXÉCUTION ---
    print(f"\nTraitement en cours...")
    print(f"Source : {input_path}")
    print(f"Destination : {output_path}")

    # Vérification que le CSV source existe bien
    if not os.path.exists(input_path):
        print(f"\n❌ ERREUR CRITIQUE : Le fichier source n'existe pas !")
        print(f"Attendu : {input_path}")
        print("Vérifiez que vous avez bien extrait les données pour ce type.")
        return

    # Lancement de la transformation
    transform_cv_data(input_path, output_path, selected_type)

if __name__ == "__main__":
    main()
