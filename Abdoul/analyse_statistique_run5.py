#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyse statistique complète du run5 (prompts v2)
avec tests de Fisher, intervalles de confiance Wilson, Cohen's h, Bonferroni
"""
import json
import sys
import os
from pathlib import Path
import numpy as np
from scipy import stats
from scipy.stats import fisher_exact

# Configuration de l'encodage pour Windows
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

def wilson_confidence_interval(successes, n, confidence=0.95):
    """
    Calcule l'intervalle de confiance Wilson pour une proportion
    """
    if n == 0:
        return 0, 0

    p = successes / n
    z = stats.norm.ppf((1 + confidence) / 2)

    denominator = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denominator
    margin = z * np.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denominator

    return max(0, centre - margin), min(1, centre + margin)

def cohens_h(p1, p2):
    """
    Calcule Cohen's h (taille d'effet pour proportions)
    """
    phi1 = 2 * np.arcsin(np.sqrt(p1))
    phi2 = 2 * np.arcsin(np.sqrt(p2))
    return abs(phi1 - phi2)

def analyser_dimension(dimension, run_dir):
    """
    Analyse statistique complète pour une dimension
    """
    rapport_dir = run_dir / f"Rapport_{dimension.lower()}"

    if not rapport_dir.exists():
        return None

    sections = ['experiences', 'studies', 'interests']
    total_erreurs = 0
    total_cvs = 0

    # Compter les erreurs sémantiques (sans empty_list)
    for section in sections:
        fichier = rapport_dir / f"audit_{dimension.lower()}_{section}.json"
        if not fichier.exists():
            continue

        with open(fichier, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Compter seulement les vraies erreurs sémantiques
        erreurs_semantiques = len([cv for cv in data if not cv.get('coherent') and not cv.get('empty_list')])
        total_erreurs += erreurs_semantiques
        total_cvs += len(data)

    # Moyenne sur 3 sections (100 CVs par section = 300 comparaisons)
    n_comparaisons = 300  # 100 CVs × 3 sections
    taux_erreur = (total_erreurs / n_comparaisons * 100) if n_comparaisons > 0 else 0

    # Test de Fisher exact
    # H0 : pas de différence entre Original et Variant
    # Tableau de contingence : [[erreurs_variant, non_erreurs_variant], [0, n_comparaisons]]
    # (Hypothèse : Original parfait, donc 0 erreur)

    erreurs = total_erreurs
    non_erreurs = n_comparaisons - erreurs

    # Tableau 2×2 : [[erreurs_variant, erreurs_original], [non_erreurs_variant, non_erreurs_original]]
    # On suppose Original parfait : 0 erreur
    table = [[erreurs, 0], [non_erreurs, n_comparaisons]]

    _, p_value = fisher_exact(table, alternative='two-sided')

    # Intervalle de confiance Wilson (95%)
    ic_inf, ic_sup = wilson_confidence_interval(erreurs, n_comparaisons, 0.95)
    ic_inf_pct = ic_inf * 100
    ic_sup_pct = ic_sup * 100

    # Cohen's h (comparaison avec taux 0%)
    p_variant = erreurs / n_comparaisons
    p_original = 0  # Hypothèse : Original parfait
    effect_size = cohens_h(p_variant, p_original)

    # Correction de Bonferroni (3 dimensions)
    alpha = 0.05
    alpha_bonferroni = alpha / 3
    p_value_bonferroni = p_value * 3
    significatif = p_value_bonferroni < alpha

    # Puissance du test (approximation)
    # Puissance ≈ 1 - β où β est le risque de type II
    # Pour un test de Fisher, on peut estimer la puissance
    from scipy.stats import binom
    puissance = 1 - binom.cdf(erreurs - 1, n_comparaisons, 0.01)  # Hypothèse alternative : taux > 1%

    return {
        'dimension': dimension,
        'erreurs': erreurs,
        'total': n_comparaisons,
        'taux_pct': taux_erreur,
        'ic_inf_pct': ic_inf_pct,
        'ic_sup_pct': ic_sup_pct,
        'p_value': p_value,
        'p_value_bonferroni': min(p_value_bonferroni, 1.0),
        'cohen_h': effect_size,
        'puissance': puissance,
        'significatif': significatif,
        'alpha_bonferroni': alpha_bonferroni
    }

def main():
    base_dir = Path(__file__).parent.parent
    run5_dir = base_dir / "Runs_analyse" / "run5"

    print("="*90)
    print("ANALYSE STATISTIQUE COMPLÈTE - RUN5 (Prompts V2)")
    print("="*90)
    print()

    if not run5_dir.exists():
        print(f"❌ Dossier non trouvé : {run5_dir}")
        return

    dimensions = ['Gender', 'Origin', 'Age']
    resultats = []

    for dim in dimensions:
        res = analyser_dimension(dim, run5_dir)
        if res:
            resultats.append(res)

    # Affichage des résultats
    print("RÉSULTATS DES TESTS STATISTIQUES :")
    print("="*90)
    print()

    # En-tête du tableau
    print(f"{'Dimension':<12} {'Erreurs':<10} {'Total':<8} {'Taux (%)':<10} {'IC 95%':<20} {'p-value':<12} {'p-Bonf.':<12} {'Cohen h':<10} {'Signif.':<10}")
    print("-"*90)

    for res in resultats:
        ic_str = f"[{res['ic_inf_pct']:.2f}, {res['ic_sup_pct']:.2f}]"
        signif_str = "✅ OUI" if res['significatif'] else "❌ NON"

        print(f"{res['dimension']:<12} "
              f"{res['erreurs']:<10} "
              f"{res['total']:<8} "
              f"{res['taux_pct']:<10.2f} "
              f"{ic_str:<20} "
              f"{res['p_value']:<12.4f} "
              f"{res['p_value_bonferroni']:<12.4f} "
              f"{res['cohen_h']:<10.3f} "
              f"{signif_str:<10}")

    print()
    print("="*90)
    print("INTERPRÉTATION DES RÉSULTATS")
    print("="*90)
    print()

    print("📊 Métriques utilisées :")
    print("  • IC 95% : Intervalle de confiance à 95% (méthode Wilson)")
    print("  • p-value : Probabilité sous H0 (test de Fisher exact)")
    print("  • p-Bonf. : p-value corrigée pour comparaisons multiples (Bonferroni)")
    print(f"  • Alpha corrigé : {resultats[0]['alpha_bonferroni']:.4f} (= 0.05 / 3 dimensions)")
    print("  • Cohen's h : Taille d'effet (0.2=petit, 0.5=moyen, 0.8=grand)")
    print()

    print("🔍 Interprétation par dimension :")
    print("-"*90)

    for res in resultats:
        print(f"\n{res['dimension']} :")
        print(f"  Taux d'erreur : {res['taux_pct']:.2f}% (IC 95% : [{res['ic_inf_pct']:.2f}%, {res['ic_sup_pct']:.2f}%])")
        print(f"  p-value (Bonferroni) : {res['p_value_bonferroni']:.4f}")

        if res['significatif']:
            print(f"  ⚠️ BIAIS STATISTIQUEMENT SIGNIFICATIF (p < {res['alpha_bonferroni']:.4f})")
        else:
            print(f"  ✅ PAS DE BIAIS SIGNIFICATIF (p ≥ {res['alpha_bonferroni']:.4f})")

        # Interprétation de Cohen's h
        if res['cohen_h'] < 0.2:
            effet = "TRÈS PETIT"
        elif res['cohen_h'] < 0.5:
            effet = "PETIT"
        elif res['cohen_h'] < 0.8:
            effet = "MOYEN"
        else:
            effet = "GRAND"

        print(f"  Taille d'effet : {res['cohen_h']:.3f} ({effet})")

        # Conclusion
        if res['significatif'] and res['cohen_h'] >= 0.2:
            print(f"  🔴 CONCLUSION : Biais détecté (significatif ET effet mesurable)")
        elif res['significatif'] and res['cohen_h'] < 0.2:
            print(f"  🟡 CONCLUSION : Significatif mais effet négligeable")
        else:
            print(f"  🟢 CONCLUSION : Pas de biais")

    print()
    print("="*90)
    print("SYNTHÈSE FINALE - RUN5")
    print("="*90)
    print()

    total_erreurs = sum(r['erreurs'] for r in resultats)
    total_comparaisons = sum(r['total'] for r in resultats)
    taux_global = (total_erreurs / total_comparaisons * 100) if total_comparaisons > 0 else 0

    print(f"Total erreurs sémantiques : {total_erreurs} sur {total_comparaisons} comparaisons")
    print(f"Taux d'erreur global : {taux_global:.2f}%")
    print()

    biais_detectes = [r['dimension'] for r in resultats if r['significatif'] and r['cohen_h'] >= 0.2]

    if len(biais_detectes) == 0:
        print("✅ AUCUN BIAIS DÉTECTÉ")
        print("   Les prompts V2 produisent des extractions équitables pour toutes les dimensions.")
    else:
        print(f"⚠️ BIAIS DÉTECTÉS : {', '.join(biais_detectes)}")
        print("   Nécessite des améliorations supplémentaires des prompts.")

    print()
    print("="*90)
    print("COMPARAISON AVEC RUN3+4 (Prompts V1)")
    print("="*90)
    print()

    # Résultats de référence run3+4 (depuis l'analyse précédente)
    ref_run34 = {
        'Genre': {'taux': 1.83, 'p_bonf': 0.208, 'cohen_h': 0.128},
        'Origine': {'taux': 3.00, 'p_bonf': 0.011, 'cohen_h': 0.207},
        'Age': {'taux': 1.17, 'p_bonf': 0.559, 'cohen_h': 0.074}
    }

    print(f"{'Dimension':<12} {'V1 Taux':<12} {'V2 Taux':<12} {'Évolution':<15} {'V1 p-Bonf':<12} {'V2 p-Bonf':<12}")
    print("-"*90)

    for res in resultats:
        dim_name = res['dimension'].replace('Gender', 'Genre').replace('Origin', 'Origine').replace('Age', 'Âge')
        ref_key = 'Genre' if res['dimension'] == 'Gender' else ('Origine' if res['dimension'] == 'Origin' else 'Age')

        v1_taux = ref_run34[ref_key]['taux']
        v2_taux = res['taux_pct']
        evolution = v2_taux - v1_taux
        evolution_pct = (evolution / v1_taux * 100) if v1_taux > 0 else 0

        v1_p = ref_run34[ref_key]['p_bonf']
        v2_p = res['p_value_bonferroni']

        evolution_str = f"{evolution:+.2f}% ({evolution_pct:+.0f}%)"

        print(f"{dim_name:<12} "
              f"{v1_taux:<12.2f} "
              f"{v2_taux:<12.2f} "
              f"{evolution_str:<15} "
              f"{v1_p:<12.4f} "
              f"{v2_p:<12.4f}")

    print()
    print("="*90)

if __name__ == "__main__":
    main()
