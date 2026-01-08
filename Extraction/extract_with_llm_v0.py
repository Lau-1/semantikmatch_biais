from abc import ABC, abstractmethod
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

class ExtractWithLLM(ABC):

    def __init__(self, output_dir):
        run_dir = self.get_next_run_dir(output_dir)
        self.output_dir = os.path.join(run_dir, output_dir)


    @abstractmethod
    def prompt(self):
        pass

    def get_next_run_dir(self, output_dir, base_dir="Extraction\data"):
    # Numérote automatiquement la run
        os.makedirs(base_dir, exist_ok=True)

        run_number = 1

        while True:
            run_dir = os.path.join(base_dir, f"run_{run_number}")
            full_output_path = os.path.join(run_dir, output_dir)

            if os.path.exists(full_output_path):
                run_number += 1
                continue

            # Création des dossiers nécessaires
            os.makedirs(os.path.dirname(full_output_path), exist_ok=True)
            return run_dir

    def clean_json_string(self, text_value):
        """Nettoie le texte pour ne garder que le JSON valide"""
        # 1. Enlever les citations
        clean_text = CITATION_PATTERN.sub("", text_value)

        # 2. Enlever les balises markdown ```json ... ```
        clean_text = clean_text.replace("```json", "").replace("```", "").strip()

        return clean_text

    def wait_for_run(self, run, thread_id):
        while run.status in ['queued', 'in_progress', 'cancelling']:
            time.sleep(0.5) # Réduit à 0.5s pour être plus réactif
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
        return run

    def process_single_cv(self, assistant_id, folder_path, filename):
        file_path = os.path.join(folder_path, filename)
        openai_file_id = None

        try:
            # 1. Upload du fichier
            file_obj = client.files.create(
                file=open(file_path, "rb"),
                purpose="assistants"
            )
            openai_file_id = file_obj.id

            user_prompt = self.prompt()
            # 2. Création du thread
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

            # 4. Attente avec Timeout (3 min)
            run = self.wait_for_run(run, thread.id)

            result_data = {}

            if run is None:
                result_data = {"error": "Timeout (> 3min)"}

            elif run.status == 'completed':
                messages = client.beta.threads.messages.list(thread_id=thread.id)
                response_text = messages.data[0].content[0].text.value

                cleaned_text = self.clean_json_string(response_text)
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

    def extract_parallel(self, folder_path):
        final_results = {}
        files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]

        # Création de l'assistant UNE SEULE FOIS
        assistant = client.beta.assistants.create(
            name="CV Extractor Fast",
            instructions="You are a data extraction bot. You answer STRICTLY in JSON without citations.",
            model="gpt-4o",
            tools=[{"type": "file_search"}]
        )

        print(f"Début de l'extraction sur {len(files)} fichiers...")

        # Utilisation de ThreadPoolExecutor pour paralléliser
        # max_workers=5 signifie traiter 5 CVs simultanément
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_file = {
                executor.submit(self.process_single_cv, assistant.id, folder_path, filename): filename
                for filename in files
            }

            for future in as_completed(future_to_file):
                filename, data = future.result()
                final_results[filename] = data
                print(f"Traité : {filename}")

        # Suppression de l'assistant à la fin
        client.beta.assistants.delete(assistant.id)

        with open(self.output_dir, "w", encoding="utf-8") as f:
            json.dump(final_results, f, indent=4, ensure_ascii=False)

        print("Terminé.")
