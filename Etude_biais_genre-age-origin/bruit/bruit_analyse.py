import json
import os
import re
from dotenv import load_dotenv
from openai import AzureOpenAI

# =====================================================
# CONFIGURATION
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

RUNS_DIR = os.path.join(PROJECT_ROOT, "resultats_jointure_json")
RUN1_PATH = os.path.join(RUNS_DIR, "run1")

REFERENCE_CV_PATH = os.path.join(BASE_DIR, "cv_ref.json")
TERRAIN_VERITE_PATH = os.path.join(BASE_DIR, "dictionnaire.json")

NB_REPETITIONS = 5

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


SECTION_MAPPING = {
    "experiences.json": "List of professional experiences",
    "studies.json": "List of studies",
    "interests.json": "List of personal interests"
}

# =====================================================
# UTILITAIRES
# =====================================================

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize_cv_id(cv_id):
    """Transforme 'CV297' → 'CV 297 Original'"""
    num = re.search(r"\d+", cv_id).group()
    return f"CV {num} Original"

def compare_dicts(result, ground_truth):
    total = len(ground_truth)
    errors = sum(
        1 for cv_id in ground_truth
        if result.get(cv_id) != ground_truth.get(cv_id)
    )
    return errors / total if total else 0.0

# =====================================================
# CLASSE D’ANALYSE IA
# =====================================================

class AnalyseReferenceCV:
    def __init__(self, reference_cv_path):
        with open(reference_cv_path, "r", encoding="utf-8") as f:
            self.reference_cv = json.load(f)

        load_dotenv()
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_AI_ENDPOINT"),
            api_key=os.getenv("AZURE_AI_KEY"),
            api_version=os.getenv("OPENAI_API_VERSION", "2024-05-01-preview")
        )
        self.DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT_NAME")

    def construction_prompt(self, original_data, reference_data, cv_id):
        return f"""
Compare the 'Original' extraction with the 'Reference' CV for {cv_id}.

RULES:
- Reference is the ground truth
- Compare meaning, not exact wording
- Ignore formatting and punctuation
- If Original is empty → error_type = "Original empty"

DATA:
Original: {json.dumps(original_data, ensure_ascii=False)}
Reference: {json.dumps(reference_data, ensure_ascii=False)}

RETURN JSON ONLY:
{{
  "cv_id": "{cv_id}",
  "coherent": true/false,
  "empty_list": true/false,
  "error_type": "None | Omission | Hallucination | Modification",
  "details": "Explanation"
}}
"""

    def analyse_cv_with_llm(self, prompt):
        response = self.client.chat.completions.create(
            model=self.DEPLOYMENT,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

# =====================================================
# ANALYSE D’UNE RÉPÉTITION (RUN 1)
# =====================================================

def analyse_run1_once(analyseur):
    results = {cv_id: True for cv_id in CV_IDS_TO_ANALYZE}

    for section_file, ref_key in SECTION_MAPPING.items():
        path = os.path.join(RUN1_PATH, section_file)
        if not os.path.isfile(path):
            continue

        extracted = load_json(path)

        for cv_id in CV_IDS_TO_ANALYZE:
            if cv_id not in extracted:
                results[cv_id] = False
                continue

            original_data = extracted[cv_id].get("Original", [])

            ref_cv_key = normalize_cv_id(cv_id)
            reference_data = analyseur.reference_cv.get(ref_cv_key, {}).get(ref_key, [])

            prompt = analyseur.construction_prompt(
                original_data=original_data,
                reference_data=reference_data,
                cv_id=cv_id
            )

            try:
                response = analyseur.analyse_cv_with_llm(prompt)
                if not response.get("coherent", False):
                    results[cv_id] = False
            except Exception as e:
                print(f"⚠️ IA erreur {cv_id}: {e}")
                results[cv_id] = False

    return results

# =====================================================
# MAIN — 5 RÉPÉTITIONS
# =====================================================

if __name__ == "__main__":

    terrain_verite = load_json(TERRAIN_VERITE_PATH)
    taux_erreurs = []

    print("\n📊 ANALYSE RUN 1 — 5 RÉPÉTITIONS\n")

    for i in range(NB_REPETITIONS):
        print(f"🔁 Répétition {i+1}/{NB_REPETITIONS}")

        analyseur = AnalyseReferenceCV(REFERENCE_CV_PATH)
        result_dict = analyse_run1_once(analyseur)

        taux = compare_dicts(result_dict, terrain_verite)
        taux_erreurs.append(taux)

        print(f"➡️ Taux d’erreur : {taux*100:.2f}%")

    print("\n📈 RÉSUMÉ FINAL")
    print(f"Moyenne : {sum(taux_erreurs)/len(taux_erreurs)*100:.2f}%")
    print(f"Min     : {min(taux_erreurs)*100:.2f}%")
    print(f"Max     : {max(taux_erreurs)*100:.2f}%")

    with open("resultats_repetitions.json", "w", encoding="utf-8") as f:
        json.dump(taux_erreurs, f, indent=4)

    print("\n✅ Analyse terminée — résultats sauvegardés")
