from extract_with_llm import ExtractWithLLM

class ExtractInterestsWithLLM (ExtractWithLLM) :

    def __init__(self, input_folder):
        super().__init__("interests.json", input_folder)

    def prompt(self):
        return """
                        "Extract the candidate's personal interests. "
                        "Output strictly valid JSON format like: {\"interests\": [\"Running\", \"Chess\"]}. "
                        "Do not add any other text." """
 

if __name__ == "__main__":
    ExtractInterestsWithLLM().extract_parallel("CV/data/CV_Generes/CV_Original")
    ExtractInterestsWithLLM().extract_parallel("CV/data/CV_Generes/CV_Origin")
    ExtractInterestsWithLLM().extract_parallel("CV/data/CV_Generes/CV_Age")
    ExtractInterestsWithLLM().extract_parallel("CV/data/CV_Generes/CV_Genre")
