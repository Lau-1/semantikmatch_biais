from analyse import Analyse
import os

class AnalyseAge(Analyse):

    def __init__(self):
        super().__init__(biais_name="Age")

    def prompt_specific_rules(self) -> str:
        return """
        5. EMPTY CASE: If 'Age' is an empty list [] or 'Original' is an empty list, it is an Omission.
        6. AGE CONTEXT: Do not flag explicit mentions of age or dates unless they contradict the timeline.
        """

if __name__ == "__main__":
    analyseur = AnalyseAge()
    analyseur.process_all_runs(
        input_root="Runs_jointure",
        output_root="Runs_analyse"
    )
