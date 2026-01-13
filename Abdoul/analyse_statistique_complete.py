#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyse statistique complète des runs 5, 6, 7 (prompts v2)
"""
import json
import sys
import os
from pathlib import Path
import numpy as np
from scipy import stats
from scipy.stats import fisher_exact
import pandas as pd

# Configuration de l'encodage pour Windows
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

def wilson_confidence_interval(successes, n, confidence=0.95):
    """Calcule l'intervalle de confiance Wilson"""
    if n == 0:
        return 0, 0
    p = successes / n
    z = stats.norm.ppf((1 + confidence) / 2)
    denominator = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denominator
    margin = z * np.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denominator
    return max(0, centre - margin), min(1, centre + margin)

def cohens_h(p1, p2):
    """Calcule Cohen's h"""
    phi1 = 2 * np.arcsin(np.sqrt(p1))
    phi2 = 2 * np.arcsin(np.sqrt(p2))
    return abs(phi1 - phi2)

def analyser_run_dimension(run_dir, dimension):
    """Analyse une dimension pour un run"""
    rapport_dir = run_dir / f"Rapport_{dimension.lower()}"
    if not rapport_dir.exists():
        return None

    sections = ['experiences', 'studies', 'interests']
    total_erreurs = 0
    total_cvs = 0

    for section in sections:
        fichier = rapport_dir / f"audit_{dimension.lower()}_{section}.json"
        if not fichier.exists():
            continue

        with open(fichier, 'r', encoding='utf-8') as f:
            data = json.load(f)

        erreurs_semantiques = len([cv for cv in data if not cv.get('coherent') and not cv.get('empty_list')])
        total_erreurs += erreurs_semantiques
        total_cvs += len(data)

    n_comparaisons = total_cvs
    taux_erreur = (total_erreurs / n_comparaisons * 100) if n_comparaisons > 0 else 0

    # Test de Fisher
    table = [[total_erreurs, 0], [n_comparaisons - total_erreurs, n_comparaisons]]
    _, p_value = fisher_exact(table, alternative='two-sided')

    # Intervalle de confiance
    ic_inf, ic_sup = wilson_confidence_interval(total_erreurs, n_comparaisons, 0.95)

    # Cohen's h
    p_variant = total_erreurs / n_comparaisons if n_comparaisons > 0 else 0
    effect_size = cohens_h(p_variant, 0)

    return {
        'run': run_dir.name,
        'dimension': dimension,
        'erreurs': total_erreurs,
        'total': n_comparaisons,
        'taux_pct': taux_erreur,
        'ic_inf_pct': ic_inf * 100,
        'ic_sup_pct': ic_sup * 100,
        'p_value': p_value,
        'cohen_h': effect_size
    }

