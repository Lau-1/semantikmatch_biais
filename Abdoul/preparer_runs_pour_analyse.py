#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour préparer les runs 5, 6, 7 pour l'analyse
Crée les fichiers séparés (experiences.json, studies.json, interests.json)
à partir des fichiers de jointure
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

def separer_fichiers(run_dir, dimensions=['Original', 'Gender', 'Origin', 'Age']):
    """
    Lit les fichiers de jointure et crée les fichiers séparés pour l'analyse
    """
    # Charger tous les fichiers
    data_by_dimension = {}

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

    return True

def main():
    base_dir = Path(__file__).parent.parent
    runs_jointure_dir = base_dir / "Runs_jointure"

    runs_a_preparer = ['run5', 'run6', 'run7']

    print("="*80)
    print("PRÉPARATION DES RUNS POUR L'ANALYSE")
    print("="*80)
    print()

    for run in runs_a_preparer:
        run_dir = runs_jointure_dir / run

        if not run_dir.exists():
            print(f"⚠️ Dossier non trouvé : {run_dir}")
            continue

        print(f"📂 {run.upper()} :")

        success = separer_fichiers(run_dir)

        if not success:
            print(f"  ❌ Échec de la préparation")

        print()

    print("="*80)
    print("✅ PRÉPARATION TERMINÉE")
    print("="*80)
    print()
    print("Prochaine étape : Lancer les analyses")
    print("python Analyse/analyseorigin.py")
    print("python Analyse/analysegenre.py")
    print("python Analyse/analyseage.py")

if __name__ == "__main__":
    main()
