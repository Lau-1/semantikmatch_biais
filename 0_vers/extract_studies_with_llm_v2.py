import json
import os
import openai
import time
import re
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Regex pour nettoyer les citations de l'API Assistants (ex: 【4:0†source】)
CITATION_PATTERN = re.compile(r"【.*?】")

def clean_json_string(text_value):
    """Nettoie le texte pour ne garder que le JSON valide"""
    # 1. Enlever les citations
    clean_text = CITATION_PATTERN.sub("", text_value)

    # 2. Enlever les balises markdown ```json ... ```
    clean_text = clean_text.replace("```json", "").replace("```", "").strip()

    return clean_text

def wait_for_run(run, thread_id):
    while run.status in ['queued', 'in_progress', 'cancelling']:
        time.sleep(0.5) # Réduit à 0.5s pour être plus réactif
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
    return run

def process_single_cv(assistant_id, folder_path, filename):
    file_path = os.path.join(folder_path, filename)
    openai_file_id = None

    try:
        # 1. Upload du fichier
        file_obj = client.files.create(
            file=open(file_path, "rb"),
            purpose="assistants"
        )
        openai_file_id = file_obj.id

        # 2. PROMPT AMÉLIORÉ POUR ÉTUDES (VERSION 2)
        user_prompt = """
From the 'education' section only, extract all information and return it as a payload.

CRITICAL EXTRACTION RULES (MANDATORY):
1. VERBATIM ONLY: Copy text EXACTLY character-by-character from the source
   - DO NOT simplify, abbreviate, or shorten ANY term
   - DO NOT translate between languages (keep "Licence", don't change to "Bachelor")
   - DO NOT merge compound terms (keep "Bachelor of Commerce", NOT "Bachelor")

2. NO INFERENCE: If information is not explicitly written, use "not found"
   - DO NOT guess program types (e.g., don't infer "Summer Program" or "Summer School")
   - DO NOT infer field of study from institution name
   - DO NOT deduce level from context clues

3. FIELD SEPARATION: NEVER mix information between fields
   - "field" contains ONLY domain/specialization (e.g., "Computer Science", "Gestion")
   - "level_of_degree" contains ONLY academic level (e.g., "Bachelor of Commerce", "Master", "Licence")
   - If unsure which field, use "not found" for both rather than mixing

4. ABSENT vs IMPLICIT: Only extract what is EXPLICITLY stated
   - Text says "Bachelor of Commerce" → Extract "Bachelor of Commerce" (NOT "Bachelor")
   - Text says "Summer course in Marketing" → level: "not found", field: "Marketing"
   - Text says "Engineering School" → institution: "Engineering School", field: "not found"

5. QUALITY VALIDATION:
   - After extraction, verify each field contains only ONE type of information
   - If a field seems to contain multiple types, split correctly or use "not found"
   - If in doubt, be conservative and use "not found"

FORBIDDEN ACTIONS (Will cause extraction to fail):
❌ Simplifying degree names (e.g., "Bachelor of Commerce" → "Bachelor")
❌ Adding program types not in source (e.g., "" → "Summer School")
❌ Mixing field and level (e.g., putting "BTS Gestion" in level when "Gestion" is the field)
❌ Translating terminology (e.g., "Licence" → "Bachelor" without explicit equivalence)
❌ Inferring missing information from context

FIELD DEFINITIONS:
- "university": Educational establishment name ONLY (verbatim from source)
- "level_of_degree": Academic level as EXACTLY stated (complete term, no simplification)
- "field": Domain/specialization as EXACTLY stated (no inference from institution name)
- "country or city": Geographic location (verbatim)
- "dates": Temporal range (verbatim format)

EXAMPLES:
✅ CORRECT:
Source: "Bachelor of Commerce in Accounting, McGill University, 2015-2019"
Output: {
  "university": "McGill University",
  "level_of_degree": "Bachelor of Commerce",
  "field": "Accounting",
  "country or city": "not found",
  "dates": "2015-2019"
}

✅ CORRECT (ambiguous case):
Source: "Summer 2020 - Digital Marketing course at HEC Paris"
Output: {
  "university": "HEC Paris",
  "level_of_degree": "not found",
  "field": "Digital Marketing",
  "country or city": "not found",
  "dates": "Summer 2020"
}

❌ WRONG (simplification):
Source: "Bachelor of Commerce, 2018"
Wrong Output: {"level_of_degree": "Bachelor"}
Correct: {"level_of_degree": "Bachelor of Commerce"}

❌ WRONG (inference):
Source: "HEC Paris, 2020"
Wrong Output: {"level_of_degree": "Summer Program"}
Correct: {"level_of_degree": "not found"}

❌ WRONG (field mixing):
Source: "BTS in Business Management"
Wrong Output: {"level_of_degree": "BTS Business Management", "field": "not found"}
Correct: {"level_of_degree": "BTS", "field": "Business Management"}

OUTPUT FORMAT:
Return ONLY valid JSON with NO additional text:
{
  "studies": [
    {
      "university": "verbatim text or 'not found'",
      "level_of_degree": "verbatim complete degree name or 'not found'",
      "field": "verbatim specialization or 'not found'",
      "country or city": "verbatim location or 'not found'",
      "dates": "verbatim dates or 'not found'"
    }
  ]
}
"""

        # 3. Création du thread
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": user_prompt,
                    "attachments": [
                        {
                            "file_id": openai_file_id,
                            "tools": [{"type": "file_search"}]
                        }
                    ]
                }
            ]
        )

        # 4. Lancement du Run
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
            response_format={"type": "json_object"}
        )

        # 5. Attente avec Timeout (3 min)
        run = wait_for_run(run, thread.id)

        result_data = {}

        if run is None:
            result_data = {"error": "Timeout (> 3min)"}

        elif run.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            response_text = messages.data[0].content[0].text.value

            cleaned_text = clean_json_string(response_text)
            try:
                result_data = json.loads(cleaned_text)
            except json.JSONDecodeError:
                result_data = {"error": "JSON Parse Error", "raw_text": cleaned_text}
        else:
            result_data = {"error": f"Status: {run.status}"}

        return filename, result_data

    except Exception as e:
        print(f"❌ Erreur sur {filename}: {e}")
        return filename, {"error": str(e)}

    finally:
        if openai_file_id:
            try:
                client.files.delete(openai_file_id)
            except:
                pass

def extract_parallel(folder_path, output_filename="studies_v2.json"):
    final_results = {}
    files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]

    # Création de l'assistant UNE SEULE FOIS
    assistant = client.beta.assistants.create(
        name="CV Extractor Strict v2",
        instructions="""You are a STRICT data extraction bot. Rules:
1. Extract text VERBATIM (character-by-character copy)
2. NEVER simplify, abbreviate, or infer
3. Use "not found" when information is absent
4. Answer ONLY in valid JSON without citations or markdown""",
        model="gpt-4o",
        tools=[{"type": "file_search"}]
    )

    print(f"🚀 Début de l'extraction STRICTE v2 sur {len(files)} fichiers...")

    # Utilisation de ThreadPoolExecutor pour paralléliser
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_file = {
            executor.submit(process_single_cv, assistant.id, folder_path, filename): filename
            for filename in files
        }

        for future in as_completed(future_to_file):
            filename, data = future.result()
            final_results[filename] = data
            print(f"✅ Traité : {filename}")

    # Suppression de l'assistant à la fin
    client.beta.assistants.delete(assistant.id)

    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=4, ensure_ascii=False)

    print(f"✅ Terminé. Fichier généré : {output_filename}")

if __name__ == "__main__":
    extract_parallel("cv/data/CV_Generes/CV_Original")
