from extract_with_llm import ExtractWithLLM

class ExtractInterestsWithLLM (ExtractWithLLM) :

    def __init__(self):
        super().__init__(
            output_dir = "interests.json"
        )

    def prompt(self):
        return """
                        "Extract the candidate's personal interests. "
                        "Output strictly valid JSON format like: {\"interests\": [\"Running\", \"Chess\"]}. "
                        "Do not add any other text." """
 

if __name__ == "__main__":
    ExtractInterestsWithLLM().extract_parallel("cv/data/CV_Generes/CV_Original")
