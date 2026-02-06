import json
import os

# -------------------------
# CONFIGURATION
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUNS_DIR = os.path.join(BASE_DIR, "runs")
REFERENCE_CV_PATH = os.path.join(BASE_DIR, "reference_cv.json")

SECTIONS = ["interests", "experiences", "studies"]

# -------------------------
# UTILS
# -------------------------
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize(item):
    """Simplification légère pour comparaison"""
    return json.dumps(item, ensure_ascii=False, sort_keys=True).lower()

def compare_lists(original, reference):
    """
    Retourne True si les listes sont équivalentes sémantiquement
    (ordre ignoré)
    """
    if not original and not reference:
        return True
    if not original or not reference:
        return False

    original_norm = sorted(normalize(x) for x in original)
    reference_norm = sorted(normalize(x) for x in reference)

    return original_norm == reference_norm

# -------------------------
# MAIN LOGIC
# -------------------------
def compute_error_rate_for_run(run_path, reference_cv):
    extracted_dir = os.path.join(run_path, "extracted_original")

    cv_status = {}  # cv_id -> True/False

    for section in SECTIONS:
        section_path = os.path.join(extracted_dir, f"{section}.json")
        if not os.path.isfile(section_path):
            continue

        extracted_data = load_json(section_path)
        reference_section = reference_cv.get(section, [])

        for cv_id, content in extracted_data.items():
            original_data = content.get("Original", [])

            is_ok = compare_lists(original_data, reference_section)

            if cv_id not in cv_status:
                cv_status[cv_id] = True

            if not is_ok:
                cv_status[cv_id] = False

    total = len(cv_status)
    errors = sum(1 for v in cv_status.values() if not v)
    rate = errors / total if total > 0 else 0.0

    return {
        "total_cv": total,
        "incorrect_cv": errors,
        "error_rate": round(rate, 4)
    }

# -------------------------
# ENTRY POINT
# -------------------------
if __name__ == "__main__":
    reference_cv = load_json(REFERENCE_CV_PATH)

    print("📊 BRUIT D'EXTRACTION – TAUX D'ERREUR PAR RUN\n")

    results = {}

    for run_name in sorted(os.listdir(RUNS_DIR)):
        run_path = os.path.join(RUNS_DIR, run_name)
        if not os.path.isdir(run_path):
            continue

        stats = compute_error_rate_for_run(run_path, reference_cv)
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
