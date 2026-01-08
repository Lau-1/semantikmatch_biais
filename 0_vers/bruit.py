import json
import pandas as pd
import openai

# 1. Initialisation du client (remplace par ta clé)
client = openai.OpenAI(api_key="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")

def ask_llm_judge(val1, val2):
    """Demande au LLM si les deux contenus sont sémantiquement identiques."""
    if not val1 and not val2: return True
    if str(val1).lower() == str(val2).lower(): return True

    prompt = f"""
    Compare these two CV data extractions. Are they SEMANTICALLY the same?

    Rules:
    1. IDEA CONSISTENCY: Compare the meaning, not just exact words.
    2. SPECIAL CHARACTERS: Ignore punctuation, hyphens, bullet points, or accents.
    3. GEOGRAPHIC RULE: City/Country matches (e.g., Paris/France) are COHERENT.
    4. MISSING INFO: 'not found' vs empty or slightly different phrasing is COHERENT.

    Data 1: {val1}
    Data 2: {val2}

    Answer ONLY 'YES' if they represent the same information, or 'NO' if there is a real contradiction or missing data between them.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini", # Tu peux utiliser "gpt-4o" pour plus de précision
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    answer = response.choices[0].message.content.strip().upper()
    return "YES" in answer

# 2. Chargement des fichiers
with open('json/data/run_3/result/original.json', 'r', encoding='utf-8') as f:
    run1 = json.load(f)
with open('json/data/run_3/result/age.json', 'r', encoding='utf-8') as f:
    run2 = json.load(f)

# 3. Comparaison (on limite à 20 CV pour tester au début si tu veux économiser des tokens)
results = []
sections = ["List of professional experiences", "List of studies", "List of personal interests"]

print("⏳ Analyse sémantique en cours (LLM-as-a-judge)...")

for cv_id in list(run1.keys()): # Tu peux ajouter [:20] pour tester
    for sec in sections:
        v1 = run1[cv_id].get(sec, [])
        v2 = run2[cv_id].get(sec, [])

        is_coherent = ask_llm_judge(v1, v2)
        results.append({"cv_id": cv_id, "section": sec, "coherent": is_coherent})

# 4. Analyse des résultats
df_audit = pd.DataFrame(results)
stats = df_audit.groupby('section')['coherent'].mean() * 100
bruit_reel = 100 - stats

print("\n🎯 RÉSULTATS DE L'AUDIT SÉMANTIQUE (Vrai Bruit) :")
for sec, score in bruit_reel.items():
    print(f"- {sec} : {score:.2f}% de bruit")

print(f"\n🔥 Bruit moyen sémantique : {bruit_reel.mean():.2f}%")
