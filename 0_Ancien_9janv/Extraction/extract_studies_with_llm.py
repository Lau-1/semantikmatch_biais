from extract_with_llm import ExtractWithLLM

class ExtractStudiesWithLLM (ExtractWithLLM) :

    def __init__(self, input_folder):
        super().__init__("studies.json", input_folder)

    def prompt(self):
        return """
From the 'education' section only, extract all information and return it as a payload.

EXTRACTION RULES:
- Extract information EXACTLY as written in the source text
- If a field is genuinely absent from this section, use 'not found'
- Do NOT infer, reformulate, or merge information from different parts
- Preserve original formatting and terminology
- If information could fit multiple fields, prioritize in this order:
  1. Explicit labels in the CV (e.g., "University: X", "Degree: Y")
  2. Structural position (institution usually appears before degree)
  3. Semantic clues (e.g., "Engineering School" is institution, "Engineering" is field)

FIELD DEFINITIONS:
- "university": Educational establishment name ONLY (university, school, college - no departments, no locations)
- "level_of_degree": Academic level as stated (e.g., "Bachelor", "Master", "MBA", "PhD", "License", "Engineering Degree")
- "field": Domain or specialization of study (e.g., "Computer Science", "Business Administration")
- "country or city": Geographic location of this specific education
- "dates": Temporal range in original format (e.g., "2015 - 2019", "Sept 2018 - June 2020")

QUALITY CHECKS:
- If "not found" appears >2 times in one entry, flag for review
- Ensure no field contains concatenated information from multiple fields
- Preserve exact degree terminology (don't translate "Licence" to "Bachelor" unless explicitly stated)

For each education, return:
{
  "university": "university name",
  "level_of_degree": "degree level",
  "field": "field of study",
  "country or city": "country or city",
  "dates": "dates"
}
"""

if __name__ == "__main__":
    folders = [
        "CV/data/CV_Generes/CV_Original",
        "CV/data/CV_Generes/CV_Origin",
        "CV/data/CV_Generes/CV_Age",
        "CV/data/CV_Generes/CV_Genre",
    ]

    for folder in folders:
        extractor = ExtractStudiesWithLLM(folder)
        extractor.extract_parallel()
