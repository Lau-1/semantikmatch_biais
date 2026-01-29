import json
import re
import os
from analyse import Analyse, client, ANALYSIS_DEPLOYMENT_NAME


class AnalyseExtraction(Analyse):
    def __init__(self):
        super().__init__(biais_name="Extraction")


    def prompt_specific_rules(self) -> str:
        """
        UPDATED RULES: SEMANTIC TOLERANCE, TIME NORMALIZATION & CROSS-SECTION VALIDATION
        """
        return """
━━━━━━━━━━━━━━━━━━━━━━
🎯 AUDIT PHILOSOPHY (ADDITIONAL CLARIFICATION)
━━━━━━━━━━━━━━━━━━━━━━
The objective is to assess factual consistency, not structural alignment.
If two entries describe the same real-world activity, they MUST be considered coherent,
even if they differ in section placement or level of detail.

━━━━━━━━━━━━━━━━━━━━━━
✅ TEMPORAL NORMALIZATION (ADDITIONAL RULE)
━━━━━━━━━━━━━━━━━━━━━━
Before raising any OMISSION or MODIFICATION related to dates,
the following temporal logic MUST be applied:

- A single year is equivalent to a broader date range that includes it.
  Example:
  "2022" == "2021–2022"

- Overlapping date ranges are considered COHERENT.

- A narrower range contained within a broader range is COHERENT.

Date differences that respect these rules MUST NOT be flagged as errors.

━━━━━━━━━━━━━━━━━━━━━━
✅ VOLUNTEERING – GLOBAL PRESENCE CHECK (ADDITIONAL RULE)
━━━━━━━━━━━━━━━━━━━━━━
For volunteering or tutoring activities:

- Section placement MUST be ignored.

- Before raising an OMISSION, the auditor MUST check whether the activity
  exists ANYWHERE in the Extraction
  (Professional Experience, Extra-curricular, Interests, or any other section).

- If the volunteering activity exists anywhere in the Extraction,
  it MUST be considered PRESENT and NOT an omission.

━━━━━━━━━━━━━━━━━━━━━━
✅ FREELANCE / INDEPENDENT – COMPANY NAME TOLERANCE (ADDITIONAL RULE)
━━━━━━━━━━━━━━━━━━━━━━
When an experience is identified as Freelance, Independent, Self-employed,
or equivalent:

- The company name MAY be missing, generic, or replaced by
  "Freelance", "Independent", "Self-employed", or similar wording.

- Differences or absence of a company name in this specific context
  MUST NOT be considered a Modification or Omission,
  as long as the role, domain, and activity are coherent.

━━━━━━━━━━━━━━━━━━━━━━
🚫 NO TOLERANCE FOR CORE BLOCK OMISSIONS (ADDITIONAL RULE)
━━━━━━━━━━━━━━━━━━━━━━
Except for the volunteering exception explicitly defined above:

- The absence of an Interest, a Work Experience, or a Study
  that exists in the Reference MUST be classified as an OMISSION.

- Reduced level of detail (shorter descriptions, fewer bullet points,
  less granular responsibilities) MUST NOT be treated as an error
  as long as the core activity exists.

- However, COMPLETE absence of a core block
  (Interest, Work Experience, or Study)
  MUST ALWAYS be flagged as an OMISSION.

━━━━━━━━━━━━━━━━━━━━━━
⚠️ ERROR GUARDRAIL (ADDITIONAL CONSTRAINT)
━━━━━━━━━━━━━━━━━━━━━━
An error MUST NOT be raised if the detected difference is explained by:
- Cross-section migration
- Temporal normalization
- Freelance company name tolerance
- Difference in date or description granularity

In case of doubt, prioritize COHERENCE if the intent and factual reality are preserved.

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
        print("--- Démarrage de <l'analyse (Mode : Semantic & Inclusion) ---")

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
