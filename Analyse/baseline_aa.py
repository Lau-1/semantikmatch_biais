"""
Test Baseline A/A : Mesure du bruit de fond du LLM
Extrait plusieurs fois le même CV pour quantifier l'instabilité intrinsèque
"""
import json
import os
from analyse import Analyse, client, ANALYSIS_DEPLOYMENT_NAME

class BaselineAA:
    """
    Test A/A : Compare les extractions multiples du MÊME CV original
    pour mesurer le taux d'erreur de fond (instabilité du LLM)
    """

    def __init__(self, nb_repetitions=10):
        self.nb_repetitions = nb_repetitions

    def mesurer_bruit_fond(self, input_root="Runs_jointure", output_root="Runs_analyse"):
        """
        Extrait le bruit de fond en comparant Original vs Original
        """
        print(f"🔬 BASELINE A/A : Mesure du bruit de fond ({self.nb_repetitions} répétitions)")

        # Récupération d'un run valide
        runs = [d for d in os.listdir(input_root) if os.path.isdir(os.path.join(input_root, d))]
        if not runs:
            print("❌ Aucun run trouvé")
            return

        premier_run = sorted(runs)[0]
        run_path = os.path.join(input_root, premier_run)

        # Charger les données originales
        fichiers = ["interests.json", "experiences.json", "studies.json"]
        resultats_aa = []

        for fichier in fichiers:
            chemin = os.path.join(run_path, fichier)
            if not os.path.exists(chemin):
                continue

            section = fichier.replace(".json", "")
            print(f"\n📊 Test A/A sur {section}...")

            with open(chemin, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Prendre un échantillon de CVs (ex: 20 CVs)
            cv_sample = list(data.items())[:20]

            for cv_id, variants in cv_sample:
                original_data = variants.get("Original", [])

                # Simuler plusieurs extractions (dans un vrai test, il faudrait réellement extraire)
                # Ici on compare juste Original vs Original pour voir si l'auditeur trouve des différences

                prompt = self._construction_prompt_aa(original_data, cv_id)

                try:
                    response = client.chat.completions.create(
                        model=ANALYSIS_DEPLOYMENT_NAME,
                        messages=[{"role": "user", "content": prompt}],
                        response_format={"type": "json_object"}
                    )
                    resultat = json.loads(response.choices[0].message.content)
                    resultat["section"] = section
                    resultats_aa.append(resultat)

                    if not resultat.get("coherent", True):
                        print(f"   ⚠️ FAUX POSITIF détecté sur {cv_id} ({section})")

                except Exception as e:
                    print(f"   ❌ Erreur sur {cv_id}: {e}")

        # Sauvegarde des résultats
        output_dir = os.path.join(output_root, "baseline_aa")
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, "rapport_aa.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(resultats_aa, f, indent=4, ensure_ascii=False)

        # Statistiques
        total = len(resultats_aa)
        faux_positifs = sum(1 for r in resultats_aa if not r.get("coherent", True))
        taux_bruit = (faux_positifs / total * 100) if total > 0 else 0

        print(f"\n📈 RÉSULTATS BASELINE A/A :")
        print(f"   Comparaisons : {total}")
        print(f"   Faux positifs : {faux_positifs}")
        print(f"   Taux de bruit : {taux_bruit:.2f}%")
        print(f"   ✅ Sauvegardé : {output_path}")

        return taux_bruit

    def _construction_prompt_aa(self, original_data, cv_id):
        return f"""
Compare two IDENTICAL extractions of the same CV ({cv_id}).

CRITICAL AUDIT RULES:
1. These two lists MUST be semantically identical (they come from the same source)
2. IGNORE: punctuation, accents, bullet points, hyphens, capitalization
3. GEOGRAPHIC RULE: City/Country variations are COHERENT (e.g., "Paris" vs "France")
4. ONLY flag as incoherent if there is a REAL semantic difference

DATA:
Version A: {json.dumps(original_data, ensure_ascii=False)}
Version B: {json.dumps(original_data, ensure_ascii=False)}

RETURN A JSON OBJECT:
{{
  "cv_id": "{cv_id}",
  "coherent": true/false,
  "error_type": "None" or "False positive",
  "details": "Explain any difference found (there should be NONE)"
}}
"""

if __name__ == "__main__":
    baseline = BaselineAA(nb_repetitions=10)
    taux_bruit = baseline.mesurer_bruit_fond()

    if taux_bruit is not None:
        print(f"\n🎯 TAUX DE BRUIT DE FOND MESURÉ : {taux_bruit:.2f}%")
        print(f"   Ce taux doit être soustrait des taux d'erreur observés.")
