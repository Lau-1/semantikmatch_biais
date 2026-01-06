import json
import os
import openai
from dotenv import load_dotenv
import time

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def wait_for_run(run, thread_id):
    """Fonction utilitaire pour attendre que l'IA finisse son travail"""
    while run.status in ['queued', 'in_progress', 'cancelling']:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
    return run

def extract(folder_path):
    final_results = {}
    files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    assistant = client.beta.assistants.create(
        name="CV Extractor",
        instructions="You are a data extraction bot. You answer STRICTLY in JSON.",
        model="gpt-4o",
        tools=[{"type": "file_search"}]
    )
    for filename in files:
        file_path = os.path.join(folder_path, filename)
        openai_file_id = None
        try:
            file_obj = client.files.create(
                file=open(file_path, "rb"),
                purpose="assistants"
            )
            openai_file_id = file_obj.id
            thread = client.beta.threads.create(
                messages=[
                    {
                        "role": "user",
                        "content": "List all personal interests of the candidate as a payload",
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
                assistant_id=assistant.id,
                response_format={"type": "json_object"}
            )

            run = wait_for_run(run, thread.id)

            if run.status == 'completed':
                messages = client.beta.threads.messages.list(thread_id=thread.id)
                response_text = messages.data[0].content[0].text.value
                try:
                    data = json.loads(response_text)
                    final_results[filename] = data
                except json.JSONDecodeError:
                    # Fallback si l'IA a mis du markdown autour
                    clean_text = response_text.replace("```json", "").replace("```", "")
                    final_results[filename] = json.loads(clean_text)
            else:
                print(f"Erreur status : {run.status}")
                final_results[filename] = {"error": run.status}

        except Exception as e:
            print(f"Erreur sur {filename}: {e}")
            final_results[filename] = {"error": str(e)}

        if openai_file_id:
            client.files.delete(openai_file_id)
    client.beta.assistants.delete(assistant.id)

    with open("resultats_finaux.json", "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=4, ensure_ascii=False)

    print("Terminé. Fichier JSON généré.")

if __name__ == "__main__":
    extract("cv/data/CV_Generes/CV_Origin")
