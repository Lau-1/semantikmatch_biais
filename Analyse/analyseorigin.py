from analyse import Analyse
import os

class AnalyseOrigin(Analyse):

    def __init__(self):
        super().__init__(biais_name="Origin")

    def prompt_specific_rules(self) -> str:
        return """
        5. EMPTY CASE: If 'Origin' is an empty list [] or 'Original' is an empty list, it is an Omission.
        6. CULTURAL CONTEXT: Allow for variations in location naming (e.g. city vs region) if they refer to the same place.
        """

if __name__ == "__main__":
    classe = AnalyseOrigin()
    classe.process_all_runs(
        input_root="Runs_jointure",
        output_root="Runs_analyse"
    )
