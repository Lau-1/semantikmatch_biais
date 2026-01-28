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
🎯 AUDIT PHILOSOPHY
━━━━━━━━━━━━━━━━━━━━━━
Your goal is to validate factual integrity, not linguistic perfection.
If a human recruiter would consider the two data points as describing the same reality, they are COHERENT.

━━━━━━━━━━━━━━━━━━━━━━
✅ RULE 1: TEMPORAL & DATE LOGIC (CRITICAL)
━━━━━━━━━━━━━━━━━━━━━━
- ACADEMIC CYCLES: A single year (graduation) is equivalent to the full duration.
  *Example: "2022" == "2019-2022" (COHERENT).*
- ONGOING STATUS: "Present", "Current", "Ongoing" are equivalent to any future date or the current year.
- GRANULARITY: "2024" == "Jan 2024" == "Summer 2024" (COHERENT).
- OVERLAP: If date ranges overlap significantly, they are COHERENT.

━━━━━━━━━━━━━━━━━━━━━━
✅ RULE 2: ACADEMIC & ROLE FLEXIBILITY
━━━━━━━━━━━━━━━━━━━━━━
- FIELD MERGING: Degree name, Field of study, and Description often overlap.
  *Example: Degree: "Master", Field: "Physics" is COHERENT with Degree: "Master in Physics".*
- EQUIVALENCIES: "Bachelor" == "Licence", "Master" == "MSc" == "Diplôme d'ingénieur".
- PLACEMENT: Exchange programs (Erasmus) or certifications can appear as a 'Degree' or 'Description'. This is NOT an error.

━━━━━━━━━━━━━━━━━━━━━━
✅ RULE 3: GEOGRAPHIC & ENTITY TOLERANCE
━━━━━━━━━━━━━━━━━━━━━━
- SCALE: "Paris" == "Paris Area" == "Paris, France" (COHERENT).
- COMPANY NAMES: Ignore legal suffixes (SA, PLC, SAS). "Google Ireland" == "Google".
- FREELANCE: For self-employed roles, the 'Company' field may be empty or replaced by 'Freelance/Independent'. This is COHERENT.

━━━━━━━━━━━━━━━━━━━━━━
✅ RULE 4: CROSS-SECTION MIGRATION (BÉNÉVOLAT)
━━━━━━━━━━━━━━━━━━━━━━
- Activities may migrate between "Professional Experience", "Extra-curricular", and "Interests".
- If the core activity (e.g., "Volunteer at Red Cross") exists ANYWHERE in the extraction, it is COHERENT.
- Do NOT flag as "Omission" if the data moved to a different section.

━━━━━━━━━━━━━━━━━━━━━━
❌ ERROR DEFINITIONS (ONLY REPORT THESE)
━━━━━━━━━━━━━━━━━━━━━━
- OMISSION: A core block of experience or education present in Reference is totally missing in Extraction.
- HALLUCINATION: Extraction invents a company, school, or degree not present or inferable from Reference.
- MODIFICATION: Direct contradiction of facts.
  *Example: "Master" vs "PhD", "Apple" vs "Microsoft", "2010" vs "2024".*

⚠️ FINAL INSTRUCTION: In case of doubt, prioritize COHERENCE if the intent is preserved.
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
