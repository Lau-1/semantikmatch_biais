"""
Analyse comparative de tous les runs disponibles
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

# Configuration encodage Windows
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except:
        pass

# Imports locaux
from statistiques_avancees import AnalyseStatistique

def analyser_tous_les_runs(project_root=None):
    """
    Analyse tous les runs disponibles et compare les résultats
    """
    if project_root is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)

    runs_analyse_dir = os.path.join(project_root, "Runs_analyse")

    print("="*70)
    print("ANALYSE COMPARATIVE DE TOUS LES RUNS".center(70))
    print("="*70)

    # Détecter tous les runs disponibles
    runs_disponibles = []
    for item in os.listdir(runs_analyse_dir):
        item_path = os.path.join(runs_analyse_dir, item)
        if os.path.isdir(item_path) and item.startswith("run"):
            # Vérifier que le run contient des données
            sous_dossiers = os.listdir(item_path)
            if any('Rapport_' in s for s in sous_dossiers):
                runs_disponibles.append(item)

    runs_disponibles.sort()

    # Filtrer uniquement run3 et run4 (mêmes prompts d'extraction)
    runs_disponibles = [r for r in runs_disponibles if r in ['run3', 'run4']]

    if not runs_disponibles:
        print("[ERR] Aucun run valide trouve")
        return None

    print(f"\n[INFO] {len(runs_disponibles)} runs valides detectes : {', '.join(runs_disponibles)}\n")

    # Analyser chaque run
    analyseur = AnalyseStatistique(alpha=0.05)
    tous_resultats = []

    for run_name in runs_disponibles:
        print("\n" + "="*70)
        print(f"ANALYSE DE {run_name.upper()}".center(70))
        print("="*70)

        run_path = os.path.join(runs_analyse_dir, run_name)

        try:
            # Analyse avec taux de bruit par défaut (à ajuster si baseline A/A mesurée)
            df_resultats = analyseur.analyser_run(run_path, taux_bruit_fond=0.5)

            if df_resultats is not None:
                # Ajouter la colonne run
                df_resultats['Run'] = run_name
                tous_resultats.append(df_resultats)

                print(f"\n[OK] {run_name} analyse avec succes")
            else:
                print(f"[WARN] {run_name} : donnees vides")

        except Exception as e:
            print(f"[ERR] Erreur sur {run_name} : {e}")
            import traceback
            traceback.print_exc()

        print("\n" + "-"*70)

    if not tous_resultats:
        print("\n[ERR] Aucun resultat disponible")
        return None

    # Consolider tous les résultats
    df_complet = pd.concat(tous_resultats, ignore_index=True)

    # Analyse comparative
    print("\n" + "="*70)
    print("SYNTHESE COMPARATIVE".center(70))
    print("="*70)

    # 1. Taux d'erreur moyen par biais (tous runs confondus)
    print("\n[STATS] 1. TAUX D'ERREUR MOYEN PAR BIAIS")
    print("-"*70)

    stats_globales = df_complet.groupby('Biais').agg({
        'Taux (%)': ['mean', 'std', 'min', 'max'],
        'p-value (Bonferroni)': 'mean',
        "Cohen's h": 'mean'
    }).round(3)

    print(stats_globales)

    # 2. Reproductibilité : Combien de runs montrent un biais significatif ?
    print("\n[STATS] 2. REPRODUCTIBILITE DES BIAIS")
    print("-"*70)

    for biais in df_complet['Biais'].unique():
        df_biais = df_complet[df_complet['Biais'] == biais]
        nb_significatif = (df_biais['p-value (Bonferroni)'] < 0.05).sum()
        nb_total = len(df_biais)

        print(f"\n{biais} :")
        print(f"  - Significatif sur {nb_significatif}/{nb_total} runs ({nb_significatif/nb_total*100:.1f}%)")
        print(f"  - Taux moyen : {df_biais['Taux (%)'].mean():.2f}% (± {df_biais['Taux (%)'].std():.2f}%)")
        print(f"  - Cohen's h moyen : {df_biais['Cohen\'s h'].mean():.3f}")

        if nb_significatif >= nb_total * 0.5:
            print(f"  - [WARN] Biais reproductible detecte")
        else:
            print(f"  - [OK] Pas de biais reproductible")

    # 3. Tableau récapitulatif pivot
    print("\n[STATS] 3. TABLEAU RECAPITULATIF (Taux %)")
    print("-"*70)

    pivot_taux = df_complet.pivot(index='Run', columns='Biais', values='Taux (%)').round(2)
    print(pivot_taux)

    # 4. Graphique comparatif
    print("\n[GRAPH] 4. GENERATION DU GRAPHIQUE COMPARATIF...")

    try:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Graphique 1 : Evolution des taux par run
        pivot_taux.plot(kind='line', marker='o', ax=axes[0], linewidth=2)
        axes[0].set_title('Evolution des taux d\'erreur par run', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Taux d\'erreur (%)')
        axes[0].set_xlabel('Run')
        axes[0].legend(title='Biais')
        axes[0].grid(True, alpha=0.3)
        axes[0].axhline(y=2, color='red', linestyle='--', alpha=0.5, label='Seuil 2%')

        # Graphique 2 : Boxplot des distributions
        df_melted = df_complet[['Biais', 'Taux (%)']].copy()
        df_melted.boxplot(by='Biais', ax=axes[1], patch_artist=True)
        axes[1].set_title('Distribution des taux d\'erreur par biais', fontsize=14, fontweight='bold')
        axes[1].set_ylabel('Taux d\'erreur (%)')
        axes[1].set_xlabel('Biais')
        plt.suptitle('')  # Supprimer le titre automatique

        plt.tight_layout()

        # Sauvegarder
        output_path = os.path.join(project_root, "Analyse", "comparaison_runs.png")
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"[OK] Graphique sauvegarde : {output_path}")

        # Afficher seulement si pas en mode batch
        # plt.show()

    except Exception as e:
        print(f"[WARN] Erreur lors de la generation du graphique : {e}")

    # 5. Sauvegarde CSV
    output_csv = os.path.join(project_root, "Analyse", "synthese_tous_runs.csv")
    df_complet.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\n[OK] Synthese sauvegardee : {output_csv}")

    # 6. Conclusion
    print("\n" + "="*70)
    print("CONCLUSION".center(70))
    print("="*70)

    taux_moyens = df_complet.groupby('Biais')['Taux (%)'].mean()
    cohens_h_moyens = df_complet.groupby('Biais')["Cohen's h"].mean()

    print("\nRESUME FINAL :")
    for biais in taux_moyens.index:
        taux_moy = taux_moyens[biais]
        cohen = cohens_h_moyens[biais]
        nb_runs_sig = (df_complet[df_complet['Biais'] == biais]['p-value (Bonferroni)'] < 0.05).sum()
        nb_runs_total = len(df_complet[df_complet['Biais'] == biais])

        print(f"\n{biais} :")
        print(f"  Taux moyen : {taux_moy:.2f}%")
        print(f"  Cohen's h : {cohen:.3f} ({'tres petit' if cohen < 0.2 else 'petit' if cohen < 0.5 else 'moyen'})")
        print(f"  Reproductibilite : {nb_runs_sig}/{nb_runs_total} runs significatifs")

        if taux_moy < 2.0 and cohen < 0.2:
            print(f"  ==> [OK] PAS DE BIAIS DETECTE (taux faible, petit effet)")
        elif nb_runs_sig < nb_runs_total * 0.5:
            print(f"  ==> [OK] BIAIS NON REPRODUCTIBLE (significatif sur < 50% des runs)")
        else:
            print(f"  ==> [WARN] BIAIS POSSIBLE (a investiguer)")

    print("\n" + "="*70)

    return df_complet


if __name__ == "__main__":
    print("\n[START] Lancement de l'analyse comparative de tous les runs...\n")

    try:
        df_resultats = analyser_tous_les_runs()

        if df_resultats is not None:
            print("\n[SUCCESS] Analyse terminee avec succes !")
            print("\nFichiers generes :")
            print("  - Analyse/synthese_tous_runs.csv")
            print("  - Analyse/comparaison_runs.png")
        else:
            print("\n[ERR] Echec de l'analyse")
            sys.exit(1)

    except Exception as e:
        print(f"\n[ERR] Erreur fatale : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
