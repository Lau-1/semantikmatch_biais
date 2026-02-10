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
                # Extraction du nom de la section (ex: experiences, interests, studies)
                section = fichier.replace('audit_gender_', '').replace('audit_origin_', '').replace('audit_age_', '').replace('.json', '')
                full_path = os.path.join(chemin_sous_dossier, fichier)

                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            for item in data:
                                item['Biais'] = label_biais
                                item['Section'] = section  # Stocke la section (experiences, etc.)
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
            # Note: Ceci est une simplification, la p-value nécessite une baseline réelle
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

# === NOUVELLE FONCTION AJOUTÉE ===
def afficher_analyse_par_section(df):
    """
    Affiche le nombre d'erreurs groupées par section (studies, experiences, interests).
    """
    print("\n" + "-"*60)
    print(f"  📂 ANALYSE PAR SECTION (Experiences, Studies, Interests...)")
    print("-"*60)

    if 'Section' not in df.columns:
        print("⚠️  Erreur : Colonne 'Section' introuvable dans les données.")
        return

    # On récupère toutes les sections présentes
    sections_uniques = df['Section'].unique()

    header = f" {'Section':<20} | {'Total':<8} | {'Erreurs':<8} | {'Taux (%)':<10}"
    print(header)
    print("-" * len(header))

    for section in sections_uniques:
        subset = df[df['Section'] == section]
        n_total = len(subset)
        n_errors = len(subset[subset['coherent'] == False])
        taux = (n_errors / n_total * 100) if n_total > 0 else 0.0

        # Formattage propre du nom de la section
        nom_section = section.capitalize() if section else "Inconnu"

        print(f" {nom_section:<20} | {n_total:<8} | {n_errors:<8} | {taux:<10.2f}")

    print("-" * len(header))
# =================================

def afficher_types_erreurs(df):
    df_erreurs = df[df['coherent'] == False]
    print("\n" + "-"*60)
    print(f"  📋 DÉTAIL DES TYPES D'ERREURS")
    print("-"*60)

    if df_erreurs.empty:
        print("  ✅ Aucune erreur détectée sur les CVs sélectionnés.")
    else:
        if 'error_type' in df_erreurs.columns:
            # On groupe maintenant aussi par Section pour plus de clarté si nécessaire
            # Mais ici on garde le groupement par Biais -> Error Type
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
# 3. ANALYSE PAR CV & PAR ERREUR
# ==========================================

def inspecter_details_cv(df, cv_id_cible):
    """Affiche les détails des erreurs pour un CV spécifique."""
    print("\n" + "="*60)
    print(f"  🔎 INSPECTION DU CV ID : {cv_id_cible}")
    print("="*60)

    # Filtrer sur le CV et uniquement les erreurs (coherent == False)
    subset = df[(df[CHAMP_ID] == cv_id_cible) & (df['coherent'] == False)]

    if subset.empty:
        print("  ✅ Aucune erreur 'stricte' (coherent=False) trouvée pour ce CV.")
        print("     (Si vous cherchez des modifications mineures, elles sont peut-être marquées 'coherent: true')")
        return

    cols_possibles = ['details', 'reason', 'explanation', 'message', 'error_message']
    col_msg = next((c for c in cols_possibles if c in df.columns), None)

    for _, row in subset.iterrows():
        biais = row.get('Biais', 'Inconnu')
        section = row.get('Section', 'N/A')
        err_type = row.get('error_type', 'Type non spécifié')

        print(f"\n  🔸 Biais : {biais.upper()} | Section : {section}")
        print(f"     Type  : {err_type}")

        if col_msg and pd.notna(row[col_msg]):
            print(f"     📝 Détails : {row[col_msg]}")
        else:
            print("     📝 Détails : (Aucun message disponible)")

    print("-" * 60)

