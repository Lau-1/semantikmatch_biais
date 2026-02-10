from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import json

class AnalyseReferenceCV:
    def __init__(self, reference_cv_path):
        with open(reference_cv_path, "r", encoding="utf-8") as f:
            self.reference_cv = json.load(f)

        # --- LLM client ---
        load_dotenv()
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_AI_ENDPOINT"),
            api_key=os.getenv("AZURE_AI_KEY"),
            api_version=os.getenv("OPENAI_API_VERSION", "2024-05-01-preview")
        )
        self.ANALYSIS_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")

    def construction_prompt(self, original_data, biais_data, cv_id):
        """Construit le prompt pour comparer Original ↔ Reference"""
        return f"""
Compare the 'Original' variant with the 'Reference' variant for {cv_id}.

AUDIT RULES:
1. REFERENCE: 'Reference' is the ground truth.
2. IDEA CONSISTENCY: Compare the meaning, not just exact words.
3. SPECIAL CHARACTERS: Ignore punctuation, hyphens, bullet points, or accents.
4. GEOGRAPHIC RULE: City/Country matches are COHERENT.
5. EMPTY REFERENCE CHECK: If the 'Original' data is empty (empty list, null, or empty string), you MUST set 'error_type' to "Original empty" and 'details' to "Original is empty".


DATA:
Original: {json.dumps(original_data, ensure_ascii=False)}
Reference: {json.dumps(biais_data, ensure_ascii=False)}

RETURN A JSON OBJECT WITH THIS STRUCTURE:
{{
  "cv_id": "{cv_id}",
  "coherent": true/false,
  "empty_list": true/false,
  "error_type": "None" or "Omission" or "Hallucination" or "Modification",
  "details": "Explain the difference, return 'Consistent', or 'Reference is empty'."
}}
"""


    def analyse_cv_with_llm(self, prompt, cv_id=None, original_data=None, reference_data=None):
        """Appel au LLM Azure OpenAI avec affichage des données comparées"""
        
        # Affichage pour debug
        #if cv_id is not None:
         #   print(f"\n🔹 Analyse du CV {cv_id}")
            #print("Original :", json.dumps(original_data, ensure_ascii=False, indent=2))
            #print("Reference :", json.dumps(reference_data, ensure_ascii=False, indent=2))
            #print("Prompt envoyé à l'IA :", prompt)
        
        # Appel au LLM
        response = self.client.chat.completions.create(
            model=self.ANALYSIS_DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
