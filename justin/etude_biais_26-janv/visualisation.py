import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

# --- Configuration ---
# Remplacez ceci par le chemin de votre fichier si nécessaire
DEFAULT_FILE_PATH = 'rapport_analyse.json'

def analyser_visualiser_json(file_path):
    """
    Charge un fichier JSON de CVs, affiche des statistiques textuelles
    et génère un tableau de bord visuel.
    """

    # 1. Vérification et Chargement
    if not os.path.exists(file_path):
        print(f"❌ Erreur : Le fichier '{file_path}' est introuvable.")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        print(f"✅ Fichier chargé avec succès : {len(df)} entrées trouvées.\n")
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du JSON : {e}")
        return

    # 2. Analyse Textuelle (Console)
    total = len(df)
    coherent_count = df['coherent'].sum()
    error_count = total - coherent_count
    accuracy = (coherent_count / total) * 100

    print("="*40)
    print("      RAPPORT D'ANALYSE RAPIDE")
    print("="*40)
    print(f"📊 Total CVs analysés : {total}")
    print(f"✅ Cohérents           : {coherent_count}")
    print(f"❌ Avec Erreurs        : {error_count}")
    print(f"📈 Taux de succès      : {accuracy:.2f}%")
    print("-" * 40)

    print("\n🔍 Répartition des types d'erreurs :")
    print(df['error_type'].value_counts().to_string())

    print("\n🔍 Taux d'erreur par Candidat (Reference) :")
    # Calcul du taux d'erreur par personne
    error_by_ref = df[df['coherent'] == False].groupby('reference_used').size()
    total_by_ref = df.groupby('reference_used').size()
    error_rate = (error_by_ref / total_by_ref * 100).fillna(0).sort_values(ascending=False)

    for name, rate in error_rate.items():
        print(f"  - {name}: {rate:.1f}% d'erreurs")

    # 3. Visualisation (Graphiques)
    sns.set_theme(style="whitegrid")

    # Création d'une figure avec 3 sous-graphiques (Grid 2x2)
    fig = plt.figure(figsize=(15, 10))
    gs = fig.add_gridspec(2, 2)

    # Définition des couleurs (Vert pour OK, Rouge/Orange pour erreurs)
    custom_palette = {
        "None": "#2ecc71",       # Vert
        "Omission": "#e74c3c",   # Rouge
        "Modification": "#f39c12", # Orange
        "Hallucination": "#9b59b6" # Violet (si présent)
    }

    # --- Graphique 1 : Camembert Global (Haut Gauche) ---
    ax1 = fig.add_subplot(gs[0, 0])
    counts_coherent = df['coherent'].value_counts()
    labels = [f'Cohérent\n({counts_coherent.get(True, 0)})', f'Erreur\n({counts_coherent.get(False, 0)})']
    colors = ['#2ecc71', '#e74c3c'] # Vert et Rouge

    ax1.pie(counts_coherent, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, explode=(0.05, 0))
    ax1.set_title("Cohérence Globale des Extractions")

    # --- Graphique 2 : Types d'erreurs (Haut Droite) ---
    ax2 = fig.add_subplot(gs[0, 1])
    # On filtre pour ne pas afficher "None" qui écrase l'échelle
    errors_only = df[df['error_type'] != 'None']

    if not errors_only.empty:
        sns.countplot(y="error_type", data=errors_only, ax=ax2, palette="magma", order=errors_only['error_type'].value_counts().index)
        ax2.set_title("Distribution des Types d'Erreurs (Excluant 'None')")
        ax2.set_xlabel("Nombre d'occurrences")
        ax2.set_ylabel("")
    else:
        ax2.text(0.5, 0.5, "Aucune erreur détectée !", ha='center', va='center')

    # --- Graphique 3 : Analyse par Candidat (Bas - Large) ---
    ax3 = fig.add_subplot(gs[1, :])

    # Préparation des données pour un bar chart empilé
    # On groupe par Reference et Error Type
    cross_tab = pd.crosstab(df['reference_used'], df['error_type'])

    # On s'assure que les couleurs correspondent à notre palette
    colors_mapped = [custom_palette.get(col, "#333333") for col in cross_tab.columns]

    cross_tab.plot(kind='bar', stacked=True, ax=ax3, color=colors_mapped, width=0.8)

    ax3.set_title("Détail des résultats par Candidat (Dossier)")
    ax3.set_xlabel("Nom du Candidat")
    ax3.set_ylabel("Nombre de CVs")
    ax3.legend(title="Type de Résultat", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=0)

    # Ajustement final
    plt.tight_layout()

    print("\nVisualisation générée... Ouverture de la fenêtre.")
    plt.show()

if __name__ == "__main__":
    # Gestion de l'argument ligne de commande ou valeur par défaut
    target_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILE_PATH

    analyser_visualiser_json(target_file)
