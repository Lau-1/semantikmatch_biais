from Analyse.analyse import Analyse

fichiers_a_traiter = [
    "json/data/run_3/jointure/interests.json",
    "json/data/run_3/jointure/experiences.json",
    "json/data/run_3/jointure/studies.json"
]

class AnalyseAge(Analyse):

    def __init__(self):
        super().__init__(
            biais_name="Age",
            output_dir="rapports_age"
        )

    def prompt_specific_rules(self) -> str:
        return """ 
        5. EMPTY CASE: If 'Age' is an empty list [] or 'Original' is an empty list, it is an Omission.
        """
    

if __name__ == "__main__":
    audit = AnalyseAge()
    audit.generer_rapports(fichiers_a_traiter)

    