import json
import os
import re
import sys

# -------------------------
# PATHS
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
RUNS_DIR = os.path.join(PROJECT_ROOT, "resultats_jointure_json")
REFERENCE_CV_PATH = os.path.join(BASE_DIR, "cv_ref_clean.json")

print("BASE_DIR =", BASE_DIR)
print("RUNS_DIR =", RUNS_DIR)

if not os.path.isdir(RUNS_DIR):
    raise FileNotFoundError(f"RUNS_DIR introuvable : {RUNS_DIR}")

sys.path.append(os.path.dirname(BASE_DIR))
from fichiers_analyse.analyseoriginal import AnalyseReferenceCV

SECTIONS = ["experiences", "studies", "interests"]

# -------------------------
# LISTE DES CV À ANALYSER
# -------------------------
CV_IDS_TO_ANALYZE = [
    "CV297",
    "CV295",
    "CV291",
    "CV289",
    "CV288",
    "CV282",
    "CV279",
    "CV272",
    "CV268",
    "CV266",
    "CV262",
    "CV258",
    "CV254",
    "CV253",
    "CV250",
    "CV249",
    "CV246",
    "CV244",
    "CV243",
    "CV238",
    "CV235",
    "CV233",
    "CV231",
    "CV229",
    "CV226",
    "CV223",
    "CV220",
    "CV217",
    "CV215",
    "CV211",
    "CV209",
    "CV204",
    "CV202",
    "CV198",
    "CV195",
    "CV193",
    "CV189",
    "CV185",
    "CV182",
    "CV179",
    "CV176",
    "CV173",
    "CV169",
    "CV166",
    "CV165",
    "CV161",
    "CV158",
    "CV155",
    "CV153",
    "CV150",
    "CV147",
    "CV145",
    "CV142",
    "CV139",
    "CV134",
    "CV131",
    "CV128",
    "CV125",
    "CV121",
    "CV119",
    "CV117",
    "CV114",
    "CV111",
    "CV109",
    "CV106",
    "CV105",
    "CV102",
    "CV99",
    "CV98",
    "CV94",
    "CV91",
    "CV89",
    "CV85",
    "CV81",
    "CV78",
    "CV72",
    "CV68",
    "CV66",
    "CV63",
    "CV59",
    "CV56",
    "CV52",
    "CV50",
    "CV48",
    "CV45",
    "CV44",
    "CV41",
    "CV39",
    "CV37",
    "CV33",
    "CV31",
    "CV28",
    "CV23",
    "CV21",
    "CV19",
    "CV15",
    "CV12",
    "CV9",
    "CV4",
    "CV2"
]



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
# ERREUR PAR RUN
# -------------------------
# -------------------------
# ERREUR PAR RUN (avec sortie globale par run)
# -------------------------
def compute_error_rate_for_run(run_path, analyseur, cv_ids_to_analyze):
    """
    Compare les CV présents dans cv_ids_to_analyze.
    Retourne un dictionnaire complet par CV pour ce run.
    """
    cv_results = {}  # cv_id -> dict avec cohérence, détails, etc.

    for section_file in ["experiences.json", "studies.json", "interests.json"]:
        section_path = os.path.join(run_path, section_file)
        if not os.path.isfile(section_path):
            continue

        extracted_data = load_json(section_path)

        for cv_id, variants in extracted_data.items():
            if cv_id not in cv_ids_to_analyze:
                continue  # ignore CVs non sélectionnés

            # Mapping entre les fichiers JSON de sections et les clés exactes de la référence
            section_mapping = {
                "experiences.json": "List of professional experiences",
                "studies.json": "List of studies",
                "interests.json": "List of personal interests"
            }

            original_data = variants.get("Original", [])
            section_key = section_mapping[section_file]  # ← ici on prend la clé exacte
            reference_data = analyseur.reference_cv.get(cv_id, {}).get(section_key, [])

            prompt = analyseur.construction_prompt(
                original_data=original_data,
                biais_data=reference_data,
                cv_id=cv_id
            )
            try:
                # 🔹 Affichage des données comparées avant l'appel LLM
                #print(f"\n🔹 Analyse du CV {cv_id} – Section {section_key}")
                #print("Original :", json.dumps(original_data, ensure_ascii=False, indent=2))
                #print("Reference :", json.dumps(reference_data, ensure_ascii=False, indent=2))

                # Appel LLM
                resultat = analyseur.analyse_cv_with_llm(
                    prompt,
                    cv_id=cv_id,
                    original_data=original_data,
                    reference_data=reference_data
                )
            except Exception as e:
                print(f"⚠️ Erreur IA pour {cv_id}: {e}")
                resultat = {
                    "cv_id": cv_id,
                    "coherent": False,
                    "empty_list": not bool(original_data),
                    "error_type": "Exception",
                    "details": str(e)
                }

            try:
                resultat = analyseur.analyse_cv_with_llm(prompt)
            except Exception as e:
                print(f"⚠️ Erreur IA pour {cv_id}: {e}")
                resultat = {
                    "cv_id": cv_id,
                    "coherent": False,
                    "empty_list": not bool(original_data),
                    "error_type": "Exception",
                    "details": str(e)
                }

            # Stockage du résultat par CV
            cv_results[cv_id] = resultat

    # Calcul du taux d'erreur global du run
    total = len(cv_results)
    errors = sum(1 for v in cv_results.values() if not v.get("coherent", False))
    summary = {
        "total_cv": total,
        "incorrect_cv": errors,
        "error_rate": round(errors / total, 4) if total else 0.0,
        "details": cv_results  # tous les résultats CV
    }

    return summary


# -------------------------
# MAIN (sauvegarde par run)
# -------------------------
if __name__ == "__main__":
    analyseur = AnalyseReferenceCV(reference_cv_path=REFERENCE_CV_PATH)

    print("📊 BRUIT D'EXTRACTION – TAUX D'ERREUR PAR RUN (via IA)\n")

    results = {}

    for run_name in [f"run{i}" for i in range(1, 7)]:
        run_path = os.path.join(RUNS_DIR, run_name)
        if not os.path.isdir(run_path):
            print(f"⚠️ Dossier manquant : {run_name}")
            continue

        stats = compute_error_rate_for_run(run_path, analyseur, CV_IDS_TO_ANALYZE)
        results[run_name] = stats

        # Sauvegarde par run
        run_output_path = os.path.join(BASE_DIR, f"{run_name}_results.json")
        with open(run_output_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=4, ensure_ascii=False)

        print(
            f"{run_name} → "
            f"{stats['incorrect_cv']}/{stats['total_cv']} CV incorrects "
            f"(taux = {stats['error_rate']*100:.2f}%) - sauvegardé dans {run_output_path}"
        )

    # Sauvegarde globale (optionnelle)
    global_output_path = os.path.join(BASE_DIR, "bruit_extraction_summary.json")
    with open(global_output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Résumé global sauvegardé dans : {global_output_path}")


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    # Initialise l'analyseur avec le CV de référence
    analyseur = AnalyseReferenceCV(reference_cv_path=REFERENCE_CV_PATH)

    print("📊 BRUIT D'EXTRACTION – TAUX D'ERREUR PAR RUN (via IA)\n")

    results = {}

    # Analyse des runs de run1 à run6 uniquement
    for run_name in [f"run{i}" for i in range(1, 7)]:
        run_path = os.path.join(RUNS_DIR, run_name)
        if not os.path.isdir(run_path):
            print(f"⚠️ Dossier manquant : {run_name}")
            continue

        stats = compute_error_rate_for_run(run_path, analyseur, CV_IDS_TO_ANALYZE)
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