def lister_toutes_les_erreurs(df):
    """
    Affiche la liste séquentielle de toutes les erreurs trouvées.
    """
    df_erreurs = df[df['coherent'] == False]
    nb_err = len(df_erreurs)

    if df_erreurs.empty:
        print("\n✅ Aucune erreur à afficher dans la sélection actuelle.")
        return

    print("\n" + "="*80)
    print(f"  📜 LISTE COMPLÈTE DES ERREURS ({nb_err} trouvées)")
    print("="*80)

    cols_possibles = ['details', 'reason', 'explanation', 'message', 'error_message']
    col_msg = next((c for c in cols_possibles if c in df.columns), None)

    for i, (_, row) in enumerate(df_erreurs.iterrows(), 1):
        cv_id = row.get(CHAMP_ID, "N/A")
        biais = row.get('Biais', 'Inconnu')
        section = row.get('Section', 'N/A')
        err_type = row.get('error_type', 'N/A')

        msg = "Pas de détails"
        if col_msg and pd.notna(row[col_msg]):
            msg = str(row[col_msg]).strip()

        print(f"[{i}/{nb_err}] CV: {cv_id} | {biais} > {section}")
        print(f"    ❌ Type : {err_type}")
        print(f"    📝 Note : {msg}")
        print("-" * 40)


def menu_analyse_par_cv(df):
    """Sous-menu pour afficher les stats par CV."""

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

    top_n = stats_cv.head(15)
    for idx, row in top_n.iterrows():
        print(f"  {idx+1:<5} | {row[CHAMP_ID]:<15} | {row['Nb_Erreurs']:<10}")

    if len(stats_cv) > 15:
        print(f"  ... (et {len(stats_cv) - 15} autres CVs avec des erreurs)")

    while True:
        print("\nOptions d'inspection :")
        print("  • Entrez un ID de CV pour voir ses messages d'erreur.")
        print("  • Tapez 'T' pour voir tout le tableau des scores.")
        print("  • Tapez 'R' pour Retour au menu précédent.")

        choix = input("👉 Votre choix : ").strip()

        if choix.lower() == 'r':
            break

        elif choix.lower() == 't':
            print("\n" + str(stats_cv))

        elif choix:
            clean_input = choix.replace("CV", "").replace("cv", "").strip()
            if clean_input in df[CHAMP_ID].values:
                inspecter_details_cv(df, clean_input)
            elif choix in df[CHAMP_ID].values:
                inspecter_details_cv(df, choix)
            else:
                print(f"❌ ID '{choix}' introuvable dans les données.")

# ==========================================
# 4. GESTION DES EXCLUSIONS & FILTRES
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
        rep = input("👉 Validez-vous cette liste ? (o/n) : ").lower().strip()

        if rep == 'o' or rep == 'y':
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

def demander_exclusion_technique():
    """Demande à l'utilisateur s'il veut filtrer les erreurs 'Original empty'."""
    print("\n" + "?"*60)
    print("  🛠  FILTRE TECHNIQUE")
    print("?"*60)
    print("  Certaines erreurs sont marquées 'Original empty' (champ vide à la source).")
    print("  Cela indique souvent un problème d'extraction plutôt qu'un biais.")
    print("-" * 60)
    rep = input("👉 Souhaitez-vous exclure ces erreurs techniques des stats ? (o/n) : ").lower().strip()
    return rep in ['o', 'y', 'oui', 'yes']

# ==========================================
# 5. MENU INTERNE SYNTHESE
# ==========================================

