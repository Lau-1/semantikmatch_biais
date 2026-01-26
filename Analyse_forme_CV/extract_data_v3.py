import csv
import json
import os
import re
import ast

def safe_parse_value(valeur):
    """
    Parse intelligemment les champs venant du CSV :
    - JSON encodé en string
    - listes / dicts Python
    - valeurs cassées
    """
    if valeur is None:
        return []

    if isinstance(valeur, (list, dict)):
        return valeur

    if isinstance(valeur, str):
        try:
            cleaned = valeur.replace('""', '"').strip()
            return json.loads(cleaned)
        except Exception:
            try:
                return ast.literal_eval(cleaned)
            except Exception:
                return []

    return []


def extraire_donnees_ordonnees(chemin_entree, chemin_sortie):
    if not os.path.exists(chemin_entree):
        print(f"Erreur : Le fichier {chemin_entree} est introuvable.")
        return

    # 🔹 Lecture CSV + reconstruction d'une structure type "data"
    data_source = []

    with open(chemin_entree, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')

        for row in reader:
            if len(row) < 4:
                continue

            nom = row[0].strip()
            parties_nom = nom.split()

            firstname = parties_nom[0] if parties_nom else ""
            lastname = parties_nom[-1] if len(parties_nom) > 1 else ""

            data_source.append({
                "agg_firstname": firstname,
                "agg_lastname": lastname,
                "criterias": [
                    {"id": 1, "custom_name": "List of personal interests"},
                    {"id": 2, "custom_name": "List of studies"},
                    {"id": 3, "custom_name": "List of professional experiences"}
                ],
                "criteria_result": [
                    {"criteria_id": 1, "payload": {"value": row[1]}},
                    {"criteria_id": 2, "payload": {"value": row[2]}},
                    {"criteria_id": 3, "payload": {"value": row[3]}}
                ]
            })

    resultat_final = {}

    for candidat in data_source:
        # 🔹 Nom formaté (Louis 01, Louis 02...)
        firstname = candidat.get('agg_firstname', '').capitalize()
        lastname = candidat.get('agg_lastname', '')

        try:
            numero = int(lastname)
            nom_complet = f"{firstname} {numero:02d}"
        except ValueError:
            nom_complet = f"{firstname} {lastname}".strip()

        mapping_criteres = {
            c['id']: c['custom_name']
            for c in candidat.get('criterias', [])
        }

        sections_trouvees = {}

        for resultat in candidat.get('criteria_result', []):
            critere_id = resultat.get('criteria_id')
            nom_section = mapping_criteres.get(critere_id)

            if not nom_section:
                continue

            valeur_brute = resultat.get('payload', {}).get('value')
            valeur = safe_parse_value(valeur_brute)

            # 🔹 Déballage si encapsulé
            if isinstance(valeur, dict):
                for key in ("interests", "studies", "experiences"):
                    if key in valeur:
                        valeur = valeur[key]
                        break

            sections_trouvees[nom_section] = valeur

        # 🔹 Ordre imposé
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

    # 🔹 Tri naturel (Louis 09 < Louis 10)
    def natural_sort_key(s):
        return [
            int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)
        ]

    resultat_final = dict(
        sorted(resultat_final.items(), key=lambda x: natural_sort_key(x[0]))
    )

    # 🔹 Sauvegarde JSON
    with open(chemin_sortie, 'w', encoding='utf-8') as f:
        json.dump(resultat_final, f, indent=4, ensure_ascii=False)

    print(f"Extraction terminée avec succès. {len(resultat_final)} CV traités.")


# ▶️ Exécution
if __name__ == "__main__":
    extraire_donnees_ordonnees(
        'Analyse_forme_CV/Audit_forme/input.csv',
        'Analyse_forme_CV/Audit_forme/output.json'
    )
