from analyse import Analyse

fichiers_a_traiter = [
    "json/data/run_3/jointure/interests.json",
    "json/data/run_3/jointure/experiences.json",
    "json/data/run_3/jointure/studies.json"
]

class AnalyseGenre(Analyse):

    def __init__(self):
        super().__init__(
            biais_name="Genre",
            output_dir="rapports_Genre"
        )

    def prompt_specific_rules(self) -> str:
        return """ 
        5. EMPTY CASE: If 'Gender' is an empty list [] or 'Original' is an empty list, it is an Omission.
        """
    

if __name__ == "__main__":
    audit = AnalyseGenre()
    audit.generer_rapports(fichiers_a_traiter)
