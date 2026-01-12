from analyse import Analyse
import os

class AnalyseOrigin(Analyse):

    def __init__(self):
        super().__init__(biais_name="Origin")

    def prompt_specific_rules(self) -> str:
        return """
        5. EMPTY CASE: If 'Origin' is an empty list [] or 'Original' is an empty list, it is an Omission.

        6. CRITICAL - ORIGIN VARIANT RULE (GEOGRAPHY):
           - This variant involves INTENTIONAL changes to geographic origins (City, Country, University/Company location).
           - IGNORE any difference related to geography.
           - Example: "Paris" vs "London" = COHERENT.
           - Example: "University of Lyon" vs "University of Tokyo" = COHERENT (same level, different location).

        7. CRITICAL - STRUCTURAL FLEXIBILITY (CROSS-KEY MATCHING):
           - Information may have shifted between keys during extraction. This is NOT an error.
           - RULE: Treat each entry (study or experience) as a "bag of words". If information missing from one key (e.g., 'field') appears in another key (e.g., 'level_of_degree' or 'title') within the same entry, it is COHERENT.
           - Example:
             Original: {"field": "Marketing", "level": "Master"}
             Origin:   {"field": "Master in Marketing", "level": "not found"}
             -> This is COHERENT.

        8. LIST ORDER:
           - The order of items in lists (e.g., interests, list of jobs) does not matter. If all items are present but shuffled, it is COHERENT.
        """


if __name__ == "__main__":
    import os
    # Se placer à la racine du projet
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    print(f"Working directory: {os.getcwd()}")

    classe = AnalyseOrigin()
    classe.process_runs(
        input_root="Runs_jointure",
        output_root="Runs_analyse",
        target_runs = ["run6", "run7"]
    )
