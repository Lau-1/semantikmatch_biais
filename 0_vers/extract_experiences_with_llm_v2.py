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
    """Traite un seul fichier (sera exécuté en parallèle)"""
    file_path = os.path.join(folder_path, filename)
    openai_file_id = None

    try:
        # 1. Upload du fichier
        file_obj = client.files.create(
            file=open(file_path, "rb"),
            purpose="assistants"
        )
        openai_file_id = file_obj.id

        user_prompt = """
From the 'professional experiences' section only, extract all information and return it as a payload.

CRITICAL EXTRACTION RULES (MANDATORY):
1. VERBATIM ONLY: Copy text EXACTLY character-by-character from the source
   - DO NOT simplify job titles (keep "Intern - Warehouse", NOT "Intern")
   - DO NOT abbreviate company names
   - DO NOT summarize descriptions

2. NO INFERENCE: If information is not explicitly written, use "not found"
   - DO NOT guess company name from job title (e.g., "Intern - Customs Broker" → company: "not found")
   - DO NOT infer dates from context
   - DO NOT add details not present in source

3. FIELD SEPARATION: NEVER mix information between fields
   - "company" = Legal entity name ONLY (e.g., "Google", "Accenture")
   - "job title" = Complete position INCLUDING specialization (e.g., "Intern - Warehouse", "Senior Engineer - AI")
   - "description" = Tasks/responsibilities (preserve original bullets/paragraphs)

4. JOB TITLE COMPLETENESS: Keep full title with all components
   - Text: "Intern - Warehouse Operations" → Extract: "Intern - Warehouse Operations" (NOT "Intern")
   - Text: "Data Analyst - Marketing Team" → Extract: "Data Analyst - Marketing Team" (NOT "Data Analyst")

5. QUALITY VALIDATION:
   - Verify job title is complete (includes specialty if present)
   - Verify company is legal entity (not department or project name)
   - If in doubt, be conservative and use "not found"

FORBIDDEN ACTIONS:
❌ Truncating job titles (e.g., "Intern - Warehouse" → "Intern")
❌ Moving company info from job title to company field when not explicitly separated
❌ Inferring company name when only job title is given
❌ Simplifying or summarizing descriptions

FIELD DEFINITIONS:
- "company": Legal entity or organization name ONLY (verbatim from source)
- "job title": Complete position title with specialization (verbatim from source)
- "description": Tasks, achievements, responsibilities (preserve original structure)
- "country or city": Geographic location (verbatim)
- "dates": Temporal range (verbatim format)

EXAMPLES:
✅ CORRECT:
Source: "Software Engineer at Google, Mountain View, 2020-2023"
Output: {
  "company": "Google",
  "job title": "Software Engineer",
  "description": "not found",
  "country or city": "Mountain View",
  "dates": "2020-2023"
}

✅ CORRECT (compound title):
Source: "Intern - Warehouse Operations, Summer 2021"
Output: {
  "company": "not found",
  "job title": "Intern - Warehouse Operations",
  "description": "not found",
  "country or city": "not found",
  "dates": "Summer 2021"
}

❌ WRONG (truncation):
Source: "Intern - Customs Broker, 2022"
Wrong Output: {"job title": "Intern"}
Correct: {"job title": "Intern - Customs Broker"}

❌ WRONG (inference):
Source: "Intern - Customs Broker"
Wrong Output: {"company": "Customs Broker", "job title": "Intern"}
Correct: {"company": "not found", "job title": "Intern - Customs Broker"}

OUTPUT FORMAT:
Return ONLY valid JSON with NO additional text:
{
  "experiences": [
    {
      "company": "verbatim text or 'not found'",
      "job title": "verbatim complete title or 'not found'",
      "description": "verbatim text or 'not found'",
      "country or city": "verbatim location or 'not found'",
      "dates": "verbatim dates or 'not found'"
    }
  ]
}
"""

        # 2. Création du thread avec le fichier
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

        # 3. Lancement du Run
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
            response_format={"type": "json_object"} # Force le JSON
        )

        run = wait_for_run(run, thread.id)

        result_data = {}
        if run.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            response_text = messages.data[0].content[0].text.value

            # Nettoyage et Parsing
            cleaned_text = clean_json_string(response_text)
            try:
                result_data = json.loads(cleaned_text)
            except json.JSONDecodeError as e:
                result_data = {"error": "JSON Parse Error", "raw_text": cleaned_text}
        else:
            result_data = {"error": f"Run failed with status: {run.status}"}

        return filename, result_data

    except Exception as e:
        return filename, {"error": str(e)}

    finally:
        # Nettoyage toujours effectué (suppression du fichier OpenAI)
        if openai_file_id:
            try:
                client.files.delete(openai_file_id)
            except:
                pass

def extract_parallel(folder_path, output_filename="experiences_v2.json"):
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
    # max_workers=5 signifie traiter 5 CVs simultanément
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
