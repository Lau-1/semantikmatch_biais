"""
Script principal pour lancer l'analyse complète des biais avec toutes les améliorations
"""
import os
import sys

# Configuration de l'encodage pour Windows
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

def banner(texte):
    """Affiche un banner décoratif"""
    largeur = 60
    try:
        print("\n" + "=" * largeur)
        print(texte.center(largeur))
        print("=" * largeur + "\n")
    except UnicodeEncodeError:
        # Fallback sans emojis pour les terminaux qui ne les supportent pas
        texte_simple = texte.encode('ascii', 'ignore').decode('ascii')
        print("\n" + "=" * largeur)
        print(texte_simple.center(largeur))
        print("=" * largeur + "\n")

def main():
    banner("🔬 ANALYSE COMPLÈTE DES BIAIS LLM")

    print("Ce script lance une analyse complète en 4 étapes :\n")
    print("1. 📊 Baseline A/A (mesure du bruit de fond)")
    print("2. 📈 Statistiques avancées (IC, puissance, Bonferroni)")
    print("3. 🔍 Analyse de sévérité et par section")
    print("4. 🧑‍⚖️ [OPTIONNEL] Validation humaine\n")

    reponse = input("Voulez-vous continuer ? [O/n] : ").strip().lower()
    if reponse == 'n':
        print("❌ Annulé")
        return

    # Vérification des dépendances
    banner("📦 Vérification des dépendances")
    try:
        import statsmodels
        import sklearn
        import tqdm
        print("✅ Toutes les dépendances sont installées")
    except ImportError as e:
        print(f"❌ Dépendance manquante : {e}")
        print("\n📥 Installez les dépendances avec :")
        print("   pip install -r requirements.txt")
        return

    # Déterminer le répertoire racine du projet
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Remonter d'un niveau depuis Analyse/

    # Chemins corrigés
    runs_analyse_path = os.path.join(project_root, "Runs_analyse", "run3")
    runs_jointure_path = os.path.join(project_root, "Runs_jointure")

    print(f"📁 Répertoire du projet : {project_root}")
    print(f"📁 Cherche run1 dans : {runs_analyse_path}\n")

    # Vérification de la structure des dossiers
    if not os.path.exists(runs_analyse_path):
        print(f"❌ Erreur : Le dossier {runs_analyse_path} est introuvable")
        print("   Assurez-vous d'avoir exécuté les analyses de base")
        print("\n💡 Suggestions :")
        print("   1. Vérifiez que le dossier Runs_analyse/run1 existe à la racine du projet")
        print("   2. Exécutez d'abord : python Analyse/analyser_tout.py")
        return

    # ============================
    # ÉTAPE 1 : BASELINE A/A
    # ============================
    banner("📊 ÉTAPE 1/4 : BASELINE A/A")
    print("Mesure du bruit de fond du système...")

    try:
        from baseline_aa import BaselineAA

        baseline = BaselineAA(nb_repetitions=10)
        taux_bruit = baseline.mesurer_bruit_fond(
            input_root=runs_jointure_path,
            output_root=os.path.join(project_root, "Runs_analyse")
        )

        if taux_bruit is None:
            taux_bruit = 0.33  # Valeur par défaut
            print(f"⚠️ Utilisation du taux par défaut : {taux_bruit}%")
        else:
            print(f"\n✅ Taux de bruit mesuré : {taux_bruit:.2f}%")

    except Exception as e:
        print(f"❌ Erreur lors de la baseline A/A : {e}")
        taux_bruit = 0.33
        print(f"⚠️ Utilisation du taux par défaut : {taux_bruit}%")

    input("\nAppuyez sur Entrée pour continuer...")

    # ============================
    # ÉTAPE 2 : STATISTIQUES AVANCÉES
    # ============================
    banner("📈 ÉTAPE 2/4 : STATISTIQUES AVANCÉES")
    print("Calcul des intervalles de confiance, puissance statistique, etc.")

    try:
        from statistiques_avancees import AnalyseStatistique

        analyseur = AnalyseStatistique(alpha=0.05)
        df_resultats = analyseur.analyser_run(runs_analyse_path, taux_bruit_fond=taux_bruit)

        if df_resultats is not None:
            print("\n✅ Analyse statistique terminée")
        else:
            print("❌ Échec de l'analyse statistique")

    except Exception as e:
        print(f"❌ Erreur lors de l'analyse statistique : {e}")
        import traceback
        traceback.print_exc()

    input("\nAppuyez sur Entrée pour continuer...")

    # ============================
    # ÉTAPE 3 : ANALYSE DE SÉVÉRITÉ
    # ============================
    banner("🔍 ÉTAPE 3/4 : ANALYSE DE SÉVÉRITÉ")
    print("Distribution des types d'erreurs et analyse par section...")

    try:
        analyseur.analyser_severite_erreurs(runs_analyse_path)
        analyseur.analyser_par_section(runs_analyse_path)
        print("\n✅ Analyse de sévérité terminée")
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse de sévérité : {e}")

    input("\nAppuyez sur Entrée pour continuer...")

    # ============================
    # ÉTAPE 4 : VALIDATION HUMAINE (OPTIONNELLE)
    # ============================
    banner("🧑‍⚖️ ÉTAPE 4/4 : VALIDATION HUMAINE")
    print("Cette étape nécessite une annotation manuelle.")
    print("Elle permet de créer un gold standard et mesurer l'accord humain-LLM.\n")

    reponse = input("Voulez-vous lancer la validation humaine ? [o/N] : ").strip().lower()

    if reponse == 'o':
        try:
            from validation_humaine import ValidationHumaine

            print("\n⚠️ Cette étape va vous demander d'annoter manuellement ~30 comparaisons")
            print("   Temps estimé : 15-30 minutes\n")

            reponse2 = input("Confirmer ? [o/N] : ").strip().lower()

            if reponse2 == 'o':
                validateur = ValidationHumaine(taille_echantillon=30)
                echantillon = validateur.selectionner_echantillon(
                    input_root=runs_jointure_path,
                    run_number="run1"
                )

                if echantillon:
                    annotations = validateur.interface_annotation(echantillon)

                    if annotations:
                        output_dir = os.path.join(project_root, "Analyse", "validation_humaine")
                        validateur.sauvegarder_annotations(output_dir)
                        print("\n✅ Validation humaine terminée")
                    else:
                        print("\n⚠️ Aucune annotation créée")
                else:
                    print("\n❌ Échec de la sélection de l'échantillon")
            else:
                print("⏭️ Étape ignorée")

        except Exception as e:
            print(f"❌ Erreur lors de la validation humaine : {e}")
    else:
        print("⏭️ Étape ignorée")

    # ============================
    # RÉSUMÉ FINAL
    # ============================
    banner("✅ ANALYSE COMPLÈTE TERMINÉE")

    print("📋 Résumé des fichiers générés :\n")
    print(f"   1. {os.path.join(project_root, 'Runs_analyse', 'baseline_aa', 'rapport_aa.json')}")
    print("   2. Résultats statistiques affichés dans la console")
    print(f"   3. [Si validé] {os.path.join(project_root, 'Analyse', 'validation_humaine', 'annotations_*.json')}\n")

    print("📊 Prochaines étapes recommandées :\n")
    print("   1. Consulter le fichier RECOMMANDATIONS_AMELIORATION.md")
    print("   2. Compléter les runs 2-5 pour améliorer la reproductibilité")
    print("   3. Si taux de bruit > 2% : Investiguer la cause")
    print("   4. Si biais significatif : Analyser les patterns d'erreurs")
    print("   5. Mettre en place un monitoring continu\n")

    print("📚 Documentation complète : RECOMMANDATIONS_AMELIORATION.md")
    print("\n🎉 Merci d'avoir utilisé le système d'analyse des biais !")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Analyse interrompue par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur fatale : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
