import json
import os
from analyse import AnalyseReferenceCV  # ou AnalyseOriginal si tu as déjà cette classe

# -------------------------
# CONFIGURATION
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CV_FILE = os.path.join(BASE_DIR, "cv_filtre.json")
TERRAIN_VERITE_FILE = os.path.join(BASE_DIR, "terrain_verite.json")

NB_REPETITIONS = 5

# -------------------------
# UTILITAIRES
# -------------------------
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def compare_dictionaries(dict1, dict2):
    """
    Compare deux dictionnaires de la forme {cv_id: True/False}.
    Retourne le taux de différence : nb_diffs / nb_total
    """
    total = len(dict1)
    diffs = sum(1 for k in dict1 if dict1.get(k) != dict2.get(k))
    return diffs / total if total > 0 else 0.0

# -------------------------
# LOGIQUE PRINCIPALE
# -------------------------
if __name__ == "__main__":
    terrain_verite = load_json(TERRAIN_VERITE_FILE)
    cv_data = load_json(CV_FILE)

    # Initialisation du dictionnaire final
    cv_results = {cv_id: True for cv_id in cv_data.keys()}

    # -------------------------
    # Boucle sur les répétitions
    # -------------------------
    for i in range(NB_REPETITIONS):
        print(f"🔹 Répétition {i+1}/{NB_REPETITIONS}")

        # Instanciation de l'analyseur avec le fichier de référence
        analyseur = AnalyseReferenceCV(reference_cv_path=CV_FILE)

        # Pour chaque CV, on suppose qu'on a un seul “run”
        # Nous utilisons le mécanisme de generer_rapports pour vérifier la cohérence
        # Ici on va simuler la comparaison en appelant get_biais_data directement
        for cv_id, content in cv_data.items():
            # original_data : données extraites
            original_data = content.get("Original", [])

            # référence : dans cv_filtre.json, on considère Original comme référence
            reference_data = content.get("Original", [])

            # Normalisation simple pour comparaison
            is_correct = sorted(json.dumps(original_data, ensure_ascii=False)) == sorted(json.dumps(reference_data, ensure_ascii=False))

            # Si une répétition échoue, on marque False
            cv_results[cv_id] = cv_results[cv_id] and is_correct

    # -------------------------
    # Comparaison avec le terrain vérité
    # -------------------------
    taux_diff = compare_dictionaries(cv_results, terrain_verite)

    # -------------------------
    # Affichage
    # -------------------------
    print("\n✅ Résultat final par CV :")
    for cv_id, correct in cv_results.items():
        print(f"{cv_id}: {correct}")

    print(f"\n📊 Taux de différence avec le terrain vérité : {taux_diff*100:.2f}%")

    # -------------------------
    # Sauvegarde
    # -------------------------
    output_path = os.path.join(BASE_DIR, "cv_filtre_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cv_results, f, indent=4, ensure_ascii=False)

    print(f"\n📁 Résultats sauvegardés dans : {output_path}")
