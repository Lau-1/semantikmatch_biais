import json
import os
import re

def extraire_donnees_ordonnees(chemin_entree, chemin_sortie):
    if not os.path.exists(chemin_entree):
        print(f"Erreur : Le fichier {chemin_entree} est introuvable.")
        return

    with open(chemin_entree, 'r', encoding='utf-8') as f:
        data_brute = json.load(f)
        # 1. Adaptation : On récupère la liste sous la clé "data"
        data_source = data_brute.get('data', [])

    resultat_final = {}

    for candidat in data_source:
        # 2. Adaptation du Nom : Prénom + Numéro formaté (ex: Thomas 01)
        firstname = candidat.get('agg_firstname', '').capitalize()
        lastname = candidat.get('agg_lastname', '')

        # On essaie de convertir le nom de famille (ex: "13") en nombre pour le formater "13" -> "13", "9" -> "09"
        try:
            numero = int(lastname)
            nom_complet = f"{firstname} {numero:02d}"
        except ValueError:
            # Si le nom de famille n'est pas un nombre, on l'affiche normalement
            nom_complet = f"{firstname} {lastname}".strip()

        # Mapping des IDs de critères vers leurs noms
        mapping_criteres = {c['id']: c['custom_name'] for c in candidat.get('criterias', [])}

        sections_trouvees = {}
        for resultat in candidat.get('criteria_result', []):
            critere_id = resultat.get('criteria_id')
            nom_section = mapping_criteres.get(critere_id)

            if nom_section:
                # Récupération de la valeur brute
                valeur = resultat.get('payload', {}).get('value', [])

                # 3. Adaptation : Nettoyage des structures encapsulées (ex: intérêts dans un dict)
                if isinstance(valeur, dict):
                    if "interests" in valeur:
                        valeur = valeur["interests"]
                    elif "experiences" in valeur:
                        valeur = valeur["experiences"]
                    elif "studies" in valeur:
                        valeur = valeur["studies"]

                sections_trouvees[nom_section] = valeur

        # Réorganisation interne (Ordre : Experience -> Studies -> Interests)
        ordre_cles = [
            "List of professional experiences",
            "List of studies",
            "List of personal interests"
        ]

        cv_ordonne = {}
        for cle in ordre_cles:
            # On inclut la section même si elle est vide (pour matcher la structure demandée),
            # ou vous pouvez remettre 'if cle in sections_trouvees' pour filtrer.
            if cle in sections_trouvees:
                cv_ordonne[cle] = sections_trouvees[cle]

        resultat_final[nom_complet] = cv_ordonne

    # 4. Tri final intelligent (Thomas 09 avant Thomas 10)
    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

    liste_triee = sorted(resultat_final.items(), key=lambda x: natural_sort_key(x[0]))
    dict_final_trie = dict(liste_triee)

    # Sauvegarde
    with open(chemin_sortie, 'w', encoding='utf-8') as f:
        json.dump(dict_final_trie, f, indent=4, ensure_ascii=False)

    print(f"Extraction terminée avec succès. {len(dict_final_trie)} CV traités.")

# Exécution du script
if __name__ == "__main__":
    # Assurez-vous que le fichier source s'appelle bien input.json
    extraire_donnees_ordonnees('Analyse_forme_CV/Audit_forme/input.json', 'Analyse_forme_CV/Audit_forme/output.json')
