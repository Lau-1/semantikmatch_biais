#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour extraire toutes les erreurs détectées dans les audits de biais
et les exporter dans un fichier JSON structuré
"""
import json
import os
import sys
from pathlib import Path

# Configuration de l'encodage pour Windows
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

def extraire_erreurs():
    """Extrait toutes les erreurs des fichiers d'audit"""
    erreurs = {
        'metadata': {
            'runs_analyses': ['run3', 'run4'],
            'dimensions': ['Genre', 'Origine', 'Age'],
            'total_erreurs': 0,
            'description': 'Extraction des erreurs détectées dans les audits de biais LLM'
        },
        'erreurs_par_run': {},
        'erreurs_detaillees': []
    }

    base_path = Path('../Runs_analyse')

    for run in ['run3', 'run4']:
        erreurs['erreurs_par_run'][run] = {
            'Genre': {'count': 0, 'erreurs': []},
            'Origine': {'count': 0, 'erreurs': []},
            'Age': {'count': 0, 'erreurs': []}
        }

        for dimension in ['gender', 'origin', 'age']:
            rapport_dir = base_path / run / f'Rapport_{dimension}'

            if not rapport_dir.exists():
                print(f'[SKIP] Dossier introuvable: {rapport_dir}')
                continue

            for audit_file in rapport_dir.glob('audit_*.json'):
                section = audit_file.stem.split('_')[-1]  # experiences, studies, interests

                try:
                    with open(audit_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    for item in data:
                        if not item.get('coherent', True):
                            dimension_name = 'Genre' if dimension == 'gender' else 'Origine' if dimension == 'origin' else 'Age'

                            erreur = {
                                'run': run,
                                'dimension': dimension_name,
                                'section': section,
                                'cv_id': item.get('cv_id', 'unknown'),
                                'error_type': item.get('error_type', 'Unknown'),
                                'details': item.get('details', 'No details'),
                                'empty_list': item.get('empty_list', False)
                            }

                            erreurs['erreurs_detaillees'].append(erreur)
                            erreurs['erreurs_par_run'][run][dimension_name]['erreurs'].append(erreur)
                            erreurs['erreurs_par_run'][run][dimension_name]['count'] += 1
                            erreurs['metadata']['total_erreurs'] += 1

                except Exception as e:
                    print(f'[ERR] Erreur lecture {audit_file}: {e}')

    # Statistiques globales
    erreurs['statistiques'] = {
        'par_dimension': {},
        'par_section': {},
        'par_type_erreur': {}
    }

    for err in erreurs['erreurs_detaillees']:
        # Par dimension
        dim = err['dimension']
        if dim not in erreurs['statistiques']['par_dimension']:
            erreurs['statistiques']['par_dimension'][dim] = 0
        erreurs['statistiques']['par_dimension'][dim] += 1

        # Par section
        sec = err['section']
        if sec not in erreurs['statistiques']['par_section']:
            erreurs['statistiques']['par_section'][sec] = 0
        erreurs['statistiques']['par_section'][sec] += 1

        # Par type d'erreur
        typ = err['error_type']
        if typ not in erreurs['statistiques']['par_type_erreur']:
            erreurs['statistiques']['par_type_erreur'][typ] = 0
        erreurs['statistiques']['par_type_erreur'][typ] += 1

    return erreurs

if __name__ == "__main__":
    print("="*70)
    print("EXTRACTION DES ERREURS DÉTECTÉES".center(70))
    print("="*70)
    print()

    # Extraire les erreurs
    resultat = extraire_erreurs()

    # Sauvegarder en JSON
    output_file = 'erreurs_detaillees.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(resultat, f, indent=2, ensure_ascii=False)

    print(f'[OK] Fichier JSON cree: {output_file}')
    print()
    print(f'[STATS] Total erreurs: {resultat["metadata"]["total_erreurs"]}')
    print()
    print('Repartition par dimension:')
    for dim, count in resultat['statistiques']['par_dimension'].items():
        print(f'  - {dim}: {count} erreurs')
    print()
    print('Repartition par section:')
    for sec, count in resultat['statistiques']['par_section'].items():
        print(f'  - {sec}: {count} erreurs')
    print()
    print('Repartition par type:')
    for typ, count in resultat['statistiques']['par_type_erreur'].items():
        print(f'  - {typ}: {count} erreurs')
    print()
    print("="*70)
