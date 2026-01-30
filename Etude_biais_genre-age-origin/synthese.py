import os
import json
import pandas as pd
import sys

# Tenter d'importer scipy pour les tests statistiques
try:
    import scipy.stats as stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# ==========================================
# CONFIGURATION
# ==========================================
CHAMP_ID = "cv_id"
NOM_FICHIER_EXCLUSION = "cv_a_exclure.json"

# ==========================================
# 1. CHARGEMENT DES DONNÉES
# ==========================================

def charger_donnees_run(base_path, run_name):
    """
    Charge les fichiers JSON et crée le DataFrame brut.
    Nettoie les IDs (enlève le préfixe 'CV') pour uniformiser.
    """
    all_data = []
    mapping_biais = {
        "Rapport_gender": "Genre",
        "Rapport_origin": "Origine",
        "Rapport_age": "Âge"
    }

    # Construction du chemin : root/resultats_analyses/run_name
    run_path = os.path.join(base_path, "resultats_analyses", run_name)

    if not os.path.exists(run_path):
        print(f"❌ Erreur : Le dossier '{run_path}' est introuvable.")
        print(f"   Vérifiez que vous avez bien lancé les analyses (Option 3) pour '{run_name}'.")
        return pd.DataFrame()

    print(f"🔄 Chargement des données depuis : {run_path}")
    files_found = 0

    for sous_dossier, label_biais in mapping_biais.items():
        chemin_sous_dossier = os.path.join(run_path, sous_dossier)

        if not os.path.exists(chemin_sous_dossier):
            continue

        for fichier in os.listdir(chemin_sous_dossier):
            if fichier.endswith(".json"):
                section = fichier.replace('audit_gender_', '').replace('audit_origin_', '').replace('audit_age_', '').replace('.json', '')
                full_path = os.path.join(chemin_sous_dossier, fichier)

                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            for item in data:
                                item['Biais'] = label_biais
                                item['Section'] = section
                                item['Fichier'] = fichier

                                # === NETTOYAGE ID ===
                                if CHAMP_ID in item:
                                    raw_id = str(item[CHAMP_ID])
                                    clean_id = raw_id.replace("CV", "").replace("cv", "").strip()
                                    item[CHAMP_ID] = clean_id
                                # ====================

                                all_data.append(item)
                            files_found += 1
                except json.JSONDecodeError:
                    pass

    if files_found == 0:
        print("❌ Aucun fichier JSON valide trouvé dans ce dossier.")
        return pd.DataFrame()

    print(f"✅ Données chargées ({len(all_data)} comparaisons brutes).")
    return pd.DataFrame(all_data)

# ==========================================
# 2. FONCTIONS D'ANALYSE GÉNÉRALE
# ==========================================

def afficher_synthese_globale(df):
    nb_total = len(df)
    if nb_total == 0:
        print("\n⚠️  Attention : Aucune donnée à analyser (tout a été filtré ?).")
        return

    df_erreurs = df[df['coherent'] == False]
    nb_erreurs = len(df_erreurs)
    taux = (nb_erreurs / nb_total * 100) if nb_total > 0 else 0

    print("\n" + "-"*60)
    print(f"  📊 SYNTHÈSE GLOBALE (Calculée sur {nb_total} entrées valides)")
    print("-"*60)
    print(f"  • Total Comparaisons : {nb_total}")
    print(f"  • Total Erreurs      : {nb_erreurs}")
    print(f"  • Taux d'erreur      : {taux:.2f}%")
    print("-" * 60)

