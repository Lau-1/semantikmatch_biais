import json
import os
import re
import openai

# --- CONFIGURATION ---
# Remplace par ta véritable clé API
client = openai.OpenAI(api_key="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")

fichiers_a_traiter = [
    "json/data/run_3/jointure/interests.json",
    "json/data/run_3/jointure/experiences.json",
    "json/data/run_3/jointure/studies.json"
]

def generer_rapports_audit(fichiers):
    dossier_sortie = 'rapports'
    if not os.path.exists(dossier_sortie):
        os.makedirs(dossier_sortie)

    for chemin_complet in fichiers:
        if not os.path.exists(chemin_complet):
            print(f"⚠️ File not found: {chemin_complet}")
            continue
            
        nom_fichier_seul = os.path.basename(chemin_complet)
        print(f"\n--- 📊 Audit: Original vs Gender | {nom_fichier_seul} ---")
        
        with open(chemin_complet, 'r', encoding='utf-8') as f:
            data = json.load(f)

        rapport_categorie = []

        for cv_id, variants in data.items():
            original_data = variants.get('Original', [])
            gender_data = variants.get('Gender', [])

            print(f"  > Analyzing {cv_id}...")
            
            prompt = f"""
            Compare the 'Original' variant with the 'Gender' variant for {cv_id}.
            
            AUDIT RULES:
            1. REFERENCE: 'Original' is the ground truth.
            2. IDEA CONSISTENCY: Compare the meaning, not just exact words.
            3. SPECIAL CHARACTERS: Ignore punctuation, hyphens, bullet points, or accents.
            4. GEOGRAPHIC RULE: City/Country matches (e.g., Paris/France) are COHERENT.
            5. EMPTY CASE: If 'Gender' is an empty list [] or 'Original' is an empty list, it is an Omission.

            DATA:
            Original: {json.dumps(original_data, ensure_ascii=False)}
            Gender: {json.dumps(gender_data, ensure_ascii=False)}
            
            RETURN A JSON OBJECT WITH THIS STRUCTURE:
            {{
                "cv_id": "{cv_id}",
                "coherent": true/false,
                "empty_list": true/false,
                "error_type": "None" or "Omission" or "Hallucination" or "Modification",
                "details": "Explain the difference or return 'Consistent'."
            }}
            """

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={ "type": "json_object" }
                )
                resultat = json.loads(response.choices[0].message.content)
                
                # Double vérification de sécurité pour la clé empty_extraction
                # Si le Gender est vide alors que l'Original ne l'est pas
                if len(gender_data) == 0 and len(original_data) > 0:
                    resultat["empty_extraction"] = True
                    resultat["coherent"] = False
                    resultat["error_type"] = "Omission"
                
                rapport_categorie.append(resultat)
            except Exception as e:
                print(f"  ❌ Error on {cv_id}: {e}")

        nom_propre = nom_fichier_seul.replace('.json', '')
        chemin_rapport = os.path.join(dossier_sortie, f"audit_gender_{nom_propre}.json")
        
        with open(chemin_rapport, 'w', encoding='utf-8') as f:
            json.dump(rapport_categorie, f, indent=4, ensure_ascii=False)
        print(f"✅ Report generated: {chemin_rapport}")

if __name__ == "__main__":
    generer_rapports_audit(fichiers_a_traiter)