def main():
    base_dir = Path(__file__).parent.parent
    runs_analyse_dir = base_dir / "Runs_analyse"

    runs = ['run5', 'run6', 'run7']
    dimensions = ['Gender', 'Origin', 'Age']

    print("="*100)
    print("ANALYSE STATISTIQUE COMPLÈTE - RUNS 5, 6, 7 (Prompts V2)")
    print("="*100)
    print()

    # Collecter tous les résultats
    tous_resultats = []

    for run in runs:
        run_dir = runs_analyse_dir / run
        if not run_dir.exists():
            print(f"⚠️ {run} non trouvé")
            continue

        print(f"📊 Analyse {run.upper()}...")
        for dim in dimensions:
            res = analyser_run_dimension(run_dir, dim)
            if res:
                tous_resultats.append(res)

    print()

    # Créer un DataFrame pour faciliter l'analyse
    df = pd.DataFrame(tous_resultats)

    # Calcul des moyennes par dimension
    print("="*100)
    print("RÉSULTATS PAR RUN ET DIMENSION")
    print("="*100)
    print()

    print(f"{'Run':<8} {'Dimension':<12} {'Erreurs':<10} {'Total':<10} {'Taux (%)':<10} {'IC 95%':<25} {'p-value':<12} {'Cohen h':<10}")
    print("-"*100)

    for _, row in df.iterrows():
        ic_str = f"[{row['ic_inf_pct']:.2f}, {row['ic_sup_pct']:.2f}]"
        print(f"{row['run']:<8} "
              f"{row['dimension']:<12} "
              f"{row['erreurs']:<10} "
              f"{row['total']:<10} "
              f"{row['taux_pct']:<10.2f} "
              f"{ic_str:<25} "
              f"{row['p_value']:<12.6f} "
              f"{row['cohen_h']:<10.3f}")

    # Statistiques par dimension (moyenne des runs)
    print()
    print("="*100)
    print("SYNTHÈSE PAR DIMENSION (Moyenne sur 3 runs)")
    print("="*100)
    print()

    alpha = 0.05
    alpha_bonferroni = alpha / 3

    stats_by_dim = df.groupby('dimension').agg({
        'erreurs': ['sum', 'mean', 'std'],
        'total': 'sum',
        'taux_pct': ['mean', 'std', 'min', 'max'],
        'p_value': 'mean',
        'cohen_h': 'mean'
    }).round(3)

    print(f"{'Dimension':<12} {'Erreurs Tot':<12} {'Taux Moy (%)':<15} {'Écart-type':<12} {'p-value moy':<15} {'Cohen h moy':<12} {'Runs signif':<15}")
    print("-"*100)

    for dim in dimensions:
        if dim not in stats_by_dim.index:
            continue

        erreurs_sum = stats_by_dim.loc[dim, ('erreurs', 'sum')]
        total_sum = stats_by_dim.loc[dim, 'total']['sum']
        taux_moy = stats_by_dim.loc[dim, ('taux_pct', 'mean')]
        taux_std = stats_by_dim.loc[dim, ('taux_pct', 'std')]
        p_moy = stats_by_dim.loc[dim, ('p_value', 'mean')]
        cohen_moy = stats_by_dim.loc[dim, ('cohen_h', 'mean')]

        # Compter combien de runs sont significatifs
        runs_signif = len(df[(df['dimension'] == dim) & (df['p_value'] * 3 < alpha)])
        pct_signif = (runs_signif / 3 * 100)

        print(f"{dim:<12} "
              f"{int(erreurs_sum):<12} "
              f"{taux_moy:.2f} ± {taux_std:.2f}%  "
              f"{taux_std:<12.2f} "
              f"{p_moy:<15.6f} "
              f"{cohen_moy:<12.3f} "
              f"{runs_signif}/3 ({pct_signif:.0f}%)")

    # Test global avec correction de Bonferroni
    print()
    print("="*100)
    print("TEST DE SIGNIFICATIVITÉ (Correction de Bonferroni)")
    print("="*100)
    print()
    print(f"Alpha nominal : 0.05")
    print(f"Alpha corrigé (3 dimensions) : {alpha_bonferroni:.4f}")
    print()

    for dim in dimensions:
        dim_data = df[df['dimension'] == dim]
        if len(dim_data) == 0:
            continue

        # Combiner les données de tous les runs pour un test global
        erreurs_total = dim_data['erreurs'].sum()
        total_comparaisons = dim_data['total'].sum()

        # Test de Fisher global
        table = [[erreurs_total, 0], [total_comparaisons - erreurs_total, total_comparaisons]]
        _, p_global = fisher_exact(table, alternative='two-sided')
        p_bonferroni = min(p_global * 3, 1.0)

        significatif = p_bonferroni < alpha

        print(f"{dim} :")
        print(f"  Erreurs totales : {int(erreurs_total)} / {int(total_comparaisons)}")
        print(f"  Taux global : {erreurs_total/total_comparaisons*100:.2f}%")
        print(f"  p-value (global) : {p_global:.6f}")
        print(f"  p-value (Bonferroni) : {p_bonferroni:.6f}")

        if significatif:
            print(f"  ⚠️ STATISTIQUEMENT SIGNIFICATIF (p < {alpha_bonferroni:.4f})")
        else:
            print(f"  ✅ NON SIGNIFICATIF (p ≥ {alpha_bonferroni:.4f})")

        print()

    # Conclusion finale
    print("="*100)
    print("CONCLUSION FINALE")
    print("="*100)
    print()

    biais_detectes = []
    for dim in dimensions:
        dim_data = df[df['dimension'] == dim]
        if len(dim_data) == 0:
            continue

        erreurs_total = dim_data['erreurs'].sum()
        total_comparaisons = dim_data['total'].sum()
        table = [[erreurs_total, 0], [total_comparaisons - erreurs_total, total_comparaisons]]
        _, p_global = fisher_exact(table, alternative='two-sided')
        p_bonferroni = min(p_global * 3, 1.0)

        if p_bonferroni < alpha:
            biais_detectes.append(dim)

    total_erreurs_global = df['erreurs'].sum()
    total_comparaisons_global = df['total'].sum()
    taux_global = (total_erreurs_global / total_comparaisons_global * 100) if total_comparaisons_global > 0 else 0

    print(f"Total erreurs sémantiques : {int(total_erreurs_global)} sur {int(total_comparaisons_global)} comparaisons")
    print(f"Taux d'erreur global : {taux_global:.2f}%")
    print()

    if len(biais_detectes) == 0:
        print("✅ AUCUN BIAIS STATISTIQUEMENT SIGNIFICATIF DÉTECTÉ")
        print("   Les prompts V2 produisent des extractions équitables pour toutes les dimensions.")
    else:
        print(f"⚠️ BIAIS DÉTECTÉS : {', '.join(biais_detectes)}")
        print("   Nécessite des améliorations supplémentaires.")

    print()
    print("="*100)

    # Sauvegarder les résultats
    output_file = base_dir / "Abdoul" / "resultats_statistiques_runs567.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"✅ Résultats sauvegardés dans : {output_file}")

if __name__ == "__main__":
    main()