def afficher_detail_biais(df):
    print("\n" + "-"*60)
    print(f"  📈 ANALYSE PAR TYPE DE BIAIS")
    print("-"*60)

    types_biais = ['Genre', 'Origine', 'Âge']
    baseline_errors = 0

    header = f" {'Biais':<10} | {'Total':<8} | {'Erreurs':<8} | {'Taux (%)':<10} | {'p-value (Fisher)'}"
    print(header)
    print("-" * len(header))

    for biais in types_biais:
        subset = df[df['Biais'] == biais]
        n_total = len(subset)
        n_errors = len(subset[subset['coherent'] == False])
        taux = (n_errors / n_total * 100) if n_total > 0 else 0.0

        sig_str = "N/A"
        if SCIPY_AVAILABLE and n_total > 0:
            contingency = [[n_errors, n_total - n_errors], [baseline_errors, n_total - baseline_errors]]
            try:
                _, p_value = stats.fisher_exact(contingency)
                if p_value < 0.05:
                    sig_str = f"⚠️ {p_value:.4f}"
                else:
                    sig_str = f"✅ {p_value:.4f}"
            except:
                sig_str = "-"

        print(f" {biais:<10} | {n_total:<8} | {n_errors:<8} | {taux:<10.2f} | {sig_str}")
    print("-" * len(header))

def afficher_types_erreurs(df):
    df_erreurs = df[df['coherent'] == False]
    print("\n" + "-"*60)
    print(f"  📋 DÉTAIL DES TYPES D'ERREURS")
    print("-"*60)

    if df_erreurs.empty:
        print("  ✅ Aucune erreur détectée sur les CVs sélectionnés.")
    else:
        if 'error_type' in df_erreurs.columns:
            stats = df_erreurs.groupby(['Biais', 'error_type']).size().reset_index(name='Compte')
            current_biais = ""
            for _, row in stats.iterrows():
                if row['Biais'] != current_biais:
                    print(f"\n  🔸 {row['Biais'].upper()}")
                    current_biais = row['Biais']
                print(f"     └─ {row['error_type']:<30} : {row['Compte']}")
        else:
            print("  ⚠️ Colonne 'error_type' manquante.")
    print("-" * 60)

# ==========================================
# 3. ANALYSE PAR CV (MODIFIÉ POUR 'DETAILS')
# ==========================================

def inspecter_details_cv(df, cv_id_cible):
    """Affiche les détails des erreurs pour un CV spécifique."""
    print("\n" + "="*60)
    print(f"  🔎 INSPECTION DU CV ID : {cv_id_cible}")
    print("="*60)

    # Filtrer sur le CV et uniquement les erreurs (coherent == False)
    # NOTE: Si vous voulez voir les modifications même marquées "coherent: true",
    # il faudrait retirer la condition '& (df['coherent'] == False)'.
    # Par défaut, on affiche les erreurs strictes.
    subset = df[(df[CHAMP_ID] == cv_id_cible) & (df['coherent'] == False)]

    if subset.empty:
        print("  ✅ Aucune erreur 'stricte' (coherent=False) trouvée pour ce CV.")
        print("     (Si vous cherchez des modifications mineures, elles sont peut-être marquées 'coherent: true')")
        return

    # Liste de colonnes possibles pour le message, "details" en premier
    cols_possibles = ['details', 'reason', 'explanation', 'message', 'error_message']
    col_msg = next((c for c in cols_possibles if c in df.columns), None)

    for _, row in subset.iterrows():
        biais = row.get('Biais', 'Inconnu')
        section = row.get('Section', 'N/A')
        err_type = row.get('error_type', 'Type non spécifié')

        print(f"\n  🔸 Biais : {biais.upper()} | Section : {section}")
        print(f"     Type  : {err_type}")

        if col_msg and pd.notna(row[col_msg]):
            # On affiche le contenu de 'details'
            print(f"     📝 Détails : {row[col_msg]}")
        else:
            print("     📝 Détails : (Aucun message disponible)")

    print("-" * 60)

