import os
import sys

# --- CONFIGURATION DU CHEMIN PYTHON ---
base_path = os.path.dirname(os.path.abspath(__file__))

# On définit le chemin vers le sous-dossier d'analyse pour les imports
analyse_path = os.path.join(base_path, 'fichiers_analyse')
if analyse_path not in sys.path:
    sys.path.append(analyse_path)

# --- IMPORTS ---
from csv_to_json import transform_cv_data
from jointure_json import run_jointure
import synthese # Import du module de synthèse

try:
    from analyseage import AnalyseAge
    from analysegenre import AnalyseGenre
    from analyseorigin import AnalyseOrigin
except ImportError as e:
    print(f"❌ Erreur d'importation : {e}")
    sys.exit(1)

def get_available_runs(root_path):
    """Liste tous les dossiers commençant par 'run' dans le répertoire donné."""
    if not os.path.exists(root_path):
        return []
    runs = [d for d in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, d)) and d.startswith('run')]
    runs.sort()
    return runs

def menu_select_run(runs):
    """
    Affiche le menu de sélection de la run.
    Permet aussi de SAISIR manuellement le nom.
    """
    print("\n--- SÉLECTION DE LA RUN ---")
    for i, run in enumerate(runs):
        print(f"{i + 1}. {run}")

    # Ajout de l'option de saisie manuelle
    print("M. Saisir le nom du dossier manuellement")

    while True:
        choice = input("\nVotre choix (Numéro ou 'M') : ").strip()

        # Gestion Saisie Manuelle
        if choice.lower() == 'm':
            manual_name = input("✍️  Entrez le nom exact du dossier run : ").strip()
            if manual_name:
                return manual_name
            else:
                print("Le nom ne peut pas être vide.")
                continue

        # Gestion Sélection Numérique
        try:
            idx = int(choice)
            if 1 <= idx <= len(runs):
                return runs[idx - 1]
            print("Numéro invalide.")
        except ValueError:
            print("Entrée invalide. Tapez un numéro ou 'M'.")

def process_csv_to_json(root_path, selected_run):
    """Option 1 : CSV vers JSON."""
    input_run_path = os.path.join(root_path, selected_run)
    output_base_folder = os.path.join(root_path, "resultats_csv_to_json")
    output_run_folder = os.path.join(output_base_folder, selected_run)

    if not os.path.exists(input_run_path):
        print(f"❌ Erreur : Le dossier source {input_run_path} n'existe pas.")
        return

    all_files = os.listdir(input_run_path)
    csv_files = [f for f in all_files if f.startswith("extraction_") and f.endswith(".csv")]

    if not csv_files:
        print(f"⚠️ Aucun fichier CSV trouvé dans {selected_run}.")
        return

    if not os.path.exists(output_run_folder):
        os.makedirs(output_run_folder)

    print(f"\n--- Traitement CSV -> JSON pour {selected_run} ---")
    for filename in csv_files:
        file_type = filename.replace("extraction_", "").replace(".csv", "")
        input_path = os.path.join(input_run_path, filename)
        output_path = os.path.join(output_run_folder, f"{file_type}.json")
        try:
            transform_cv_data(input_path, output_path, file_type)
        except Exception as e:
            print(f"❌ Erreur {filename} : {e}")

    print(f"✅ Terminé : {output_run_folder}")

def process_analyses(selected_run):
    """Option 3 : Lance les analyses."""
    print(f"\n🚀 Lancement des analyses pour : {selected_run}")

    abs_input_dir = os.path.join(base_path, "resultats_jointure_json")
    abs_output_dir = os.path.join(base_path, "resultats_analyses")
    run_source_check = os.path.join(abs_input_dir, selected_run)

    if not os.path.exists(run_source_check):
        print(f"❌ Erreur critique : Le dossier source pour cette run n'existe pas.")
        print(f"   Chemin cherché : {run_source_check}")
        print("   -> Avez-vous lancé l'étape 2 (Jointure) ?")
        return

    analyses = [
        AnalyseAge(),
        AnalyseGenre(),
        AnalyseOrigin()
    ]

    for analyseur in analyses:
        print(f"\n------------------------------------------------")
        print(f"🔎 Analyse : {analyseur.biais_name}")
        print(f"------------------------------------------------")

        try:
            analyseur.process_runs(
                input_root=abs_input_dir,
                output_root=abs_output_dir,
                target_runs=[selected_run]
            )
        except Exception as e:
            print(f"❌ Erreur durant l'analyse {analyseur.biais_name} : {e}")

    print(f"\n✅ Toutes les analyses sont terminées pour {selected_run}.")
    print(f"📁 Résultats ici : {os.path.join(abs_output_dir, selected_run)}")

def main():
    runs = get_available_runs(base_path)

    # Note : Si aucun dossier run n'est trouvé, on permet quand même l'exécution
    # car l'utilisateur voudra peut-être saisir un nom manuellement.
    if not runs:
        print(f"ℹ️  Aucun dossier 'run*' détecté automatiquement.")

    # --- MENU ACTION ---
    print("\n=== MENU PRINCIPAL ===")
    print("1. Transformer CSV en JSON")
    print("2. Faire la Jointure des JSONs")
    print("3. Lancer les analyses (Age, Genre, Origine)")
    print("4. Synthèse et Reporting")

    while True:
        try:
            action = int(input("Votre choix (1, 2, 3 ou 4) : "))
            if action in [1, 2, 3, 4]:
                break
        except ValueError:
            pass
        print("Choix invalide.")

    # --- SÉLECTION DE LA RUN ---
    # On demande quelle run traiter, soit via la liste, soit manuellement
    selected_run = menu_select_run(runs)

    # --- EXÉCUTION ---
    if action == 1:
        process_csv_to_json(base_path, selected_run)
    elif action == 2:
        run_jointure(selected_run)
    elif action == 3:
        process_analyses(selected_run)
    elif action == 4:
        # Appel au module synthese
        synthese.run_synthese_interactive(base_path, selected_run)

if __name__ == "__main__":
    main()
