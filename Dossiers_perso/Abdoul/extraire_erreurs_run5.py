#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour extraire toutes les erreurs détectées dans run5 (nouveaux prompts v2)
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

def extraire_erreurs_run(run_dir):
    """Extrait les erreurs d'un run"""
    dimensions = ['gender', 'origin', 'age']
    sections = ['experiences', 'studies', 'interests']

    erreurs = {
        'Genre': {'total': 0, 'semantiques': 0, 'empty': 0, 'details': []},
        'Origine': {'total': 0, 'semantiques': 0, 'empty': 0, 'details': []},
        'Age': {'total': 0, 'semantiques': 0, 'empty': 0, 'details': []}
    }

    dimension_map = {'gender': 'Genre', 'origin': 'Origine', 'age': 'Age'}

    for dim in dimensions:
        rapport_dir = run_dir / f"Rapport_{dim}"
        if not rapport_dir.exists():
            continue

        dim_name = dimension_map[dim]

        for section in sections:
            fichier = rapport_dir / f"audit_{dim}_{section}.json"
            if not fichier.exists():
                continue

            with open(fichier, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Compter les erreurs
            for cv in data:
                if not cv.get('coherent'):
                    erreurs[dim_name]['total'] += 1

                    if cv.get('empty_list'):
                        erreurs[dim_name]['empty'] += 1
                    else:
                        erreurs[dim_name]['semantiques'] += 1
                        erreurs[dim_name]['details'].append({
                            'cv_id': cv.get('cv_id'),
                            'section': section,
                            'error_type': cv.get('error_type'),
                            'details': cv.get('details', '')
                        })

    return erreurs

def main():
    base_dir = Path(__file__).parent.parent
    run5_dir = base_dir / "Runs_analyse" / "run5"

    print("="*80)
    print("EXTRACTION DES ERREURS - RUN5 (Prompts V2)")
    print("="*80)
    print()

    if not run5_dir.exists():
        print(f"❌ Dossier non trouvé : {run5_dir}")
        return

    erreurs = extraire_erreurs_run(run5_dir)

    # Affichage des résultats
    print("RÉSULTATS PAR DIMENSION :")
    print("-" * 80)

    total_semantique = 0
    for dim in ['Genre', 'Origine', 'Age']:
        stats = erreurs[dim]
        total_semantique += stats['semantiques']

        print(f"\n{dim} :")
        print(f"  Total erreurs détectées : {stats['total']}")
        print(f"  Erreurs empty_list : {stats['empty']}")
        print(f"  Erreurs sémantiques : {stats['semantiques']}")

        if stats['semantiques'] > 0:
            print(f"\n  Détails des erreurs sémantiques :")
            for err in stats['details'][:10]:  # Afficher les 10 premières
                print(f"    • {err['cv_id']} ({err['section']}) - {err['error_type']}")
                print(f"      {err['details'][:120]}...")

    print()
    print("="*80)
    print(f"TOTAL ERREURS SÉMANTIQUES : {total_semantique}")
    print("="*80)

    # Sauvegarder dans un fichier JSON
    output_file = base_dir / "Abdoul" / "erreurs_run5.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(erreurs, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Erreurs sauvegardées dans : {output_file}")

    # Comparaison avec run3+4
    print()
    print("="*80)
    print("COMPARAISON AVEC RUN3+4 (Prompts V1)")
    print("="*80)

    # Valeurs de référence (depuis l'analyse précédente)
    ref_run34 = {
        'Genre': 5.5,  # (1 + 10) / 2 depuis erreurs_detaillees.json
        'Origine': 8.5,  # (8 + 9) / 2
        'Age': 3.5  # (0 + 7) / 2
    }

    print(f"\n{'Dimension':<12} {'Run3+4 (v1)':<15} {'Run5 (v2)':<15} {'Évolution':<20}")
    print("-" * 80)

    total_v1 = sum(ref_run34.values())

    for dim in ['Genre', 'Origine', 'Age']:
        v1 = ref_run34[dim]
        v2 = erreurs[dim]['semantiques']
        evolution = v2 - v1
        evolution_pct = (evolution / v1 * 100) if v1 > 0 else (100 if v2 > 0 else 0)

        evolution_str = f"{evolution:+.1f} ({evolution_pct:+.0f}%)"

        print(f"{dim:<12} {v1:<15.1f} {v2:<15d} {evolution_str:<20}")

    print("-" * 80)
    print(f"{'TOTAL':<12} {total_v1:<15.1f} {total_semantique:<15d} {total_semantique - total_v1:+.1f} ({(total_semantique - total_v1) / total_v1 * 100:+.0f}%)")

    print()
    print("="*80)

if __name__ == "__main__":
    main()
