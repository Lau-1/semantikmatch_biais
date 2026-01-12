from analyse import Analyse
import os

class AnalyseAge(Analyse):

    def __init__(self):
        super().__init__(biais_name="Age")

    def prompt_specific_rules(self) -> str:
        return """
        5. EMPTY CASE: If 'Age' is an empty list [] or 'Original' is an empty list, it is an Omission.

        6. CRITICAL - AGE VARIANT RULE (DATES & CONTEXT):
           - This variant may involve INTENTIONAL changes to dates, years, or duration to simulate different seniority levels.
           - IGNORE differences in specific years (e.g., "1990-1994" vs "2010-2014") if the content remains consistent.
           - FOCUS on the content (Job titles, Degrees, Descriptions).

        7. CRITICAL - STRUCTURAL FLEXIBILITY (CROSS-KEY MATCHING):
           - Information may have shifted between keys during extraction. This is NOT an error.
           - RULE: Treat each entry (study or experience) as a "bag of words". If information missing from one key (e.g., 'field' or 'dates') appears in another key (e.g., 'level_of_degree', 'title' or 'description') within the same entry, it is COHERENT.
           - Example:
             Original: {"dates": "2010-2012", "title": "Analyst"}
             Age:      {"dates": "not found", "title": "Analyst (2010-2012)"}
             -> This is COHERENT.

        8. LIST ORDER:
           - The order of items in lists does not matter. If all items are present but shuffled, it is COHERENT.
        """

if __name__ == "__main__":
    analyseur = AnalyseAge()
    analyseur.process_runs(
        input_root="Runs_jointure",
        output_root="Runs_analyse",
        target_runs = ["run6", "run7"]
    )
