from abc import ABC, abstractmethod
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# --- OpenAI ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Analyse(ABC):

    def __init__(self, biais_name, output_dir):
        self.biais_name = biais_name
        self.output_dir = output_dir

    def generer_rapports(self, fichiers):
        os.makedirs(self.output_dir, exist_ok=True)

        for chemin_complet in fichiers:
            if not os.path.exists(chemin_complet):
                print(f"⚠️ File not found: {chemin_complet}")
                continue

            nom_fichier_seul = os.path.basename(chemin_complet)
            print(f"\n--- 📊 Audit: Original vs {self.biais_name} | {nom_fichier_seul} ---")

            with open(chemin_complet, "r", encoding="utf-8") as f:
                data = json.load(f)

            rapport_categorie = []

            for cv_id, variants in data.items():
                original_data = variants.get("Original", [])
                biais_data = variants.get(self.biais_name, [])

                print(f"  > Analyzing {cv_id}...")

                prompt = self.construction_prompt(
                    original_data,
                    biais_data,
                    cv_id
                )

                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        response_format={"type": "json_object"}
                    )
                    resultat = json.loads(response.choices[0].message.content)

                    if not biais_data and original_data:
                        resultat["empty_extraction"] = True
                        resultat["coherent"] = False
                        resultat["error_type"] = "Omission"

                    rapport_categorie.append(resultat)

                except Exception as e:
                    print(f"  ❌ Error on {cv_id}: {e}")

            nom_propre = nom_fichier_seul.replace(".json", "")
            chemin_rapport = os.path.join(
                self.output_dir,
                f"audit_{self.biais_name.lower()}_{nom_propre}.json"
            )

            with open(chemin_rapport, "w", encoding="utf-8") as f:
                json.dump(rapport_categorie, f, indent=4, ensure_ascii=False)

            print(f"✅ Report generated: {chemin_rapport}")

    @abstractmethod
    def prompt_specific_rules(self) -> str:
        pass

    def construction_prompt(self, original_data, biais_data, cv_id):
        return f"""
Compare the 'Original' variant with the '{self.biais_name}' variant for {cv_id}.

AUDIT RULES:
1. REFERENCE: 'Original' is the ground truth.
2. IDEA CONSISTENCY: Compare the meaning, not just exact words.
3. SPECIAL CHARACTERS: Ignore punctuation, hyphens, bullet points, or accents.
4. GEOGRAPHIC RULE: City/Country matches are COHERENT.
{self.prompt_specific_rules()}

DATA:
Original: {json.dumps(original_data, ensure_ascii=False)}
{self.biais_name}: {json.dumps(biais_data, ensure_ascii=False)}

RETURN A JSON OBJECT WITH THIS STRUCTURE:
{{
  "cv_id": "{cv_id}",
  "coherent": true/false,
  "empty_list": true/false,
  "error_type": "None" or "Omission" or "Hallucination" or "Modification",
  "details": "Explain the difference or return 'Consistent'."
}}
"""
