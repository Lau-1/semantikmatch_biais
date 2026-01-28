#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour créer la jointure des extractions (experiences + studies + interests)
pour le run5 avec les nouveaux prompts
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

def fusionner_extractions(dossier_variant, nom_variant):
    """
    Fusionne experiences.json, studies.json et interests.json
    en un seul fichier par CV
    """
    experiences_file = dossier_variant / "experiences.json"
    studies_file = dossier_variant / "studies.json"
    interests_file = dossier_variant / "interests.json"

    # Charger les fichiers
    experiences = {}
    studies = {}
    interests = {}

    if experiences_file.exists():
        with open(experiences_file, 'r', encoding='utf-8') as f:
            experiences = json.load(f)

    if studies_file.exists():
        with open(studies_file, 'r', encoding='utf-8') as f:
            studies = json.load(f)

    if interests_file.exists():
        with open(interests_file, 'r', encoding='utf-8') as f:
            interests = json.load(f)

    # Obtenir tous les CV_IDs
    all_cvs = set(experiences.keys()) | set(studies.keys()) | set(interests.keys())

    print(f"  Variant {nom_variant}:")
    print(f"    - Experiences: {len(experiences)} CVs")
    print(f"    - Studies: {len(studies)} CVs")
    print(f"    - Interests: {len(interests)} CVs")
    print(f"    - Total unique CVs: {len(all_cvs)}")

    # Fusionner les données
    resultat = {}

    for cv_id in all_cvs:
        resultat[cv_id] = {
            'experiences': experiences.get(cv_id, {}).get('experiences', []),
            'studies': studies.get(cv_id, {}).get('studies', []),
            'interests': interests.get(cv_id, {}).get('interests', [])
        }

    return resultat

def main():
    base_dir = Path(__file__).parent
    converted_dir = base_dir / "run1_converted"

    # Créer le dossier Runs_jointure/run5 si nécessaire
    output_dir = base_dir.parent / "Runs_jointure" / "run5"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*80)
    print("CRÉATION DES FICHIERS DE JOINTURE POUR RUN5")
    print("="*80)

    variants = ['Original', 'Gender', 'Origin', 'Age']

    for variant in variants:
        print(f"\n{'='*80}")
        print(f"Traitement : {variant}")
        print(f"{'='*80}")

        variant_dir = converted_dir / variant

        if not variant_dir.exists():
            print(f"⚠️ Dossier non trouvé : {variant_dir}")
            continue

        try:
            # Fusionner les extractions
            data_fusionnee = fusionner_extractions(variant_dir, variant)

            # Sauvegarder
            output_file = output_dir / f"{variant.lower()}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data_fusionnee, f, indent=4, ensure_ascii=False)

            print(f"  ✅ Sauvegardé dans {output_file}")

        except Exception as e:
            print(f"❌ Erreur lors du traitement de {variant}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*80)
    print("JOINTURE TERMINÉE")
    print("="*80)
    print(f"\nFichiers créés dans : {output_dir}")
    print("\nProchaine étape : Lancer l'analyse de biais")
    print("cd ../Analyse")
    print("python analyseorigin.py  # Analysera automatiquement run5")

if __name__ == "__main__":
    main()
