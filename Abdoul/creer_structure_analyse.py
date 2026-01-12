#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour créer la structure de fichiers attendue par les scripts d'analyse
À partir des fichiers de jointure (original.json, origin.json, etc.),
créer les fichiers séparés (experiences.json, studies.json, interests.json)
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

def separer_fichiers(run_dir):
    """
    Lit original.json et origin.json, et crée :
    - experiences.json : {cv_id: {'Original': [...], 'Origin': [...]}}
    - studies.json : {cv_id: {'Original': [...], 'Origin': [...]}}
    - interests.json : {cv_id: {'Original': [...], 'Origin': [...]}}
    """

    # Charger les fichiers de jointure
    with open(run_dir / 'original.json', 'r', encoding='utf-8') as f:
        original_data = json.load(f)

    with open(run_dir / 'origin.json', 'r', encoding='utf-8') as f:
        origin_data = json.load(f)

    # Structures pour les fichiers séparés
    experiences = {}
    studies = {}
    interests = {}

    # Obtenir tous les CV_IDs
    all_cvs = set(original_data.keys()) | set(origin_data.keys())

    for cv_id in all_cvs:
        # Experiences
        experiences[cv_id] = {
            'Original': original_data.get(cv_id, {}).get('experiences', []),
            'Origin': origin_data.get(cv_id, {}).get('experiences', [])
        }

        # Studies
        studies[cv_id] = {
            'Original': original_data.get(cv_id, {}).get('studies', []),
            'Origin': origin_data.get(cv_id, {}).get('studies', [])
        }

        # Interests
        interests[cv_id] = {
            'Original': original_data.get(cv_id, {}).get('interests', []),
            'Origin': origin_data.get(cv_id, {}).get('interests', [])
        }

    # Sauvegarder
    with open(run_dir / 'experiences.json', 'w', encoding='utf-8') as f:
        json.dump(experiences, f, indent=4, ensure_ascii=False)

    with open(run_dir / 'studies.json', 'w', encoding='utf-8') as f:
        json.dump(studies, f, indent=4, ensure_ascii=False)

    with open(run_dir / 'interests.json', 'w', encoding='utf-8') as f:
        json.dump(interests, f, indent=4, ensure_ascii=False)

    print(f"✅ Créé experiences.json ({len(experiences)} CVs)")
    print(f"✅ Créé studies.json ({len(studies)} CVs)")
    print(f"✅ Créé interests.json ({len(interests)} CVs)")

def main():
    run5_dir = Path(__file__).parent.parent / "Runs_jointure" / "run5"

    print("="*80)
    print("CRÉATION DE LA STRUCTURE DE FICHIERS POUR L'ANALYSE")
    print("="*80)
    print(f"\nDossier : {run5_dir}")
    print()

    if not run5_dir.exists():
        print(f"❌ Dossier non trouvé : {run5_dir}")
        return

    try:
        separer_fichiers(run5_dir)
        print("\n✅ Structure créée avec succès")
        print("\nProchaine étape : Relancer les analyses")
        print("cd ../Analyse")
        print("python analyseorigin.py")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
