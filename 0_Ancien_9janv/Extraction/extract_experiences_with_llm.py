from extract_with_llm import ExtractWithLLM

class ExtractExperiencesWithLLM (ExtractWithLLM) :

    def __init__(self, input_folder):
        super().__init__("experiences.json", input_folder)

    def prompt(self):
        return """
From the 'professional experiences' section only, extract all information and return it as a payload.

EXTRACTION RULES:
- Extract information EXACTLY as written in the source text
- If a field is genuinely absent from this section, use 'not found'
- Do NOT infer, reformulate, or merge information from different parts
- Preserve original formatting of descriptions (bullets, paragraphs, etc.)
- If information could fit multiple fields, prioritize in this order:
  1. Explicit labels in the CV (e.g., "Company: X")
  2. Structural position (company usually appears before job title)
  3. Semantic clues (e.g., "Department" is part of job title, not company)

FIELD DEFINITIONS:
- "company": Legal entity or organization name ONLY (no departments, no locations)
- "job title": Position held, including department/specialization if specified together
- "description": Tasks, achievements, responsibilities (keep original structure)
- "country or city": Geographic location of this specific experience
- "dates": Temporal range in original format (e.g., "2019 - 2022", "Jan 2020 - Present")

QUALITY CHECKS:
- If "not found" appears >2 times in one entry, flag for review
- Ensure no field contains concatenated information from multiple fields

OUTPUT FORMAT:
Return a JSON object strictly following this structure:
{
  "experiences": [
    {
      "company": "company name",
      "job title": "job title",
      "description": "description text",
      "country or city": "location",
      "dates": "dates"
    }
  ]
}
"""


if __name__ == "__main__":
    folders = [
        "CV/data/CV_Generes/CV_Original",
        "CV/data/CV_Generes/CV_Origin",
        "CV/data/CV_Generes/CV_Age",
        "CV/data/CV_Generes/CV_Genre"
    ]

    for folder in folders:
        extractor = ExtractExperiencesWithLLM(folder)
        extractor.extract_parallel()
