from extract_with_llm import ExtractWithLLM

class ExtractInterestsWithLLM (ExtractWithLLM) :

    def __init__(self, input_folder):
        super().__init__("interests.json", input_folder)

    def prompt(self):
        return "List all personal interests of the candidate as a payload"

if __name__ == "__main__":
    folders = [
        "CV/data/CV_Generes/CV_Original",
        "CV/data/CV_Generes/CV_Origin",
        "CV/data/CV_Generes/CV_Age",
        "CV/data/CV_Generes/CV_Genre"
    ]

    for folder in folders:
        extractor = ExtractInterestsWithLLM(folder)
        extractor.extract_parallel()
