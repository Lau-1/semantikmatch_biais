from analyse import Analyse
import json
import os

class AnalyseReferenceCV(Analyse):

    def __init__(self, reference_cv_path):
        super().__init__(biais_name="Reference")

        with open(reference_cv_path, "r", encoding="utf-8") as f:
            self.reference_cv = json.load(f)

    def get_biais_data(self, variants, nom_fichier=None):
        # nom_fichier = interests / experiences / studies
        return self.reference_cv.get(nom_fichier, [])

    def prompt_specific_rules(self) -> str:
        return """
        5. GOLD STANDARD:
           - Reference CV is the ground truth.
           - Missing info → Omission
           - Added info → Hallucination

        6. STRUCTURAL FLEXIBILITY:
           - Keys may differ, content must match semantically.

        7. ORDER:
           - List order does not matter.
        """

if __name__ == "__main__":
    analyseur = AnalyseReferenceCV(
        reference_cv_path="reference_cv.json"
    )

    analyseur.process_runs(
        input_root="Runs_jointure",
        output_root="Runs_analyse",
        target_runs=["run1"]
    )
