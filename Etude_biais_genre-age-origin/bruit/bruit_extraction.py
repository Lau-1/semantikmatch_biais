import json
import os
import re
import sys

# Chemin vers le dossier contenant analyseoriginal.py
analyse_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".fichiers_analyse")
sys.path.append(analyse_dir)

# Maintenant Python peut trouver analyseoriginal.py
from analyseoriginal import AnalyseReferenceCV


# -------------------------
# CONFIGURATION
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

RUNS_DIR = os.path.join(PROJECT_ROOT, "resultats_jointure_json")
REFERENCE_CV_PATH = os.path.join(BASE_DIR, "cv_ref.json")

print("BASE_DIR =", BASE_DIR)
print("RUNS_DIR =", RUNS_DIR)

if not os.path.isdir(RUNS_DIR):
    raise FileNotFoundError(f"RUNS_DIR introuvable : {RUNS_DIR}")

SECTIONS = ["experiences", "studies", "interests"]

# -------------------------
# UTILS
# -------------------------
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_cv_number(cv_id):
    """Extrait le numéro d'un CV depuis n'importe quel format (CV297, CV 297, CV 297 Original...)"""
    match = re.search(r"\d+", cv_id)
    return match.group() if match else None

# -------------------------
# LOGIQUE PRINCIPALE AVEC IA
# -------------------------
def compute_error_rate_for_run(run_path, analyseur):
    """
    Compare les CV d'un run avec la référence via AnalyseReferenceCV
    Retourne : total CV, incorrect CV, taux d'erreur
    """
    cv_status = {}  # cv_num -> True/False

    for section_file in ["experiences.json", "studies.json", "interests.json"]:
        section_path = os.path.join(run_path, section_file)
        if not os.path.isfile(section_path):
            continue

        # Charger le fichier de CV extrait
        extracted_data = load_json(section_path)

        for cv_id, variants in extracted_data.items():
            original_data = variants.get("Original", [])
            # Récupérer les données de référence pour ce CV et cette section
            section_key = section_file.replace(".json", "")
            reference_data = analyseur.reference_cv.get(cv_id, {}).get(section_key, [])

            # Construire le prompt pour l'IA
            prompt = analyseur.construction_prompt(
                original_data=original_data,
                biais_data=reference_data,
                cv_id=cv_id
            )

            # Appel à Azure OpenAI via AnalyseReferenceCV
            try:
                response = analyseur.client.chat.completions.create(
                    model=analyseur.ANALYSIS_DEPLOYMENT_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                resultat = json.loads(response.choices[0].message.content)

                cv_num = extract_cv_number(cv_id)
                if cv_num:
                    cv_status[cv_num] = resultat.get("coherent", False)

            except Exception as e:
                print(f"⚠️ Erreur IA pour {cv_id}: {e}")
                cv_num = extract_cv_number(cv_id)
                if cv_num:
                    cv_status[cv_num] = False

    total = len(cv_status)
    errors = sum(1 for v in cv_status.values() if not v)

    return {
        "total_cv": total,
        "incorrect_cv": errors,
        "error_rate": round(errors / total, 4) if total else 0.0
    }

# -------------------------
# POINT D'ENTRÉE
# -------------------------
if __name__ == "__main__":
    # Initialiser l'analyseur IA avec le CV de référence
    analyseur = AnalyseReferenceCV(reference_cv_path=REFERENCE_CV_PATH)

    print("📊 BRUIT D'EXTRACTION – TAUX D'ERREUR PAR RUN (via IA)\n")

    results = {}

    for run_name in sorted(os.listdir(RUNS_DIR)):
        run_path = os.path.join(RUNS_DIR, run_name)
        if not os.path.isdir(run_path):
            continue

        stats = compute_error_rate_for_run(run_path, analyseur)
        results[run_name] = stats

        print(
            f"{run_name} → "
            f"{stats['incorrect_cv']}/{stats['total_cv']} CV incorrects "
            f"(taux = {stats['error_rate']*100:.2f}%)"
        )

    # Sauvegarde globale
    output_path = os.path.join(BASE_DIR, "bruit_extraction_summary.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Résumé sauvegardé dans : {output_path}")
