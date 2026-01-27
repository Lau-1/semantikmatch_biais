import pandas as pd
import json
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns

# --- CONFIGURATION ---
FILE_PATH = 'rapport_analyse.json'

# Codes couleurs pour le terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def clear_screen():
    # Nettoie le terminal pour une meilleure lisibilité
    os.system('cls' if os.name == 'nt' else 'clear')

def load_data(file_path):
    if not os.path.exists(file_path):
        print(f"{Colors.FAIL}Erreur: Fichier '{file_path}' introuvable.{Colors.ENDC}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        df = pd.DataFrame(data)

        # --- Préparation des données ---
        # On sépare le 'cv_id' (ex: "Amelie 01") en 'Candidat' et 'Model_ID'
        # On suppose que le format est toujours "Nom Numéro"
        split_data = df['cv_id'].str.rsplit(' ', n=1, expand=True)
        df['Candidat'] = split_data[0]
        df['Model_ID'] = split_data[1]

        return df
    except Exception as e:
        print(f"{Colors.FAIL}Erreur lecture JSON: {e}{Colors.ENDC}")
        return None

def show_plots(df):
    print(f"{Colors.CYAN}Génération des graphiques...{Colors.ENDC}")
    sns.set_theme(style="whitegrid")
    fig = plt.figure(figsize=(16, 8))
    gs = fig.add_gridspec(2, 2)

    # 1. Taux global
    ax1 = fig.add_subplot(gs[0, 0])
    counts = df['coherent'].value_counts()
    ax1.pie(counts, labels=['Cohérent', 'Erreur'], autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'], startangle=90)
    ax1.set_title("Taux de Cohérence Global")

    # 2. Erreurs par Candidat
    ax2 = fig.add_subplot(gs[0, 1])
    # On filtre les erreurs
    errors = df[df['coherent'] == False]
    if not errors.empty:
        sns.countplot(y='Candidat', data=errors, ax=ax2, palette="Reds_r", order=errors['Candidat'].value_counts().index)
        ax2.set_title("Nombre d'erreurs par Candidat")
    else:
        ax2.text(0.5, 0.5, "Pas d'erreurs", ha='center')

    # 3. Heatmap ou Barplot par Numéro de Modèle (1-40)
    ax3 = fig.add_subplot(gs[1, :])
    # Taux d'erreur par numéro de modèle (tous candidats confondus)
    model_stats = df.groupby('Model_ID')['coherent'].mean().reset_index()
    model_stats['error_rate'] = 1 - model_stats['coherent']

    sns.barplot(x='Model_ID', y='error_rate', data=model_stats, ax=ax3, palette="coolwarm")
    ax3.set_title("Taux d'erreur par Numéro de Modèle (1 à 40) - Tous candidats confondus")
    ax3.set_ylabel("Taux d'erreur (0 à 1)")
    ax3.set_xlabel("Numéro du Modèle (CV ID)")
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()

def stat_by_candidate(df):
    clear_screen()
    print(f"{Colors.HEADER}--- STATISTIQUES PAR CANDIDAT ---{Colors.ENDC}\n")

    # Group by Candidat
    stats = df.groupby('Candidat').agg(
        Total=('cv_id', 'count'),
        Erreurs=('coherent', lambda x: (~x).sum())
    )
    stats['Taux_Succes'] = ((stats['Total'] - stats['Erreurs']) / stats['Total'] * 100).round(1)

    # Affichage joli
    print(f"{'Candidat':<15} | {'Total':<6} | {'Erreurs':<8} | {'Succès %':<10}")
    print("-" * 50)
    for index, row in stats.iterrows():
        color = Colors.GREEN if row['Erreurs'] == 0 else (Colors.WARNING if row['Taux_Succes'] > 50 else Colors.FAIL)
        print(f"{color}{index:<15} | {row['Total']:<6} | {row['Erreurs']:<8} | {row['Taux_Succes']:<10}%{Colors.ENDC}")

    print("\n")
    input("Appuyez sur Entrée pour revenir...")

def stat_by_model(df):
    clear_screen()
    print(f"{Colors.HEADER}--- STATISTIQUES PAR MODÈLE (1-40) ---{Colors.ENDC}")
    print("Permet de voir si un numéro de CV spécifique pose problème à tout le monde.\n")

    # Calcul du taux d'échec par Model_ID
    # On convertit en numeric pour trier proprement (1, 2, 10 au lieu de 1, 10, 2)
    df['Model_ID_Int'] = pd.to_numeric(df['Model_ID'])
    stats = df.groupby('Model_ID_Int').agg(
        Total=('cv_id', 'count'),
        Erreurs=('coherent', lambda x: (~x).sum())
    ).sort_values('Model_ID_Int')

    print(f"{'Modèle #':<10} | {'Erreurs (tous candidats)':<25} | {'État':<10}")
    print("-" * 55)

    for index, row in stats.iterrows():
        err_count = row['Erreurs']
        total = row['Total']

        if err_count == 0:
            status = f"{Colors.GREEN}OK{Colors.ENDC}"
        elif err_count == total:
            status = f"{Colors.FAIL}CRITIQUE{Colors.ENDC}" # 100% d'erreur
        else:
            status = f"{Colors.WARNING}INSTABLE{Colors.ENDC}"

        # On affiche seulement ceux qui ont des problèmes pour ne pas polluer, ou tous ?
        # Affichons tout pour la vue d'ensemble, ou filtrons sur ceux avec erreurs > 0
        if err_count > 0:
            print(f"CV {index:<7} | {err_count}/{total:<23} | {status}")

    print("-" * 55)
    print(f"{Colors.CYAN}Note : Les modèles avec 0 erreur ne sont pas affichés par défaut ici pour la lisibilité (sauf modification du code).{Colors.ENDC}")

    print("\n")
    input("Appuyez sur Entrée pour revenir...")

def explore_errors(df):
    while True:
        clear_screen()
        print(f"{Colors.HEADER}--- EXPLORATEUR D'ERREURS ---{Colors.ENDC}")
        print("1. Voir toutes les erreurs d'un Candidat")
        print("2. Voir les erreurs d'un Modèle spécifique (ex: CV 13)")
        print("3. Retour")

        choice = input(f"\n{Colors.BLUE}Votre choix > {Colors.ENDC}")

        if choice == '3':
            break

        subset = pd.DataFrame()
        title_context = ""

        if choice == '1':
            cands = df['Candidat'].unique()
            print("\nCandidats disponibles : ", ", ".join(cands))
            target = input("Nom du candidat (ex: Amelie) : ").strip()
            subset = df[(df['Candidat'] == target) & (df['coherent'] == False)]
            title_context = f"Candidat {target}"

        elif choice == '2':
            target = input("Numéro du Modèle (ex: 13, 01) : ").strip()
            # Gestion du zero padding si l'utilisateur tape "1" au lieu de "01"
            if len(target) == 1 and target.isdigit():
                target = "0" + target
            subset = df[(df['Model_ID'] == target) & (df['coherent'] == False)]
            title_context = f"Modèle #{target}"

        # Affichage des résultats
        if subset.empty:
            print(f"\n{Colors.GREEN}Aucune erreur trouvée pour cette sélection !{Colors.ENDC}")
            input("Entrée pour continuer...")
        else:
            print(f"\n{Colors.FAIL}--- Liste des erreurs pour {title_context} ---{Colors.ENDC}\n")
            for idx, row in subset.iterrows():
                print(f"{Colors.BOLD}ID :{Colors.ENDC} {row['cv_id']}")
                print(f"{Colors.BOLD}Type :{Colors.ENDC} {row['error_type']}")
                print(f"{Colors.BOLD}Détails :{Colors.ENDC}")
                print(f"{Colors.WARNING}{row['details']}{Colors.ENDC}")
                print("-" * 60)

            input("\nAppuyez sur Entrée pour revenir au menu...")

def main_menu():
    df = load_data(FILE_PATH)
    if df is None:
        return

    while True:
        clear_screen()
        print(f"{Colors.HEADER}========================================{Colors.ENDC}")
        print(f"{Colors.HEADER}    ANALYSEUR DE CV - DASHBOARD CLI     {Colors.ENDC}")
        print(f"{Colors.HEADER}========================================{Colors.ENDC}")
        print(f"Données chargées : {len(df)} entrées")
        print("----------------------------------------")
        print("1. 📊 Afficher les Graphiques (Pop-up)")
        print("2. 👤 Statistiques par Candidat")
        print("3. 🔢 Statistiques par Modèle (1-40)")
        print("4. 🔍 Explorer les détails des erreurs (Texte)")
        print("5. 🚪 Quitter")
        print("----------------------------------------")

        choice = input(f"{Colors.BLUE}Choisissez une option [1-5] > {Colors.ENDC}")

        if choice == '1':
            show_plots(df)
        elif choice == '2':
            stat_by_candidate(df)
        elif choice == '3':
            stat_by_model(df)
        elif choice == '4':
            explore_errors(df)
        elif choice == '5':
            print("Au revoir !")
            sys.exit()
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nInterruption détectée. Au revoir !")
        sys.exit()