def menu_analyse_par_cv(df):
    """Sous-menu pour afficher les stats par CV et inspecter les messages."""

    # 1. Calcul du classement des erreurs
    df_erreurs = df[df['coherent'] == False]

    if df_erreurs.empty:
        print("\n✅ Aucune erreur dans le dataset actuel (tout est coherent=True).")
        return

    stats_cv = df_erreurs[CHAMP_ID].value_counts().reset_index()
    stats_cv.columns = [CHAMP_ID, 'Nb_Erreurs']

    print("\n" + "-"*60)
    print(f"  🏆 TOP DES CVs AVEC LE PLUS D'ERREURS")
    print("-" * 60)
    print(f"  {'Rang':<5} | {'ID CV':<15} | {'Nb Erreurs':<10}")
    print("-" * 60)

    # Afficher le top 15
    top_n = stats_cv.head(15)
    for idx, row in top_n.iterrows():
        print(f"  {idx+1:<5} | {row[CHAMP_ID]:<15} | {row['Nb_Erreurs']:<10}")

    if len(stats_cv) > 15:
        print(f"  ... (et {len(stats_cv) - 15} autres CVs avec des erreurs)")

    # 2. Boucle d'inspection
    while True:
        print("\nOptions d'inspection :")
        print("  • Entrez un ID de CV pour voir ses messages d'erreur (champ 'details').")
        print("  • Tapez 'T' pour voir tout le tableau des scores.")
        print("  • Tapez 'R' pour Retour au menu précédent.")

        choix = input("👉 Votre choix : ").strip()

        if choix.lower() == 'r':
            break

        elif choix.lower() == 't':
            print("\n" + str(stats_cv))

        elif choix:
            # Nettoyage rapide de l'ID saisi (au cas où l'utilisateur met "CV123")
            clean_input = choix.replace("CV", "").replace("cv", "").strip()

            # Vérifier si l'ID existe dans le df global (avec ou sans prefixe)
            if clean_input in df[CHAMP_ID].values:
                inspecter_details_cv(df, clean_input)
            elif choix in df[CHAMP_ID].values:
                inspecter_details_cv(df, choix)
            else:
                print(f"❌ ID '{choix}' introuvable dans les données.")

# ==========================================
# 4. GESTION DES EXCLUSIONS
# ==========================================

