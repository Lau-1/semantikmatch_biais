import os
from csv_to_json import transform_cv_data
from jointure_json import run_jointure

def get_available_runs(base_path):
    """Liste tous les dossiers commençant par 'run' dans le répertoire courant."""
    runs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d)) and d.startswith('run')]
    runs.sort()
    return runs

def menu_select_run(runs):
    """Affiche le menu de sélection de la run et retourne le choix."""
    print("\n--- SÉLECTION DE LA RUN ---")
    for i, run in enumerate(runs):
        print(f"{i + 1}. {run}")

    while True:
        try:
            choice = int(input("\nChoisissez le numéro de la run : "))
            if 1 <= choice <= len(runs):
                return runs[choice - 1]
            print("Choix invalide.")
        except ValueError:
            print("Veuillez entrer un nombre.")

def process_csv_to_json(base_path, selected_run):
    """
    Détecte et convertit automatiquement tous les fichiers CSV d'une run.
    """
    input_run_path = os.path.join(base_path, selected_run)

    # Dossier de sortie : ./resultats_csv_to_json/runX/
    output_base_folder = os.path.join(base_path, "resultats_csv_to_json")
    output_run_folder = os.path.join(output_base_folder, selected_run)

    # 1. Vérification que le dossier source existe
    if not os.path.exists(input_run_path):
        print(f"❌ Erreur : Le dossier {input_run_path} n'existe pas.")
        return

    # 2. Récupération de tous les fichiers 'extraction_*.csv'
    all_files = os.listdir(input_run_path)
    csv_files = [f for f in all_files if f.startswith("extraction_") and f.endswith(".csv")]

    if not csv_files:
        print(f"⚠️ Aucun fichier 'extraction_*.csv' trouvé dans {selected_run}.")
        return

    # Création du dossier de sortie s'il n'existe pas
    if not os.path.exists(output_run_folder):
        os.makedirs(output_run_folder)

    print(f"\n--- [CSV TO JSON] Traitement automatique pour {selected_run} ---")
    print(f"{len(csv_files)} fichier(s) détecté(s).")

    # 3. Traitement en boucle
    for filename in csv_files:
        # On extrait le type en retirant le préfixe et l'extension
        # ex: extraction_original.csv -> original
        file_type = filename.replace("extraction_", "").replace(".csv", "")

        input_path = os.path.join(input_run_path, filename)
        output_path = os.path.join(output_run_folder, f"{file_type}.json")

        print(f"Traitement de : {file_type}...")

        try:
            transform_cv_data(input_path, output_path, file_type)
        except Exception as e:
            print(f"❌ Erreur lors du traitement de {filename} : {e}")

    print(f"\n✅ Terminé. Les fichiers JSON sont dans : {output_run_folder}")

def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    runs = get_available_runs(base_path)

    if not runs:
        print("Aucun dossier 'run' trouvé dans ce répertoire.")
        return

    # --- ÉTAPE 0 : MENU PRINCIPAL ---
    print("\n=== MENU PRINCIPAL ===")
    print("1. Transformer CSV en JSON (Tout le dossier)")
    print("2. Faire la Jointure des JSONs")

    action = 0
    while True:
        try:
            action = int(input("Votre choix (1 ou 2) : "))
            if action in [1, 2]:
                break
            print("Choix invalide.")
        except ValueError:
            print("Entrez 1 ou 2.")

    # --- ÉTAPE 1 : CHOIX DE LA RUN ---
    selected_run = menu_select_run(runs)

    # --- ÉTAPE 2 : EXÉCUTION ---
    if action == 1:
        process_csv_to_json(base_path, selected_run)
    elif action == 2:
        run_jointure(selected_run)

if __name__ == "__main__":
    main()
