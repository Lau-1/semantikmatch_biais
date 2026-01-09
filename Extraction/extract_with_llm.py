from abc import ABC, abstractmethod
import json
import os
import time
import re
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

RUN_NUMBER = sys.argv[1] if len(sys.argv) > 1 else None

# 1. Import spécifique pour Azure
from openai import AzureOpenAI

load_dotenv()

# 2. Configuration du client Azure
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_AI_ENDPOINT"),
    api_key=os.getenv("AZURE_AI_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION", "2024-05-01-preview")
)

AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")

CITATION_PATTERN = re.compile(r"【.*?】")

class ExtractWithLLM(ABC):

    def __init__(self, output_filename, input_folder):
        #run_dir = self.get_next_run_dir(output_filename)
        if RUN_NUMBER is None:
            raise ValueError("RUN_NUMBER manquant (doit être fourni par le launcher)")
        
        run_dir = os.path.join("Extraction", "data", f"run_{RUN_NUMBER}")
        os.makedirs(run_dir, exist_ok=True)

        self.input_folder = input_folder

        # Déduction automatique du préfixe à partir du dossier
        folder_name = os.path.basename(input_folder).lower()

        if "age" in folder_name:
            prefix = "age"
        elif "original" in folder_name:
            prefix = "original"
        elif "origin" in folder_name:
            prefix = "origin"
        elif "genre" in folder_name:
            prefix = "genre"
        else:
            prefix = "original"

        final_filename = f"{prefix}_{output_filename}"
        self.output_dir = os.path.join(run_dir, final_filename)

    @abstractmethod
    def prompt(self):
        pass

    def get_next_run_dir(self, output_dir, base_dir="Extraction/data"):
        os.makedirs(base_dir, exist_ok=True)
        run_number = 1
        while True:
            run_dir = os.path.join(base_dir, f"run_{run_number}")
            full_output_path = os.path.join(run_dir, output_dir)
            if os.path.exists(full_output_path):
                run_number += 1
                continue
            os.makedirs(os.path.dirname(full_output_path), exist_ok=True)
            return run_dir

    def clean_json_string(self, text_value):
        clean_text = CITATION_PATTERN.sub("", text_value)
        clean_text = clean_text.replace("```json", "").replace("```", "").strip()
        return clean_text

    def wait_for_run(self, run, thread_id):
        while run.status in ['queued', 'in_progress', 'cancelling']:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
        return run

    def process_single_cv(self, assistant_id, folder_path, filename):
        file_path = os.path.join(folder_path, filename)
        openai_file_id = None

        try:
            file_obj = client.files.create(
                file=open(file_path, "rb"),
                purpose="assistants"
            )
            openai_file_id = file_obj.id

            user_prompt = self.prompt()

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

            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant_id,
                response_format={"type": "json_object"}
            )

            run = self.wait_for_run(run, thread.id)

            result_data = {}

            if run is None:
                result_data = {"error": "Timeout"}

            elif run.status == 'completed':
                messages = client.beta.threads.messages.list(thread_id=thread.id)
                response_text = messages.data[0].content[0].text.value

                cleaned_text = self.clean_json_string(response_text)
                try:
                    result_data = json.loads(cleaned_text)
                except json.JSONDecodeError:
                    result_data = {"error": "JSON Parse Error", "raw_text": cleaned_text}
            else:
                error_message = "Unknown Error"
                if hasattr(run, 'last_error') and run.last_error:
                    error_message = run.last_error
                result_data = {"error": f"Status: {run.status}", "details": error_message}

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

    def extract_parallel(self):
        final_results = {}
        folder_path = self.input_folder  # <-- on prend le dossier déjà stocké
        files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]

        if not AZURE_DEPLOYMENT_NAME:
            raise ValueError("Erreur: AZURE_DEPLOYMENT_NAME n'est pas défini dans le .env")

        print(f"Création de l'assistant Azure avec le déploiement : {AZURE_DEPLOYMENT_NAME}")

        # 3. Création de l'assistant
        assistant = client.beta.assistants.create(
            name="CV Extractor Fast Azure",
            instructions="You are a data extraction bot. You answer STRICTLY in JSON without citations.",
            model=AZURE_DEPLOYMENT_NAME,
            tools=[{"type": "file_search"}]
        )

        print(f"Début de l'extraction sur {len(files)} fichiers...")

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_file = {
                executor.submit(self.process_single_cv, assistant.id, folder_path, filename): filename
                for filename in files
            }

            for future in as_completed(future_to_file):
                filename, data = future.result()
                final_results[filename] = data
                print(f"Traité : {filename}")

        client.beta.assistants.delete(assistant.id)

        with open(self.output_dir, "w", encoding="utf-8") as f:
            json.dump(final_results, f, indent=4, ensure_ascii=False)

        print("Terminé.")
