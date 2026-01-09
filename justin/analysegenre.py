from analyse import Analyse
import os

class AnalyseGenre(Analyse):

    def __init__(self):
        super().__init__(biais_name="Gender")

    def prompt_specific_rules(self) -> str:
        return """
        5. EMPTY CASE: If 'Gender' is an empty list [] or 'Original' is an empty list, it is an Omission.
        6. GENDER CONTEXT: Ignore pronoun changes (he/she) if the content remains the same.
        """

if __name__ == "__main__":
    classe = AnalyseGenre()
    classe.process_all_runs(
        input_root="Runs_jointure",
        output_root="Runs_analyse"
    )
