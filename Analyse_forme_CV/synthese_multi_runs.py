import json
import csv
import re
import os
from collections import defaultdict

# ================= CONFIG =================
BASE_RUNS = "Analyse_forme_CV/Audit_forme/Run"

CSV_PERSONNES = "Analyse_forme_CV/Audit_forme/audit_personnes.csv"
CSV_FORMATS   = "Analyse_forme_CV/Audit_forme/audit_formats.csv"
CSV_RUNS      = "Analyse_forme_CV/Audit_forme/audit_runs.csv"
# ==========================================


# ==========================================
# CHARGEMENT DES RUNS
# ==========================================
def charger_tous_les_runs():
    data_par_run = {}

    if not os.path.exists(BASE_RUNS):
        print(f"❌ Dossier introuvable : {BASE_RUNS}")
        return data_par_run

    runs = sorted(d for d in os.listdir(BASE_RUNS) if d.startswith("Run_"))

    for run in runs:
        chemin = os.path.join(BASE_RUNS, run, "rapport_analyse.json")

        if not os.path.exists(chemin):
            print(f"⚠️ rapport_analyse.json manquant dans {run}")
            continue

        try:
            with open(chemin, "r", encoding="utf-8") as f:
                data_par_run[run] = json.load(f)
        except Exception as e:
            print(f"❌ Erreur lecture {run} : {e}")

    print(f"📦 {len(data_par_run)} runs chargés")
    return data_par_run


def charger_toutes_les_observations():
    runs_data = charger_tous_les_runs()
    data = []
    for run_data in runs_data.values():
        data.extend(run_data)
    return data


# ==========================================
# MODULE 1 : AUDIT PAR PERSONNE
# ==========================================
def analyse_par_personne(data):
    print(f"\n👤 --- AUDIT PAR PERSONNE ---")

    stats = defaultdict(lambda: {"total": 0, "erreurs": 0})
    lignes_csv = []

    for entree in data:
        cv_id = entree.get("cv_id", "Inconnu")
        coherent = entree.get("coherent", True)
        error_type = entree.get("error_type", "N/A")
        details = entree.get("details") or entree.get("detail") or entree.get("comment") or "Aucun détail"

        match = re.match(r"^(.*?)\s+(\d+)$", cv_id)
        personne = match.group(1) if match else cv_id
        variant = match.group(2) if match else "N/A"

        stats[personne]["total"] += 1
        if not coherent:
            stats[personne]["erreurs"] += 1
            lignes_csv.append({
                "Personne": personne,
                "Variant": variant,
                "CV_ID": cv_id,
                "Type_Erreur": error_type,
                "Détails": details
            })

    for personne, s in stats.items():
        taux = 100 * s["erreurs"] / s["total"] if s["total"] else 0
        indicateur = "✅" if taux == 0 else ("⚠️" if taux <= 50 else "🛑")
        print(f"  - {personne:<15} : {s['erreurs']}/{s['total']} ({taux:.1f}%) {indicateur}")

    with open(CSV_PERSONNES, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["Personne", "Variant", "CV_ID", "Type_Erreur", "Détails"]
        )
        writer.writeheader()
        writer.writerows(lignes_csv)

    print(f"📂 Export CSV : {CSV_PERSONNES}")


# ==========================================
# MODULE 2 : AUDIT PAR FORMAT
# ==========================================
def analyse_par_format(data):
    print(f"\n🎨 --- AUDIT PAR FORMAT ---")

    stats = defaultdict(lambda: {"total": 0, "erreurs": 0, "details": []})

    for entree in data:
        cv_id = entree.get("cv_id", "Inconnu")
        coherent = entree.get("coherent", True)
        error_type = entree.get("error_type", "N/A")
        details = entree.get("details") or entree.get("detail") or entree.get("comment") or "Aucun détail"

        match = re.search(r"\s+(\d+)$", cv_id)
        fmt = match.group(1) if match else "Autre"

        stats[fmt]["total"] += 1
        if not coherent:
            stats[fmt]["erreurs"] += 1
            stats[fmt]["details"].append({
                "Format": fmt,
                "CV_ID": cv_id,
                "Type_Erreur": error_type,
                "Détails": details
            })

    print(f"{'Format':<8} | {'Erreurs':<8} | {'Taux':<8}")
    print("-" * 32)

    lignes_csv = []
    for fmt, s in sorted(stats.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999):
        taux = 100 * s["erreurs"] / s["total"] if s["total"] else 0
        indicateur = "OK" if taux == 0 else ("⚠️" if taux <= 50 else "🛑")
        print(f"{fmt:<8} | {s['erreurs']:<8} | {taux:>5.1f}% {indicateur}")
        lignes_csv.extend(s["details"])

    with open(CSV_FORMATS, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["Format", "CV_ID", "Type_Erreur", "Détails"]
        )
        writer.writeheader()
        writer.writerows(lignes_csv)

    print(f"📂 Export CSV : {CSV_FORMATS}")


# ==========================================
# MODULE 3 : AUDIT PAR RUN (NOUVEAU)
# ==========================================
def audit_par_run():
    print(f"\n📦 --- AUDIT PAR RUN ---")

    runs_data = charger_tous_les_runs()
    lignes_csv = []

    print(f"{'Run':<10} | {'Obs':<5} | {'Erreurs':<8} | {'Taux':<8}")
    print("-" * 40)

    for run, data in runs_data.items():
        total = len(data)
        erreurs = sum(1 for d in data if not d.get("coherent", True))
        taux = 100 * erreurs / total if total else 0

        indicateur = "✅" if taux == 0 else ("⚠️" if taux <= 50 else "🛑")

        print(f"{run:<10} | {total:<5} | {erreurs:<8} | {taux:>5.1f}% {indicateur}")

        lignes_csv.append({
            "Run": run,
            "Observations": total,
            "Erreurs": erreurs,
            "Taux_erreur_%": f"{taux:.2f}"
        })

    with open(CSV_RUNS, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["Run", "Observations", "Erreurs", "Taux_erreur_%"]
        )
        writer.writeheader()
        writer.writerows(lignes_csv)

    print(f"📂 Export CSV : {CSV_RUNS}")


# ==========================================
# MENU CLI
# ==========================================
def menu():
    while True:
        print("\n" + "=" * 42)
        print("   DASHBOARD QUALITÉ – EXTRACTION CV")
        print("=" * 42)
        print("1. 👤 Audit par Personne")
        print("2. 🎨 Audit par Format")
        print("3. 📦 Audit par Run")
        print("4. 🚀 Tout générer")
        print("5. 🚪 Quitter")

        choix = input("\nVotre choix (1-5) : ")

        if choix == '1':
            analyse_par_personne(charger_toutes_les_observations())
            input("\n[Entrée] pour continuer...")

        elif choix == '2':
            analyse_par_format(charger_toutes_les_observations())
            input("\n[Entrée] pour continuer...")

        elif choix == '3':
            audit_par_run()
            input("\n[Entrée] pour continuer...")

        elif choix == '4':
            data = charger_toutes_les_observations()
            analyse_par_personne(data)
            analyse_par_format(data)
            audit_par_run()
            print("\n✅ Tous les audits ont été générés.")
            break

        elif choix == '5':
            print("Au revoir 👋")
            break

        else:
            print("❌ Choix invalide.")


# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    menu()
