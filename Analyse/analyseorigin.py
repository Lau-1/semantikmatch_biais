from analyse import Analyse

class AnalyseOrigin (Analyse):

    def __init__(self):
        super().__init__(
            biais_name="Origin",
            output_dir="rapports_Origin"
        )

    def prompt_specific_rules(self) -> str:
        return """
        5. EMPTY CASE: If 'Origin' is an empty list [] or 'Original' is an empty list, it is an Omission.
        """


if __name__ == "__main__":
    classe = AnalyseOrigin()
    fichiers_a_traiter = classe.get_fichiers_a_traiter()
    classe.generer_rapports(fichiers_a_traiter)
