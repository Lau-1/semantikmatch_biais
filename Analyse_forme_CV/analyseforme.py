import json
import re
import os
from analyse import Analyse, client, ANALYSIS_DEPLOYMENT_NAME

class AnalyseExtraction(Analyse):
    def __init__(self):
        super().__init__(biais_name="Extraction")

    def prompt_specific_rules(self) -> str:
        """
        Règles mises à jour : TOLÉRANCE SÉMANTIQUE & FUSION DE CHAMPS.
        """
        return """
        CONTEXT:
        You are an expert auditor checking data extraction.
        Compare 'Extraction' (AI Output) against 'Reference' (Ground Truth).

        🏆 SUPREME RULE: SEMANTIC EQUIVALENCE & INCLUSION
        Do NOT report errors for differences in granularity, phrasing, or formatting.
        If the core information is present, it is CONSISTENT.

        ✅ RULE 1: GEOGRAPHICAL TOLERANCE (Location Handling)
        - "Paris La Défense" == "Paris" == "Paris, France" -> COHERENT.
        - "Lyon" == "Villeurbanne" (Suburbs) -> COHERENT.
        - If the location is specific in one and general in the other, it is COHERENT.

        ✅ RULE 2: DATA MERGING & CONTAINMENT (Degree & Field)
        - If Extraction says "Bachelor in Economics" and Reference says "Bachelor" -> COHERENT (The extraction is just more precise).
        - If Extraction says "Bachelor" and Reference says "Bachelor in Economics" -> COHERENT (The extraction is less precise but correct).
        - If 'Field' is missing but the field name appears inside 'Degree' or 'School' -> COHERENT.

        ✅ RULE 3: CROSS-FIELD PRESENCE
        - If 'Company' is null, but the company name is in 'Title' -> COHERENT.
        - If 'Date' is null, but dates are in 'Description' -> COHERENT.

        ✅ RULE 4: IGNORE MINOR HALLUCINATIONS OR REDUNDANCY
        - "Strategic Strategy" vs "Strategy" -> COHERENT (Redundancy is not a critical error).
        - Minor additions that fit the context of the CV are ACCEPTABLE.

        ❌ ONLY REPORT THESE AS ERRORS:
        - TOTAL CONTRADICTION: "Master" vs "Bachelor" (Different levels).
        - WRONG ENTITY: "Google" vs "Amazon".
        - WRONG DATES: "2015" vs "2022" (Large gap).
        - MISSING CORE INFO: The job/degree is completely absent from the object.

        OUTPUT INSTRUCTIONS:
        - If the meaning is preserved -> "coherent": true.
        - Only set "coherent": false for critical factual errors.
        - Output JSON: {"coherent": boolean, "error_type": string, "comment": string}
        """

    def nettoyer_nom(self, nom_brut):
        # Transforme 'Thomas 01', 'Thomas 13' en 'Thomas'
        return re.sub(r'\s+\d+$', '', nom_brut).strip()

    def comparer_fichiers_directs(self, path_reference, path_output, path_rapport):
        print(f"--- Démarrage de l'analyse (Mode : Semantic & Inclusion) ---")

        try:
            with open(path_reference, 'r', encoding='utf-8') as f:
                data_ref = json.load(f)
            with open(path_output, 'r', encoding='utf-8') as f:
                data_ai = json.load(f)
        except Exception as e:
            print(f"Erreur chargement fichiers : {e}")
            return

        rapport_global = []

        for nom_ai, contenu_ai in data_ai.items():

            # Logique de Matching
            nom_ref_match = None
            if nom_ai in data_ref:
                nom_ref_match = nom_ai
            else:
                nom_nettoye = self.nettoyer_nom(nom_ai)
                if nom_nettoye in data_ref:
                    nom_ref_match = nom_nettoye

            if not nom_ref_match:
                print(f"⚠️  Pas de référence pour '{nom_ai}'")
                continue

            print(f"🔄 Audit de '{nom_ai}'...")

            contenu_ref = data_ref[nom_ref_match]

            # Construction du prompt
            prompt = self.construction_prompt(original_data=contenu_ref, biais_data=contenu_ai, cv_id=nom_ai)

            try:
                response = client.chat.completions.create(
                    model=ANALYSIS_DEPLOYMENT_NAME,
                    messages=[
                        {"role": "system", "content": "You are a smart auditor. Use logic of INCLUSION (e.g. 'Paris La Défense' IS 'Paris'). Output JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0
                )

                resultat_raw = response.choices[0].message.content.strip()
                if resultat_raw.startswith("```"):
                    resultat_raw = resultat_raw.replace("```json", "").replace("```", "")

                resultat_json = json.loads(resultat_raw)

                resultat_json["cv_id"] = nom_ai
                resultat_json["reference_used"] = nom_ref_match

                rapport_global.append(resultat_json)

            except Exception as e:
                print(f"❌ Erreur technique sur {nom_ai}: {e}")

        # Sauvegarde
        with open(path_rapport, 'w', encoding='utf-8') as f:
            json.dump(rapport_global, f, indent=4, ensure_ascii=False)

        print(f"✅ Analyse terminée. Rapport : {path_rapport}")

if __name__ == "__main__":
    analyseur = AnalyseExtraction()
    analyseur.comparer_fichiers_directs("real_cv.json", "output.json", "rapport_analyse.json")