def menu_interne(df_brut, base_path, run_name, liste_exclusions_validee, filtre_empty_active):
    """
    Menu principal avec la nouvelle option 'Analyse par Section'.
    """
    cvs_a_exclure = liste_exclusions_validee
    filtrer_empty = filtre_empty_active

    while True:
        # === 1. FILTRAGE ID ===
        if CHAMP_ID in df_brut.columns:
            if cvs_a_exclure:
                df_courant = df_brut[~df_brut[CHAMP_ID].isin(cvs_a_exclure)].copy()
            else:
                df_courant = df_brut.copy()
        else:
            print(f"\n❌ ERREUR CRITIQUE : La colonne '{CHAMP_ID}' n'existe pas !")
            df_courant = df_brut.copy()

        nb_apres_id = len(df_courant)

        # === 2. FILTRAGE 'Original empty' ===
        nb_empty_removed = 0
        if filtrer_empty:
            if 'error_type' in df_courant.columns:
                nb_before = len(df_courant)
                df_courant = df_courant[df_courant['error_type'] != "Original empty"]
                nb_empty_removed = nb_before - len(df_courant)

        # === STATS FILTRES ===
        nb_brut = len(df_brut)
        nb_net = len(df_courant)
        nb_exclus_id = nb_brut - nb_apres_id if nb_brut > 0 else 0

        # === AFFICHAGE HEADER MENU ===
        print("\n" + "="*55)
        print(f"      MENU SYNTHÈSE : {run_name.upper()}")
        print("="*55)

        # Info Filtres
        if nb_exclus_id > 0:
            print(f"  🚫  Filtre IDs      : {nb_exclus_id} exclus")
        else:
            print(f"  ✅  Filtre IDs      : Inactif (Tous les CVs inclus)")

        statut_empty = "ACTIVÉ" if filtrer_empty else "DÉSACTIVÉ"
        if filtrer_empty and nb_empty_removed > 0:
            print(f"  🛠  Filtre Empty    : {statut_empty} ({nb_empty_removed} 'Original empty' retirés)")
        else:
            print(f"  🛠  Filtre Empty    : {statut_empty}")

        print(f"  📉  Reste à analyser: {nb_net} comparaisons")
        print("-" * 55)
        print(" 1. Synthèse Globale")
        print(" 2. Analyse par Biais (Genre, Origine, Âge)")
        print(" 3. Analyse par Section (Experiences, Studies, etc.)")  # <--- NOUVELLE OPTION
        print(" 4. Détail des types d'erreurs")
        print(" 5. Inspecter les erreurs par CV (Top classement)")
        print(" 6. Lister TOUTES les erreurs (Flux continu)")
        print(" 7. Rapport complet (1 + 2 + 3 + 4)")
        print("-" * 55)
        print(f" 8. Modifier les exclusions d'IDs")
        print(f" 9. {'Désactiver' if filtrer_empty else 'Activer'} le filtre 'Original empty'")
        print(" Q. Retour au menu principal")
        print("-" * 55)

        choix = input("👉 Votre choix : ").strip().lower()

        if choix == '1':
            afficher_synthese_globale(df_courant)
        elif choix == '2':
            afficher_detail_biais(df_courant)
        elif choix == '3':
            # Appel de la nouvelle fonction
            afficher_analyse_par_section(df_courant)
        elif choix == '4':
            afficher_types_erreurs(df_courant)
        elif choix == '5':
            menu_analyse_par_cv(df_courant)
        elif choix == '6':
            lister_toutes_les_erreurs(df_courant)
        elif choix == '7':
            # Rapport complet mis à jour
            afficher_synthese_globale(df_courant)
            afficher_detail_biais(df_courant)
            afficher_analyse_par_section(df_courant) # Ajouté ici aussi
            afficher_types_erreurs(df_courant)
        elif choix == '8':
            cvs_a_exclure = initialiser_exclusions(base_path, run_name)
        elif choix == '9':
            filtrer_empty = not filtrer_empty
            print(f"✅ Filtre 'Original empty' {'activé' if filtrer_empty else 'désactivé'}.")
        elif choix == 'q':
            break
        else:
            print("\n❌ Choix invalide.")

        # Pause pour lecture, sauf menus interactifs
        if choix not in ['5', '6', '9']:
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

    # 4. Demander si on exclut les erreurs "Original empty"
    exclure_empty = demander_exclusion_technique()

    # 5. Lancer le menu
    menu_interne(df_resultats, base_path, run_name, liste_validee, exclure_empty)
