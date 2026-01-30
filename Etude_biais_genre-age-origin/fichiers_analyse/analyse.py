from abc import ABC, abstractmethod
import json
import os
import sys
from dotenv import load_dotenv
from openai import AzureOpenAI

# Configuration de l'encodage pour Windows
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

# --- Configuration Azure OpenAI ---
load_dotenv()

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_AI_ENDPOINT"),
    api_key=os.getenv("AZURE_AI_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION", "2024-05-01-preview")
)

ANALYSIS_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")

class Analyse(ABC):
    # Noms des fichiers attendus
    REQUIRED_FILES = [
        "interests.json",
        "experiences.json",
        "studies.json"
    ]

    def __init__(self, biais_name):
        """
        biais_name: Le nom de la variante à tester (ex: "Age", "Gender", "Origin")
        """
        self.biais_name = biais_name

    def process_runs(self, input_root="Runs_jointure", output_root="Runs_analyse", target_runs=None):
        """
        Scanne le dossier input_root et lance l'analyse.

        Args:
            input_root (str): Dossier source.
            output_root (str): Dossier de destination.
            target_runs (list or str): Liste des dossiers à traiter (ex: ["run1", "run3"])
                                       ou une seule chaine (ex: "run1").
                                       Si None, traite TOUS les dossiers trouvés.
        """
        if not os.path.exists(input_root):
            print(f"❌ Erreur : Le dossier '{input_root}' n'existe pas.")
            return

        # 1. Récupération de tous les dossiers existants
        all_available_runs = [d for d in os.listdir(input_root) if os.path.isdir(os.path.join(input_root, d))]

        # 2. Filtrage selon la demande de l'utilisateur
        runs_to_process = []

        if target_runs:
            # Si l'utilisateur a passé une seule string (ex: "run1"), on la met dans une liste
            if isinstance(target_runs, str):
                target_runs = [target_runs]

            # On ne garde que les runs demandées qui existent vraiment sur le disque
            for run in target_runs:
                if run in all_available_runs:
                    runs_to_process.append(run)
                else:
                    print(f"⚠️ Attention : Le dossier demandé '{run}' n'existe pas dans {input_root}.")
        else:
            # Si target_runs est None, on prend tout
            runs_to_process = all_available_runs

        runs_to_process.sort()

        if not runs_to_process:
            print("❌ Aucune run à traiter.")
            return

        print(f"🚀 Démarrage de l'analyse '{self.biais_name}' sur {len(runs_to_process)} runs : {runs_to_process}\n")

        for run_folder in runs_to_process:
            # ... (Le reste de la boucle reste identique à votre code original)
            print(f"🔹 Traitement : {run_folder}")

            run_input_path = os.path.join(input_root, run_folder)
            dossier_rapport = f"Rapport_{self.biais_name.lower()}"
            run_output_path = os.path.join(output_root, run_folder, dossier_rapport)

            fichiers_a_traiter = []
            for filename in self.REQUIRED_FILES:
                f = os.path.join(run_input_path, filename)
                if os.path.isfile(f):
                    fichiers_a_traiter.append(f)
                else:
                    print(f"   ⚠️ Manquant : {filename}")

            if fichiers_a_traiter:
                self.generer_rapports(fichiers_a_traiter, run_output_path)
            else:
                print("   ❌ Aucun fichier valide trouvé pour cette run.")

            print(f"   ✅ Fin de {run_folder}\n")

    def generer_rapports(self, fichiers, output_dir):
        if not ANALYSIS_DEPLOYMENT_NAME:
            raise ValueError("ERREUR: Variable AZURE_ANALYSIS_DEPLOYMENT_NAME manquante.")

        # Création récursive du dossier (ex: Runs_analyse/run1/Rapport_age)
        os.makedirs(output_dir, exist_ok=True)

        for chemin_complet in fichiers:
            nom_fichier_seul = os.path.basename(chemin_complet)
            nom_propre = nom_fichier_seul.replace(".json", "") # ex: interests

            # Nom du fichier de sortie : audit_age_interests.json
            output_filename = f"audit_{self.biais_name.lower()}_{nom_propre}.json"
            output_path = os.path.join(output_dir, output_filename)

            print(f"   📊 Analyse : {nom_fichier_seul} -> {output_path}")

            with open(chemin_complet, "r", encoding="utf-8") as f:
                data = json.load(f)

            rapport_categorie = []

            for cv_id, variants in data.items():
                original_data = variants.get("Original", [])
                biais_data = variants.get(self.biais_name, [])

                prompt = self.construction_prompt(
                    original_data,
                    biais_data,
                    cv_id
                )

                try:
                    response = client.chat.completions.create(
                        model=ANALYSIS_DEPLOYMENT_NAME,
                        messages=[{"role": "user", "content": prompt}],
                        response_format={"type": "json_object"}
                    )
                    resultat = json.loads(response.choices[0].message.content)

                    # Check spécifique : Omission totale
                    if not biais_data and original_data:
                        resultat["empty_extraction"] = True
                        resultat["coherent"] = False
                        resultat["error_type"] = "Omission"
                        resultat["details"] = "Variant list is empty while Original is not."

                    rapport_categorie.append(resultat)

                except Exception as e:
                    print(f"      ❌ Erreur sur {cv_id}: {e}")

            # Sauvegarde
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(rapport_categorie, f, indent=4, ensure_ascii=False)

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
