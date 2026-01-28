#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour analyser les résultats de run5 (nouveaux prompts v2)
et les comparer avec run3+run4 (anciens prompts v1)
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

def compter_erreurs_semantiques(fichier_audit):
    """
    Compte les vraies erreurs sémantiques (excluant les empty_list)
    """
    with open(fichier_audit, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_cvs = len(data)
    total_erreurs = len([cv for cv in data if not cv.get('coherent')])
    erreurs_empty = len([cv for cv in data if not cv.get('coherent') and cv.get('empty_list')])
    vraies_erreurs = len([cv for cv in data if not cv.get('coherent') and not cv.get('empty_list')])

    return {
        'total_cvs': total_cvs,
        'total_erreurs': total_erreurs,
        'erreurs_empty': erreurs_empty,
        'vraies_erreurs': vraies_erreurs,
        'taux_total': (total_erreurs / total_cvs * 100) if total_cvs > 0 else 0,
        'taux_semantique': (vraies_erreurs / total_cvs * 100) if total_cvs > 0 else 0
    }

def analyser_run(run_name, rapport_dir):
    """Analyse un run complet"""
    sections = ['experiences', 'studies', 'interests']
    resultats = {}

    for section in sections:
        fichier = rapport_dir / f"audit_origin_{section}.json"
        if fichier.exists():
            resultats[section] = compter_erreurs_semantiques(fichier)
        else:
            resultats[section] = None

    return resultats

def main():
    base_dir = Path(__file__).parent.parent
    runs_analyse_dir = base_dir / "Runs_analyse"

    print("="*80)
    print("ANALYSE COMPARATIVE : RUN5 (v2) vs RUN3+RUN4 (v1)")
    print("="*80)
    print()

    # Analyser run3, run4, run5
    runs_a_analyser = ['run3', 'run4', 'run5']
    tous_resultats = {}

    for run in runs_a_analyser:
        rapport_dir = runs_analyse_dir / run / "Rapport_origin"
        if rapport_dir.exists():
            print(f"Analyse de {run}...")
            tous_resultats[run] = analyser_run(run, rapport_dir)
        else:
            print(f"⚠️ Rapport non trouvé pour {run}")

    print()
    print("="*80)
    print("RÉSULTATS DÉTAILLÉS")
    print("="*80)

    for run, resultats in tous_resultats.items():
        print(f"\n{run.upper()} :")
        for section, stats in resultats.items():
            if stats:
                print(f"  {section.capitalize():12} : {stats['vraies_erreurs']:2d} erreurs sémantiques ({stats['taux_semantique']:.2f}%) "
                      f"[{stats['total_erreurs']} total dont {stats['erreurs_empty']} empty]")
            else:
                print(f"  {section.capitalize():12} : Non disponible")

    # Calcul des totaux
    print()
    print("="*80)
    print("SYNTHÈSE COMPARATIVE")
    print("="*80)

    for run, resultats in tous_resultats.items():
        total_semantique = sum(stats['vraies_erreurs'] for stats in resultats.values() if stats)
        total_cvs = sum(stats['total_cvs'] for stats in resultats.values() if stats) / 3  # Moyenne sur 3 sections
        taux_global = (total_semantique / (total_cvs * 3) * 100) if total_cvs > 0 else 0

        print(f"\n{run.upper()} :")
        print(f"  Total erreurs sémantiques : {total_semantique}")
        print(f"  Taux global : {taux_global:.2f}%")

    # Comparaison v1 vs v2
    print()
    print("="*80)
    print("COMPARAISON AVANT/APRÈS")
    print("="*80)

    # Moyenne run3+run4
    if 'run3' in tous_resultats and 'run4' in tous_resultats:
        total_v1 = 0
        for section in ['experiences', 'studies', 'interests']:
            r3 = tous_resultats['run3'][section]['vraies_erreurs'] if tous_resultats['run3'][section] else 0
            r4 = tous_resultats['run4'][section]['vraies_erreurs'] if tous_resultats['run4'][section] else 0
            total_v1 += (r3 + r4) / 2

        taux_v1 = (total_v1 / 300 * 100)

        print(f"\nV1 (Prompts originaux) - Moyenne run3+run4 :")
        print(f"  Erreurs sémantiques : {total_v1:.1f}")
        print(f"  Taux : {taux_v1:.2f}%")

    # Run5
    if 'run5' in tous_resultats:
        total_v2 = sum(tous_resultats['run5'][s]['vraies_erreurs'] for s in ['experiences', 'studies', 'interests'] if tous_resultats['run5'][s])
        taux_v2 = (total_v2 / 300 * 100)

        print(f"\nV2 (Prompts améliorés) - run5 :")
        print(f"  Erreurs sémantiques : {total_v2}")
        print(f"  Taux : {taux_v2:.2f}%")

        # Calcul amélioration
        if 'run3' in tous_resultats:
            reduction = ((total_v1 - total_v2) / total_v1 * 100) if total_v1 > 0 else 0
            print(f"\n✅ AMÉLIORATION : {reduction:.1f}%")
            print(f"   Réduction : {total_v1:.1f} → {total_v2} erreurs")

    # Détails par section
    print()
    print("="*80)
    print("DÉTAILS PAR SECTION")
    print("="*80)

    for section in ['experiences', 'studies', 'interests']:
        print(f"\n{section.upper()} :")
        print(f"{'':10} {'V1 (run3+4)':15} {'V2 (run5)':15} {'Évolution':15}")
        print("-" * 60)

        if 'run3' in tous_resultats and 'run4' in tous_resultats and 'run5' in tous_resultats:
            r3 = tous_resultats['run3'][section]['vraies_erreurs'] if tous_resultats['run3'][section] else 0
            r4 = tous_resultats['run4'][section]['vraies_erreurs'] if tous_resultats['run4'][section] else 0
            r5 = tous_resultats['run5'][section]['vraies_erreurs'] if tous_resultats['run5'][section] else 0

            v1_moy = (r3 + r4) / 2
            evolution = r5 - v1_moy
            evolution_pct = (evolution / v1_moy * 100) if v1_moy > 0 else (100 if r5 > 0 else 0)

            evolution_str = f"{evolution:+.1f} ({evolution_pct:+.0f}%)"

            print(f"{'Erreurs':10} {v1_moy:15.1f} {r5:15d} {evolution_str:15}")

    print()
    print("="*80)

if __name__ == "__main__":
    main()
