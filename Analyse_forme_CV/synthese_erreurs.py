import json
import csv
import re
import os
import sys
from collections import defaultdict

# --- CONFIGURATION ---
FICHIER_RAPPORT = "Analyse_forme_CV/Audit_forme/rapport_analyse.json"
CSV_GLOBAL = "Analyse_forme_CV/Audit_forme/audit_personnes.csv"
CSV_FORMATS = "Analyse_forme_CV/Audit_forme/audit_formats.csv"

def charger_json(chemin):
    if not os.path.exists(chemin):
        print(f"❌ Erreur : Le fichier '{chemin}' est introuvable. Lancez l'analyse d'abord.")
        return None
    try:
        with open(chemin, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Erreur de lecture JSON : {e}")
        return None

# ==========================================
# MODULE 1 : ANALYSE PAR PERSONNE (GLOBAL)
# ==========================================
def analyse_par_personne(data):
    print(f"\n📊 --- ANALYSE GLOBALE (PAR PERSONNE) ---")

    total_cvs = 0
    total_erreurs = 0
    stats_par_personne = defaultdict(lambda: {"total": 0, "erreurs": 0})
    lignes_csv = []

    for entree in data:
        total_cvs += 1
        cv_id = entree.get("cv_id", "Inconnu")
        est_coherent = entree.get("coherent", False)
        type_erreur = entree.get("error_type", "N/A")

        # --- MODIFICATION ICI : Récupération intelligente du champ détail ---
        # On cherche 'details', 'detail' ou 'comment' pour être sûr d'avoir l'info
        detail_contenu = entree.get("details") or entree.get("detail") or entree.get("comment") or "Aucun détail"

        # Extraction du nom (Thomas 01 -> Thomas)
        match = re.match(r"^(.*?)\s+(\d+)$", cv_id)
        nom_personne = match.group(1) if match else cv_id
        variant = match.group(2) if match else "N/A"

        stats_par_personne[nom_personne]["total"] += 1

        if not est_coherent:
            total_erreurs += 1
            stats_par_personne[nom_personne]["erreurs"] += 1

            lignes_csv.append({
                "Personne": nom_personne,
                "Variant": variant,
                "CV_ID": cv_id,
                "Type Erreur": type_erreur,
                "Détails": detail_contenu  # <--- COLONNE AJOUTÉE
            })

    # Affichage Console
    taux_succes = ((total_cvs - total_erreurs) / total_cvs) * 100 if total_cvs > 0 else 0
    print(f"Total CVs: {total_cvs} | Succès Global: {taux_succes:.1f}%")

    for personne, stats in stats_par_personne.items():
        err = stats["erreurs"]
        tot = stats["total"]
        pct = (err / tot) * 100 if tot > 0 else 0

        indicateur = "✅"
        if pct > 0: indicateur = "⚠️"
        if pct > 50: indicateur = "🛑"

        print(f"  - {personne:<15} : {err} erreurs / {tot} ({pct:.0f}%) {indicateur}")

    # Export CSV
    try:
        colonnes = ["Personne", "Variant", "CV_ID", "Type Erreur", "Détails"]

        with open(CSV_GLOBAL, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=colonnes)
            writer.writeheader()
            writer.writerows(lignes_csv)
        print(f"📂 Rapport exporté : {CSV_GLOBAL}")
    except Exception as e:
        print(f"Erreur export CSV : {e}")

# ==========================================
# MODULE 2 : ANALYSE PAR FORMAT (NUMÉROS)
# ==========================================
def analyse_par_format(data):
    print(f"\n🎨 --- ANALYSE TECHNIQUE (PAR FORMAT/NUMÉRO) ---")

    stats_format = defaultdict(lambda: {"total": 0, "erreurs": 0, "details": []})

    for entree in data:
        cv_id = entree.get("cv_id", "Inconnu")
        est_coherent = entree.get("coherent", True)

        # --- MODIFICATION ICI AUSSI ---
        detail_contenu = entree.get("details") or entree.get("detail") or entree.get("comment") or "Aucun détail"

        match = re.search(r'\s+(\d+)$', cv_id)
        numero_format = match.group(1) if match else "Autre"

        stats_format[numero_format]["total"] += 1

        if not est_coherent:
            stats_format[numero_format]["erreurs"] += 1
            stats_format[numero_format]["details"].append({
                "Format_Numero": numero_format,
                "Candidat": cv_id,
                "Type_Erreur": entree.get("error_type", "N/A"),
                "Détails": detail_contenu  # <--- COLONNE AJOUTÉE
            })

    # Affichage Console
    print(f"{'Format':<8} | {'Échecs':<8} | {'Taux Erreur':<12}")
    print("-" * 35)

    formats_tries = sorted(
        stats_format.items(),
        key=lambda x: (x[1]['erreurs'] / x[1]['total'] if x[1]['total'] > 0 else 0),
        reverse=True
    )

    csv_data = []
    for num, data_fmt in formats_tries:
        tot = data_fmt['total']
        err = data_fmt['erreurs']
        taux = (err / tot) * 100 if tot > 0 else 0
        alert = "🛑" if taux > 50 else ("⚠️" if taux > 0 else "OK")

        print(f"N° {num:<5} | {err}/{tot:<5} | {taux:.1f}% {alert}")

        for det in data_fmt['details']:
            csv_data.append(det)

    # Export CSV
    try:
        colonnes = ["Format_Numero", "Candidat", "Type_Erreur", "Détails"]

        with open(CSV_FORMATS, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=colonnes)
            writer.writeheader()
            writer.writerows(csv_data)
        print(f"📂 Rapport exporté : {CSV_FORMATS}")
    except Exception as e:
        print(f"Erreur export CSV : {e}")

# ==========================================
# MENU PRINCIPAL
# ==========================================
def menu():
    while True:
        print("\n" + "="*40)
        print("   DASHBOARD QUALITÉ EXTRACTION IA")
        print("="*40)
        print("1. 👤 Audit par Personne")
        print("2. 🎨 Audit par Format")
        print("3. 🚀 Tout générer")
        print("4. 🚪 Quitter")

        choix = input("\nVotre choix (1-4) : ")

        data = charger_json(FICHIER_RAPPORT)
        if not data:
            if choix != '4': continue
            else: break

        if choix == '1':
            analyse_par_personne(data)
            input("\n[Entrée] pour continuer...")
        elif choix == '2':
            analyse_par_format(data)
            input("\n[Entrée] pour continuer...")
        elif choix == '3':
            analyse_par_personne(data)
            analyse_par_format(data)
            print("\n✅ Tous les rapports ont été générés.")
            break
        elif choix == '4':
            print("Au revoir !")
            break
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    menu()
