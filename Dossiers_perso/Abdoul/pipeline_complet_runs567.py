#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pipeline complet pour run5, run6, run7 : extraction → analyse → statistiques
"""
import json
import sys
import os
from pathlib import Path
import shutil

def convertir_semantik_format(run_name):
    """
    Convertit un run du format Semantikmatch vers le format standard
    """
    print(f"\n{'='*80}")
    print(f"ETAPE 1 : Conversion du format Semantikmatch vers Standard pour {run_name}")
    print('='*80)

    base_dir = Path(__file__).parent.parent
    source_dir = base_dir / "Extract_via_semantikmatch" / run_name
    target_dir = base_dir / "Runs_jointure" / run_name

    if not source_dir.exists():
        print(f"❌ Dossier source non trouvé : {source_dir}")
        return False

    # Créer le dossier de destination
    target_dir.mkdir(parents=True, exist_ok=True)

    dimensions = ['original', 'age', 'gender', 'origin']

    for dim in dimensions:
        source_file = source_dir / f"{dim}.json"
        target_file = target_dir / f"{dim}.json"

        if not source_file.exists():
            print(f"⚠️ Fichier manquant : {source_file}")
            continue

        print(f"📄 Conversion : {dim}.json")

        with open(source_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Structure de sortie
        experiences_dict = {}
        studies_dict = {}
        interests_dict = {}

        # Deux formats possibles :
        # Format 1 : Liste d'applications (Semantikmatch brut)
        # Format 2 : Dict avec clés "CV0 Original" (déjà partiellement converti)

        if isinstance(data, list):
            # Format 1 : Liste d'applications Semantikmatch
            for application in data:
                # Récupérer le nom du CV depuis agg_firstname (ex: "CV99")
                cv_name = application.get('agg_firstname', 'Unknown')
                variant = application.get('agg_lastname', 'Unknown')

                # Construire le pdf_name (ex: "CV99 Original")
                pdf_name = f"{cv_name} {variant}"

                # Structure attendue : {"criteria_result": [{"payload": {...}}]}
                if 'criteria_result' not in application:
                    continue

                for result in application['criteria_result']:
                    if 'payload' not in result:
                        continue

                    payload = result['payload']
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
                            if isinstance(first_item, dict):
                                # Experiences : contient "job title"
                                if 'job title' in first_item:
                                    experiences_dict[pdf_name] = {'experiences': payload_value}
                                # Studies : contient "field" ou "level_of_degree"
                                elif 'field' in first_item or 'level_of_degree' in first_item:
                                    studies_dict[pdf_name] = {'studies': payload_value}

        elif isinstance(data, dict):
            # Format 2 : Dict avec clés "CV0 Original"
            for pdf_name, cv_data in data.items():
                # Extraire experiences
                if 'List of professional experiences' in cv_data:
                    experiences_dict[pdf_name] = {'experiences': cv_data['List of professional experiences']}

                # Extraire studies
                if 'List of studies' in cv_data:
                    studies_data = cv_data['List of studies']
                    # Peut être dict avec key "studies" ou directement une liste
                    if isinstance(studies_data, dict) and 'studies' in studies_data:
                        studies_dict[pdf_name] = {'studies': studies_data['studies']}
                    elif isinstance(studies_data, list):
                        studies_dict[pdf_name] = {'studies': studies_data}

                # Extraire interests
                if 'List of personal interests' in cv_data:
                    interests_dict[pdf_name] = {'interests': cv_data['List of personal interests']}

        else:
            print(f"  ⚠️ Format non reconnu pour {dim}.json")
            continue

        # Fusionner les 3 types dans un seul fichier
        output_dict = {}
        all_pdf_names = set(experiences_dict.keys()) | set(studies_dict.keys()) | set(interests_dict.keys())

        for pdf_name in sorted(all_pdf_names):
            output_dict[pdf_name] = {
                'experiences': experiences_dict.get(pdf_name, {}).get('experiences', []),
                'studies': studies_dict.get(pdf_name, {}).get('studies', []),
                'interests': interests_dict.get(pdf_name, {}).get('interests', [])
            }

        # Sauvegarder
        with open(target_file, 'w', encoding='utf-8') as f:
            json.dump(output_dict, f, indent=4, ensure_ascii=False)

        print(f"  ✅ {len(output_dict)} CVs convertis")

    print(f"✅ Conversion terminée pour {run_name}\n")
    return True


def preparer_fichiers_separes(run_name):
    """
    Crée les fichiers séparés experiences.json, studies.json, interests.json
    """
    print(f"\n{'='*80}")
    print(f"ETAPE 2 : Preparation des fichiers separes pour {run_name}")
    print('='*80)

    base_dir = Path(__file__).parent.parent
    run_dir = base_dir / "Runs_jointure" / run_name

    if not run_dir.exists():
        print(f"❌ Dossier non trouvé : {run_dir}")
        return False

    dimensions = ['Original', 'Gender', 'Origin', 'Age']
    data_by_dimension = {}

    # Charger tous les fichiers
    for dim in dimensions:
        fichier = run_dir / f"{dim.lower()}.json"
        if fichier.exists():
            with open(fichier, 'r', encoding='utf-8') as f:
                data_by_dimension[dim] = json.load(f)
        else:
            print(f"  ⚠️ Fichier manquant : {fichier}")
            return False

    # Obtenir tous les CV_IDs
    all_cvs = set()
    for data in data_by_dimension.values():
        all_cvs.update(data.keys())

    # Structures pour les fichiers séparés
    experiences = {}
    studies = {}
    interests = {}

    for cv_id in all_cvs:
        # Experiences
        experiences[cv_id] = {}
        for dim in dimensions:
            if cv_id in data_by_dimension[dim]:
                experiences[cv_id][dim] = data_by_dimension[dim][cv_id].get('experiences', [])
            else:
                experiences[cv_id][dim] = []

        # Studies
        studies[cv_id] = {}
        for dim in dimensions:
            if cv_id in data_by_dimension[dim]:
                studies[cv_id][dim] = data_by_dimension[dim][cv_id].get('studies', [])
            else:
                studies[cv_id][dim] = []

        # Interests
        interests[cv_id] = {}
        for dim in dimensions:
            if cv_id in data_by_dimension[dim]:
                interests[cv_id][dim] = data_by_dimension[dim][cv_id].get('interests', [])
            else:
                interests[cv_id][dim] = []

    # Sauvegarder les fichiers
    with open(run_dir / 'experiences.json', 'w', encoding='utf-8') as f:
        json.dump(experiences, f, indent=4, ensure_ascii=False)

    with open(run_dir / 'studies.json', 'w', encoding='utf-8') as f:
        json.dump(studies, f, indent=4, ensure_ascii=False)

    with open(run_dir / 'interests.json', 'w', encoding='utf-8') as f:
        json.dump(interests, f, indent=4, ensure_ascii=False)

    print(f"  ✅ Créé experiences.json ({len(experiences)} CVs)")
    print(f"  ✅ Créé studies.json ({len(studies)} CVs)")
    print(f"  ✅ Créé interests.json ({len(interests)} CVs)")
    print(f"✅ Préparation terminée pour {run_name}\n")

    return True


def lancer_analyses(run_name):
    """
    Lance les analyses d'audit pour toutes les dimensions
    """
    print(f"\n{'='*80}")
    print(f"ETAPE 3 : Analyses d'audit pour {run_name}")
    print('='*80)

    base_dir = Path(__file__).parent.parent
    os.chdir(base_dir)

    # Importer les classes d'analyse
    sys.path.insert(0, str(base_dir / "Analyse"))
    from analyseorigin import AnalyseOrigin
    from analysegenre import AnalyseGenre
    from analyseage import AnalyseAge

    print("\n📊 Analyse Origin...")
    analyseur_origin = AnalyseOrigin()
    analyseur_origin.process_runs(
        input_root="Runs_jointure",
        output_root="Runs_analyse",
        target_runs=[run_name]
    )

    print("\n📊 Analyse Gender...")
    analyseur_gender = AnalyseGenre()
    analyseur_gender.process_runs(
        input_root="Runs_jointure",
        output_root="Runs_analyse",
        target_runs=[run_name]
    )

    print("\n📊 Analyse Age...")
    analyseur_age = AnalyseAge()
    analyseur_age.process_runs(
        input_root="Runs_jointure",
        output_root="Runs_analyse",
        target_runs=[run_name]
    )

    print(f"✅ Analyses terminées pour {run_name}\n")
    return True


def main():
    print("="*80)
    print("PIPELINE COMPLET - RUNS 5, 6, 7 (Prompts V2)")
    print("="*80)
    print()

    runs = ['run5', 'run6', 'run7']

    # Phase 1 : Conversion de tous les runs
    print("\n" + "="*80)
    print("PHASE 1 : CONVERSION DU FORMAT")
    print("="*80)
    for run in runs:
        if not convertir_semantik_format(run):
            print(f"❌ Échec de la conversion pour {run}")
            return

    # Phase 2 : Préparation des fichiers séparés
    print("\n" + "="*80)
    print("PHASE 2 : PRÉPARATION DES FICHIERS SÉPARÉS")
    print("="*80)
    for run in runs:
        if not preparer_fichiers_separes(run):
            print(f"❌ Échec de la préparation pour {run}")
            return

    # Phase 3 : Analyses d'audit
    print("\n" + "="*80)
    print("PHASE 3 : ANALYSES D'AUDIT")
    print("="*80)
    for run in runs:
        if not lancer_analyses(run):
            print(f"❌ Échec de l'analyse pour {run}")
            return

    # Phase 4 : Analyse statistique
    print("\n" + "="*80)
    print("PHASE 4 : ANALYSE STATISTIQUE COMPLÈTE")
    print("="*80)
    print("Lancement du script d'analyse statistique...")

    base_dir = Path(__file__).parent.parent
    os.chdir(base_dir / "Abdoul")

    # Importer et exécuter l'analyse statistique
    import analyse_statistique_complete

    print("\n" + "="*80)
    print("✅ PIPELINE TERMINÉ AVEC SUCCÈS")
    print("="*80)
    print()
    print("Prochaine étape : Mettre à jour le rapport LaTeX")
    print("Résultats disponibles dans :")
    print(f"  - Runs_analyse/run5, run6, run7/")
    print(f"  - Abdoul/resultats_statistiques_runs567.csv")


if __name__ == "__main__":
    main()
