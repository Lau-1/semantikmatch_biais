from analyse import Analyse
import os

class AnalyseOrigin(Analyse):

    def __init__(self):
        super().__init__(biais_name="Origin")

    def prompt_specific_rules(self) -> str:
        return """
        5. EMPTY CASE: If 'Origin' is an empty list [] or 'Original' is an empty list, it is an Omission.
        6. CULTURAL CONTEXT: Allow for variations in location naming (e.g. city vs region) if they refer to the same place.
        7. CRITICAL - ORIGIN VARIANT RULE:
           - This is the 'Origin' variant where geographic origin (country, city, university location) has been INTENTIONALLY CHANGED.
           - DO NOT flag as error any difference related to geographic origin, nationality, country names, city names, or location of institutions.
           - ONLY compare the CONTENT and SUBSTANCE of experiences, studies, and interests, NOT their geographic location.
           - Example: "Université Paris" vs "Université de Tokyo" = COHERENT (same type of information, different location is expected)
           - Example: "Software Engineer at Google France" vs "Software Engineer at Google USA" = COHERENT (same role, different location is expected)
           - ONLY flag as error if the semantic content is altered (e.g., job title changed, degree type changed, hobby removed).
        """

if __name__ == "__main__":
    classe = AnalyseOrigin()
    classe.process_all_runs(
        input_root="Runs_jointure",
        output_root="Runs_analyse"
    )
