from analyse import Analyse

import os

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
    classe = AnalyseAge()
    fichiers_a_traiter = classe.get_fichiers_a_traiter()
    classe.generer_rapports(fichiers_a_traiter)
