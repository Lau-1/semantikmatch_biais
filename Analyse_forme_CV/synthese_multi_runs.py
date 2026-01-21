import json
import os
import csv
import re
from collections import defaultdict

# ================= CONFIG =================
BASE_RUNS = "Analyse_forme_CV/Audit_forme/runs"

# ⚠️ CSV DE SYNTHÈSE MULTI-RUNS (GLOBAL)
CSV_PERSONNES = "Analyse_forme_CV/Audit_forme/synthese_personnes.csv"
CSV_FORMATS = "Analyse_forme_CV/Audit_forme/synthese_formats.csv"
# ==========================================


def charger_tous_les_runs():
    """
    Charge tous les rapport_analyse.json présents dans runs/run_*/
    Les CSV mono-run restent dans chaque dossier run_X (non touchés)
    """
    data = []
    runs = sorted(d for d in os.listdir(BASE_RUNS) if d.startswith("run_"))

    for run in runs:
        chemin_rapport = os.path.join(BASE_RUNS, run, "rapport_analyse.json")

        if not os.path.exists(chemin_rapport):
            print(f"⚠️ rapport_analyse.json manquant dans {run}")
            continue

        with open(chemin_rapport, "r", encoding="utf-8") as f:
            data.extend(json.load(f))

    print(f"📦 {len(runs)} runs agrégés | {len(data)} observations")
    return data


# ==========================================
# SYNTHÈSE PAR PERSONNE (GLOBAL)
# ==========================================
def synthese_par_personne(data):
    stats = defaultdict(lambda: {"total": 0, "erreurs": 0})

    for entree in data:
        cv_id = entree.get("cv_id", "Inconnu")
        est_coherent = entree.get("coherent", True)

        match = re.match(r"^(.*?)\s+(\d+)$", cv_id)
        personne = match.group(1) if match else cv_id

        stats[personne]["total"] += 1
        if not est_coherent:
            stats[personne]["erreurs"] += 1

    with open(CSV_PERSONNES, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Personne", "Observations", "Erreurs", "Taux_erreur_%"])

        for personne, s in stats.items():
            taux = 100 * s["erreurs"] / s["total"] if s["total"] else 0
            writer.writerow([personne, s["total"], s["erreurs"], f"{taux:.2f}"])

    print(f"📂 Synthèse multi-runs (personnes) : {CSV_PERSONNES}")


# ==========================================
# SYNTHÈSE PAR FORMAT (GLOBAL)
# ==========================================
def synthese_par_format(data):
    stats = defaultdict(lambda: {"total": 0, "erreurs": 0})

    for entree in data:
        cv_id = entree.get("cv_id", "Inconnu")
        est_coherent = entree.get("coherent", True)

        match = re.search(r"\s+(\d+)$", cv_id)
        fmt = match.group(1) if match else "Autre"

        stats[fmt]["total"] += 1
        if not est_coherent:
            stats[fmt]["erreurs"] += 1

    with open(CSV_FORMATS, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Format", "Observations", "Erreurs", "Taux_erreur_%"])

        for fmt, s in sorted(stats.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999):
            taux = 100 * s["erreurs"] / s["total"] if s["total"] else 0
            writer.writerow([fmt, s["total"], s["erreurs"], f"{taux:.2f}"])

    print(f"📂 Synthèse multi-runs (formats) : {CSV_FORMATS}")


# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    data = charger_tous_les_runs()
    synthese_par_personne(data)
    synthese_par_format(data)
    print("\n✅ Synthèse multi-runs terminée.")