def charger_liste_exclusion_fichier(base_path, run_name):
    fichier_exclusion = os.path.join(base_path, NOM_FICHIER_EXCLUSION)
    if os.path.exists(fichier_exclusion):
        try:
            with open(fichier_exclusion, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return [str(i).strip() for i in data.get(run_name, [])]
                elif isinstance(data, list):
                    return [str(i).strip() for i in data]
        except Exception:
            return []
    return []

def initialiser_exclusions(base_path, run_name):
    current_exclusions = charger_liste_exclusion_fichier(base_path, run_name)

    while True:
        print("\n" + "!"*60)
        print(f"  🚫 CONTRÔLE DES CVs À EXCLURE ({run_name})")
        print("!"*60)

        if not current_exclusions:
            print("  ℹ️  Aucun CV n'est banni actuellement.")
        else:
            print(f"  ⚠️  {len(current_exclusions)} CVs identifiés comme problématiques :")
            chunked_list = [current_exclusions[i:i + 10] for i in range(0, len(current_exclusions), 10)]
            for chunk in chunked_list:
                print(f"     {chunk}")

        print("-" * 60)
        print("Ces CVs seront RETIRÉS de toutes les statistiques suivantes.")
        rep = input("👉 Validez-vous cette liste ? (o/n) : ").lower().strip()

        if rep == 'o' or rep == 'y':
            print("✅ Liste validée.")
            return current_exclusions

        elif rep == 'n':
            print("\n  ✍️  MODIFICATION")
            print("  1. Ajouter des IDs")
            print("  2. Retirer des IDs")
            print("  3. Tout effacer")
            print("  4. Recharger fichier")

            sub_choix = input("  👉 Votre choix : ").strip()

            if sub_choix == '1':
                ajout = input("     IDs à ajouter (séparés par virgule) : ").strip()
                if ajout:
                    news = [x.strip() for x in ajout.split(',') if x.strip()]
                    current_exclusions = list(set(current_exclusions + news))
            elif sub_choix == '2':
                retrait = input("     IDs à retirer (séparés par virgule) : ").strip()
                if retrait:
                    removes = [x.strip() for x in retrait.split(',') if x.strip()]
                    current_exclusions = [x for x in current_exclusions if x not in removes]
            elif sub_choix == '3':
                current_exclusions = []
            elif sub_choix == '4':
                current_exclusions = charger_liste_exclusion_fichier(base_path, run_name)
        else:
            print("❌ Réponse non comprise.")

# ==========================================
# 5. MENU INTERNE SYNTHESE
# ==========================================

def menu_interne(df_brut, base_path, run_name, liste_exclusions_validee):
    cvs_a_exclure = liste_exclusions_validee

    while True:
        # === FILTRAGE ===
        if cvs_a_exclure:
            if CHAMP_ID in df_brut.columns:
                df_courant = df_brut[~df_brut[CHAMP_ID].isin(cvs_a_exclure)]
            else:
                print(f"\n❌ ERREUR CRITIQUE : La colonne '{CHAMP_ID}' n'existe pas !")
                df_courant = df_brut
        else:
            df_courant = df_brut

        nb_brut = len(df_brut)
        nb_net = len(df_courant)
        nb_exclus = nb_brut - nb_net

        print("\n" + "="*55)
        print(f"      MENU SYNTHÈSE : {run_name.upper()}")
        print("="*55)
        if nb_exclus > 0:
            print(f"  ⚠️  FILTRE ACTIF : {nb_exclus} comparaisons supprimées")
            print(f"  📉  Reste : {nb_net} (sur {nb_brut})")
        else:
            print(f"  ✅  Données complètes : {nb_brut} comparaisons")

        print("-" * 55)
        print(" 1. Synthèse Globale")
        print(" 2. Analyse par Biais")
        print(" 3. Détail des types d'erreurs")
        print(" 4. 🔍 INSPECTER LES ERREURS PAR CV") # Cible la colonne "details"
        print(" 5. Rapport complet (1+2+3)")
        print(f" 6. Modifier les exclusions")
        print(" Q. Retour au menu principal")
        print("-" * 55)

        choix = input("👉 Votre choix : ").strip().lower()

        if choix == '1':
            afficher_synthese_globale(df_courant)
        elif choix == '2':
            afficher_detail_biais(df_courant)
        elif choix == '3':
            afficher_types_erreurs(df_courant)
        elif choix == '4':
            menu_analyse_par_cv(df_courant)
        elif choix == '5':
            afficher_synthese_globale(df_courant)
            afficher_detail_biais(df_courant)
            afficher_types_erreurs(df_courant)
        elif choix == '6':
            cvs_a_exclure = initialiser_exclusions(base_path, run_name)
        elif choix == 'q':
            break
        else:
            print("\n❌ Choix invalide.")

        if choix != '4':
            input("\n[Entrée pour continuer...]")

# ==========================================
# 6. POINT D'ENTRÉE PRINCIPAL
# ==========================================

def run_synthese_interactive(base_path, run_name):
    """
    Fonction appelée par le main.py.
    """
    print(f"\n🚀 Lancement du module de Synthèse...")
    print(f"📂 Dossier ciblé : {run_name}")

    # 1. Charger les données
    df_resultats = charger_donnees_run(base_path, run_name)

    if df_resultats.empty:
        print("⚠️ Pas de données disponibles ou dossier vide.")
        input("[Entrée pour retourner au menu principal...]")
        return

    # 2. Vérification colonne ID
    if CHAMP_ID not in df_resultats.columns:
        print(f"\n⚠️  ATTENTION : La colonne '{CHAMP_ID}' est introuvable dans les données chargées.")
        input("[Entrée pour retourner au menu principal...]")
        return

    # 3. Initialiser les exclusions (Interactif)
    liste_validee = initialiser_exclusions(base_path, run_name)

    # 4. Lancer le menu
    menu_interne(df_resultats, base_path, run_name, liste_validee)
