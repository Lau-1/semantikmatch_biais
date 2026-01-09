from Analyse.analyse import Analyse


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
    classe = AnalyseGenre()
    fichiers_a_traiter = classe.get_fichiers_a_traiter()
    classe.generer_rapports(fichiers_a_traiter)
