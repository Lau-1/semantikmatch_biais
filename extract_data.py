import json
import os
import re

def extraire_donnees_ordonnees(chemin_entree, chemin_sortie):
    if not os.path.exists(chemin_entree):
        print(f"Erreur : Le fichier {chemin_entree} est introuvable.")
        return

    with open(chemin_entree, 'r', encoding='utf-8') as f:
        data_source = json.load(f)

    resultat_final = {}

    # 1. Extraction des données
    for candidat in data_source:
        firstname = candidat.get('agg_firstname', '')
        lastname = candidat.get('agg_lastname', '')
        nom_complet = f"{firstname} {lastname}".strip()
        
        mapping_criteres = {c['id']: c['custom_name'] for c in candidat.get('criterias', [])}
        
        # On utilise un dictionnaire temporaire pour stocker les sections trouvées
        sections_trouvees = {}
        for resultat in candidat.get('criteria_result', []):
            critere_id = resultat.get('criteria_id')
            nom_section = mapping_criteres.get(critere_id)
            if nom_section:
                valeur = resultat.get('payload', {}).get('value', [])
                sections_trouvees[nom_section] = valeur

        # 2. Réorganisation interne (Ordre : Experience -> Studies -> Interests)
        # On définit l'ordre exact des clés souhaitées
        ordre_cles = [
            "List of professional experiences",
            "List of studies",
            "List of personal interests"
        ]
        
        cv_ordonne = {}
        for cle in ordre_cles:
            if cle in sections_trouvees:
                cv_ordonne[cle] = sections_trouvees[cle]
        
        resultat_final[nom_complet] = cv_ordonne

    # 3. Tri final des CV par ordre croissant (ex: CV0, CV1, CV2...)
    # On utilise une fonction de tri qui extrait le nombre pour éviter l'ordre alphabétique (CV10 avant CV2)
    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

    liste_triee = sorted(resultat_final.items(), key=lambda x: natural_sort_key(x[0]))
    dict_final_trie = dict(liste_triee)

    # Sauvegarde
    with open(chemin_sortie, 'w', encoding='utf-8') as f:
        json.dump(dict_final_trie, f, indent=4, ensure_ascii=False)

    print(f"✅ Extraction et tri terminés. Fichier généré : {chemin_sortie}")

if __name__ == "__main__":
    extraire_donnees_ordonnees('input.json', 'extracted_cv_sorted.json')