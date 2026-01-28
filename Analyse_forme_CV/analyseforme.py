import json
import re
import os
from analyse import Analyse, client, ANALYSIS_DEPLOYMENT_NAME


class AnalyseExtraction(Analyse):
    def __init__(self):
        super().__init__(biais_name="Extraction")

    def prompt_specific_rules(self) -> str:
        """
        UPDATED RULES: SEMANTIC TOLERANCE, TIME NORMALIZATION & FLEXIBLE ENTITY MODELING
        """

        return """
    CONTEXT:
You are an expert auditor checking data extraction.
Compare 'Extraction' (AI Output) against 'Reference' (Ground Truth).

🏆 SUPREME RULE: SEMANTIC EQUIVALENCE, INCLUSION & NORMALIZATION
Do NOT report errors for differences in wording, formatting, field placement,
granularity, or reasonable normalization of time, roles, or entities.
If the core meaning, intent, and factual content are preserved, the data is COHERENT.

━━━━━━━━━━━━━━━━━━━━━━
✅ RULE 1: GEOGRAPHICAL TOLERANCE
━━━━━━━━━━━━━━━━━━━━━━
- Specific vs general locations are COHERENT
- City vs metro area vs country is COHERENT

━━━━━━━━━━━━━━━━━━━━━━
✅ RULE 2: ACADEMIC DATA MERGING & ROLE FLEXIBILITY
━━━━━━━━━━━━━━━━━━━━━━
- Degree, Field, Program Type may overlap
- "Bachelor" == "Bachelor in Economics" → COHERENT
- Exchange / Erasmus / Visiting Student programs:
  - May appear as Degree OR Field OR Description
  - Misplacement between these fields is COHERENT
- Expanded or reduced academic labels are COHERENT

━━━━━━━━━━━━━━━━━━━━━━
✅ RULE 3: CROSS-FIELD INFORMATION PRESENCE
━━━━━━━━━━━━━━━━━━━━━━
- Missing data in one field is acceptable if present elsewhere
- Company, dates, degree, or institution inferred from another field → COHERENT

━━━━━━━━━━━━━━━━━━━━━━
✅ RULE 4: TEMPORAL NORMALIZATION (VERY IMPORTANT)
━━━━━━━━━━━━━━━━━━━━━━
The following are SEMANTICALLY EQUIVALENT and MUST be treated as COHERENT:

- "2024–Present" == "2024–2026"
- "Present", "Ongoing", "Current" == any future end date

- Year-only vs range-based dates:
  - "2022" == "2021–2022"
  - "2022" == "2022–2023"
  - "2021" == "2020-2021"
  - A single year may represent the end year of an academic cycle

- Academic degrees commonly span multiple years:
  - A degree date expressed as a single year MAY be expanded to a multi-year range
  - Examples:
    - "French Baccalauréat – 2022"
    - "French Baccalauréat – 2021–2022"
    → MUST be considered COHERENT
    - "French Baccalauréat – 2022"
    - "French Baccalauréat – 2021 – 2022"
    → MUST be considered COHERENT

- Year-only vs season-based dates:
  - "2025" == "Summer 2025" == "Spring 2025"
  - "2025–2025" == any single-period date in 2025 
  - '2024 - 2026' == 'Jan 2024 - Jan 2026'

Differences in temporal GRANULARITY are NOT errors.
Do NOT report errors when dates overlap or represent the same academic cycle.


━━━━━━━━━━━━━━━━━━━━━━
✅ RULE 5: FREELANCE & SELF-EMPLOYED ROLES
━━━━━━━━━━━━━━━━━━━━━━
- Company is OPTIONAL
- Client-based descriptions are sufficient
- Absence of Company MUST NOT be considered an error

━━━━━━━━━━━━━━━━━━━━━━
✅ RULE 6: VOLUNTEERING & COMMUNITY ACTIVITIES
━━━━━━━━━━━━━━━━━━━━━━
- Volunteering, community engagement, non-profit involvement, or civic activities
  may appear EITHER in:
  - Professional Experience
  - Personal Interests / Hobbies
  - Extra-curricular Activities

- Presence of the SAME volunteering activity in ANY of these sections
  MUST be considered COHERENT, regardless of placement.

- Reclassification between "Interest" and "Professional / Volunteer Experience"
  is NOT an error as long as:
  - The core activity exists
  - The organization or activity intent is preserved

- Absence from one section is acceptable if present in another.

- Volunteering activities MUST NOT be flagged as missing core records
  solely due to section placement differences.

━━━━━━━━━━━━━━━━━━━━━━
❌ ONLY REPORT THESE AS ERRORS
━━━━━━━━━━━━━━━━━━━━━━
Report an error ONLY if there is:

- TOTAL CONTRADICTION (Bachelor vs Master)
- WRONG ENTITY (Google vs Amazon)
- NON-OVERLAPPING, INCOMPATIBLE DATES
- MISSING CORE RECORD (entire experience or education absent)

━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT (JSON ONLY):
━━━━━━━━━━━━━━━━━━━━━━
{
  "coherent": boolean,
  "error_type": string,
  "comment": string
}

        """


    def nettoyer_nom(self, nom_brut):
        return re.sub(r'\s+\d+$', '', nom_brut).strip()

    def normaliser_nom(self, nom):
        """
        Normalisation robuste :
        - lowercase
        - supprime chiffres et suffixes (_01, -01, 01)
        """
        nom = nom.lower()
        nom = re.sub(r'[_-]?\d+$', '', nom)
        nom = re.sub(r'\s+\d+$', '', nom)
        return nom.strip()

    def comparer_fichiers_directs(self, path_reference, path_output, path_rapport):
        print("--- Démarrage de l'analyse (Mode : Semantic & Inclusion) ---")

        try:
            with open(path_reference, 'r', encoding='utf-8') as f:
                data_ref = json.load(f)

            with open(path_output, 'r', encoding='utf-8') as f:
                data_ai = json.load(f)

        except Exception as e:
            print(f"❌ Erreur chargement fichiers : {e}")
            return

        # Pré-calcul du mapping normalisé -> nom référence
        mapping_refs = {
            self.normaliser_nom(nom_ref): nom_ref
            for nom_ref in data_ref.keys()
        }

        rapport_global = []

        for nom_ai, contenu_ai in data_ai.items():

            nom_ai_norm = self.normaliser_nom(nom_ai)
            nom_ref_match = mapping_refs.get(nom_ai_norm)

            if not nom_ref_match:
                print(f"⚠️  Pas de référence pour '{nom_ai}'")
                continue

            print(f"🔄 Audit de '{nom_ai}'...")

            contenu_ref = data_ref[nom_ref_match]

            prompt = self.construction_prompt(
                original_data=contenu_ref,
                biais_data=contenu_ai,
                cv_id=nom_ai
            )

            try:
                response = client.chat.completions.create(
                    model=ANALYSIS_DEPLOYMENT_NAME,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a strict auditor using semantic inclusion. Output JSON only."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0
                )

                resultat_raw = response.choices[0].message.content.strip()
                resultat_raw = resultat_raw.replace("```json", "").replace("```", "")

                resultat_json = json.loads(resultat_raw)
                resultat_json["cv_id"] = nom_ai
                resultat_json["reference_used"] = nom_ref_match

                rapport_global.append(resultat_json)

            except Exception as e:
                print(f"❌ Erreur technique sur {nom_ai}: {e}")

        with open(path_rapport, 'w', encoding='utf-8') as f:
            json.dump(rapport_global, f, indent=4, ensure_ascii=False)

        print(f"✅ Analyse terminée. Rapport généré : {path_rapport}")


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    analyseur = AnalyseExtraction()
    analyseur.comparer_fichiers_directs(
        os.path.join(BASE_DIR, "Audit_forme/new_real_cv.json"),
        os.path.join(BASE_DIR, "Audit_forme/output.json"),
        os.path.join(BASE_DIR, "Audit_forme/rapport_analyse.json")
    )
