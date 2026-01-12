"""
Script de test rapide pour valider que les analyses fonctionnent
"""
import os
import sys

# Ajouter le répertoire parent au path pour les imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

print("="*60)
print("TEST RAPIDE DES STATISTIQUES AVANCEES".center(60))
print("="*60)

# Vérifier que run1 existe
runs_analyse_path = os.path.join(project_root, "Runs_analyse", "run1")

if not os.path.exists(runs_analyse_path):
    print(f"\nERREUR: Dossier introuvable : {runs_analyse_path}")
    sys.exit(1)

print(f"\nDossier trouve : {runs_analyse_path}")

# Test de l'import
try:
    from statistiques_avancees import AnalyseStatistique
    print("Import reussi: statistiques_avancees")
except ImportError as e:
    print(f"ERREUR d'import : {e}")
    sys.exit(1)

# Lancer l'analyse
print("\nLancement de l'analyse statistique avancee...")
print("-"*60)

try:
    analyseur = AnalyseStatistique(alpha=0.05)

    print("\n1. Analyse principale")
    print("-"*60)
    df_resultats = analyseur.analyser_run(runs_analyse_path, taux_bruit_fond=0.5)

    print("\n2. Analyse de severite des erreurs")
    print("-"*60)
    analyseur.analyser_severite_erreurs(runs_analyse_path)

    print("\n3. Analyse par section")
    print("-"*60)
    analyseur.analyser_par_section(runs_analyse_path)

    print("\n" + "="*60)
    print("ANALYSE TERMINEE AVEC SUCCES".center(60))
    print("="*60)

except Exception as e:
    print(f"\nERREUR lors de l'analyse : {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
