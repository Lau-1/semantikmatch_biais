#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour convertir les extractions Semantikmatch en format standard
pour l'analyse de biais
"""
import json
import sys
import os
from pathlib import Path

# Configuration de l'encodage pour Windows
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

def convertir_semantik_vers_standard(fichier_source, dossier_sortie):
    """
    Convertit un fichier Semantikmatch en 3 fichiers standards :
    - experiences.json
    - studies.json
    - interests.json
    """
    print(f"Lecture de {fichier_source}...")

    with open(fichier_source, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Trouvé {len(data)} CVs")

    # Structures pour stocker les données converties
    experiences_dict = {}
    studies_dict = {}
    interests_dict = {}

    for cv in data:
        cv_id = cv.get('agg_firstname', 'Unknown')
        pdf_name = f"{cv_id}.pdf"

        # Examiner les criteria_result pour identifier experiences, studies, interests
        criteria_results = cv.get('criteria_result', [])

        for criterion in criteria_results:
            payload = criterion.get('payload', {})
            payload_type = payload.get('type')
            payload_value = payload.get('value')

            # Cas 1 : Interests (type="dict", value={"interests": [...]})
            if payload_type == 'dict' and isinstance(payload_value, dict):
                if 'interests' in payload_value:
                    interests_dict[pdf_name] = {'interests': payload_value['interests']}

            # Cas 2 & 3 : Experiences ou Studies (type="list")
            elif payload_type == 'list' and isinstance(payload_value, list):
                if len(payload_value) > 0:
                    first_item = payload_value[0]

                    # Expériences : contient 'job title', 'company'
                    if isinstance(first_item, dict) and 'job title' in first_item:
                        experiences_dict[pdf_name] = {'experiences': payload_value}

                    # Études : contient 'university', 'level_of_degree', 'field'
                    elif isinstance(first_item, dict) and ('university' in first_item or 'level_of_degree' in first_item):
                        studies_dict[pdf_name] = {'studies': payload_value}

                # Liste vide - difficile de déterminer le type, on skip
                else:
                    pass

    # Créer le dossier de sortie si nécessaire
    os.makedirs(dossier_sortie, exist_ok=True)

    # Sauvegarder les fichiers convertis
    fichier_experiences = os.path.join(dossier_sortie, 'experiences.json')
    fichier_studies = os.path.join(dossier_sortie, 'studies.json')
    fichier_interests = os.path.join(dossier_sortie, 'interests.json')

    with open(fichier_experiences, 'w', encoding='utf-8') as f:
        json.dump(experiences_dict, f, indent=4, ensure_ascii=False)
    print(f"✅ Sauvegardé {len(experiences_dict)} CVs dans {fichier_experiences}")

    with open(fichier_studies, 'w', encoding='utf-8') as f:
        json.dump(studies_dict, f, indent=4, ensure_ascii=False)
    print(f"✅ Sauvegardé {len(studies_dict)} CVs dans {fichier_studies}")

    with open(fichier_interests, 'w', encoding='utf-8') as f:
        json.dump(interests_dict, f, indent=4, ensure_ascii=False)
    print(f"✅ Sauvegardé {len(interests_dict)} CVs dans {fichier_interests}")

    return experiences_dict, studies_dict, interests_dict

def main():
    base_dir = Path(__file__).parent
    run1_dir = base_dir / "run1"

    # Fichiers sources
    fichiers_sources = {
        'Original': run1_dir / "original_extract_semantik.json",
        'Gender': run1_dir / "genre_extract_semantik.json",
        'Origin': run1_dir / "origin_extract_semantik.json",
        'Age': run1_dir / "age_extract_semantik.json"
    }

    print("="*80)
    print("CONVERSION DES EXTRACTIONS SEMANTIKMATCH VERS FORMAT STANDARD")
    print("="*80)

    for variant, fichier_source in fichiers_sources.items():
        print(f"\n{'='*80}")
        print(f"Traitement : {variant}")
        print(f"{'='*80}")

        if not fichier_source.exists():
            print(f"⚠️ Fichier non trouvé : {fichier_source}")
            continue

        # Créer dossier de sortie pour cette variante
        dossier_sortie = base_dir / "run1_converted" / variant

        try:
            convertir_semantik_vers_standard(fichier_source, dossier_sortie)
        except Exception as e:
            print(f"❌ Erreur lors de la conversion de {variant}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*80)
    print("CONVERSION TERMINÉE")
    print("="*80)
    print(f"\nFichiers convertis disponibles dans : {base_dir / 'run1_converted'}")
    print("\nProchaine étape : Lancer l'analyse de biais sur ces nouvelles données")
    print("cd ../Runs_analyse")
    print("# Créer dossier run5 avec ces nouvelles extractions")
    print("# Relancer les analyses")

if __name__ == "__main__":
    main()
