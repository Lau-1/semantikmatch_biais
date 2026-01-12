"""
Analyse statistique avancée avec intervalles de confiance,
puissance statistique et correction pour comparaisons multiples
"""
import json
import os
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import chi2_contingency, fisher_exact, binom


class AnalyseStatistique:
    """
    Analyse statistique robuste pour la détection de biais
    """

    def __init__(self, alpha=0.05):
        self.alpha = alpha  # Seuil de significativité

    def charger_donnees(self, run_path):
        """
        Charge les données d'une run spécifique
        """
        all_data = []

        mapping_biais = {
            "Rapport_gender": "Genre",
            "Rapport_origin": "Origine",
            "Rapport_age": "Âge"
        }

        for sous_dossier, label_biais in mapping_biais.items():
            chemin = os.path.join(run_path, sous_dossier)
            if not os.path.exists(chemin):
                continue

            for fichier in os.listdir(chemin):
                if fichier.endswith(".json"):
                    section = fichier.replace('audit_gender_', '').replace('audit_origin_', '').replace('audit_age_', '').replace('.json', '')

                    with open(os.path.join(chemin, fichier), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        for item in data:
                            item['Biais'] = label_biais
                            item['Section'] = section
                            all_data.append(item)

        return pd.DataFrame(all_data)

    def calculer_intervalle_confiance(self, nb_erreurs, nb_total, niveau=0.95):
        """
        Calcule l'intervalle de confiance binomial (méthode Wilson)
        """
        if nb_total == 0:
            return 0, 0, 0

        p = nb_erreurs / nb_total
        z = stats.norm.ppf((1 + niveau) / 2)  # 1.96 pour 95%

        denominator = 1 + z**2 / nb_total
        center = (p + z**2 / (2 * nb_total)) / denominator
        margin = z * np.sqrt((p * (1 - p) + z**2 / (4 * nb_total)) / nb_total) / denominator

        ic_inf = max(0, center - margin)
        ic_sup = min(1, center + margin)

        return p * 100, ic_inf * 100, ic_sup * 100

    def test_puissance_statistique(self, nb_total, p0, p1, alpha=0.05):
        """
        Calcule la puissance statistique du test
        p0 = taux baseline (ex: bruit de fond)
        p1 = taux alternatif (taux détecté)
        """
        from statsmodels.stats.power import zt_ind_solve_power

        effect_size = abs(p1 - p0) / np.sqrt(p0 * (1 - p0))

        try:
            power = zt_ind_solve_power(
                effect_size=effect_size,
                nobs1=nb_total,
                alpha=alpha,
                ratio=1.0,
                alternative='two-sided'
            )
            return power
        except:
            return None

    def correction_bonferroni(self, p_values):
        """
        Applique la correction de Bonferroni pour comparaisons multiples
        """
        nb_tests = len(p_values)
        alpha_corrige = self.alpha / nb_tests

        p_values_corriges = [min(p * nb_tests, 1.0) for p in p_values]

        return alpha_corrige, p_values_corriges

    def analyser_run(self, run_path, taux_bruit_fond=0.33):
        """
        Analyse complète d'une run avec statistiques avancées
        """
        print(f"\n{'='*60}")
        print(f"ANALYSE STATISTIQUE AVANCEE")
        print(f"{'='*60}\n")

        df = self.charger_donnees(run_path)

        if df.empty:
            print("[ERR] Aucune donnée disponible")
            return None

        nb_cv = df['cv_id'].nunique()
        nb_sections = df['Section'].nunique()
        nb_comparaisons = nb_cv * nb_sections

        print(f"[INFO] Données chargées :")
        print(f"   - {nb_cv} CVs")
        print(f"   - {nb_sections} sections")
        print(f"   - {nb_comparaisons} comparaisons par biais\n")

        # Analyse par biais
        resultats = []
        p_values = []

        for biais in ['Genre', 'Origine', 'Âge']:
            df_biais = df[df['Biais'] == biais]
            nb_erreurs = (df_biais['coherent'] == False).sum()

            # Taux et intervalle de confiance
            taux, ic_inf, ic_sup = self.calculer_intervalle_confiance(nb_erreurs, nb_comparaisons)

            # Test de Fisher (contre baseline avec 0 erreurs)
            table = [
                [nb_erreurs, nb_comparaisons - nb_erreurs],
                [0, nb_comparaisons]  # Baseline théorique
            ]
            odds_ratio, p_value = fisher_exact(table)
            p_values.append(p_value)

            # Calcul de l'effet (Cohen's h)
            p_observed = nb_erreurs / nb_comparaisons
            p_baseline = taux_bruit_fond / 100
            cohens_h = 2 * (np.arcsin(np.sqrt(p_observed)) - np.arcsin(np.sqrt(p_baseline)))

            # Puissance statistique
            power = self.test_puissance_statistique(nb_comparaisons, p_baseline, p_observed)

            resultats.append({
                'Biais': biais,
                'Erreurs': nb_erreurs,
                'Total': nb_comparaisons,
                'Taux (%)': round(taux, 2),
                'IC 95% inf': round(ic_inf, 2),
                'IC 95% sup': round(ic_sup, 2),
                'p-value': round(p_value, 4),
                "Cohen's h": round(cohens_h, 3),
                'Puissance': round(power, 3) if power else "N/A"
            })

        # Correction de Bonferroni
        alpha_corrige, p_values_corriges = self.correction_bonferroni(p_values)

        for i, resultat in enumerate(resultats):
            resultat['p-value (Bonferroni)'] = round(p_values_corriges[i], 4)
            resultat['Significatif (alpha=0.05)'] = "[OK]" if p_values_corriges[i] < 0.05 else "[ERR]"

        df_resultats = pd.DataFrame(resultats)

        print(f"[GRAPH] RÉSULTATS :")
        print(df_resultats.to_string(index=False))

        print(f"\n[NOTE] Notes :")
        print(f"   - IC 95% : Intervalle de confiance à 95% (méthode Wilson)")
        print(f"   - Cohen's h : Taille d'effet (0.2=petit, 0.5=moyen, 0.8=grand)")
        print(f"   - Puissance : Probabilité de détecter un vrai effet")
        print(f"   - p-value (Bonferroni) : Corrigée pour {len(p_values)} comparaisons multiples")
        print(f"   - alpha corrigé = {alpha_corrige:.4f}")

        return df_resultats

    def analyser_severite_erreurs(self, run_path):
        """
        Analyse la distribution et sévérité des types d'erreurs
        """
        df = self.charger_donnees(run_path)

        if df.empty:
            return None

        print(f"\n{'='*60}")
        print(f"[SEARCH] ANALYSE DE SÉVÉRITÉ DES ERREURS")
        print(f"{'='*60}\n")

        df_erreurs = df[df['coherent'] == False].copy()

        if df_erreurs.empty:
            print("[OK] Aucune erreur détectée")
            return None

        # Distribution par type d'erreur et biais
        pivot = pd.crosstab(
            df_erreurs['Biais'],
            df_erreurs['error_type'],
            margins=True,
            margins_name='Total'
        )

        print("[STATS] Distribution des erreurs par type :")
        print(pivot)

        # Test du Chi-2 : Les types d'erreurs sont-ils indépendants du biais ?
        if len(df_erreurs['Biais'].unique()) > 1 and len(df_erreurs['error_type'].unique()) > 1:
            contingency = pd.crosstab(df_erreurs['Biais'], df_erreurs['error_type'])
            chi2, p_val, dof, expected = chi2_contingency(contingency)

            print(f"\n[TEST] Test d'indépendance Chi-2 :")
            print(f"   - Chi2 = {chi2:.2f}, df = {dof}, p = {p_val:.4f}")
            if p_val < 0.05:
                print(f"   - [OK] Les types d'erreurs dépendent du type de biais (p < 0.05)")
            else:
                print(f"   - [ERR] Pas de dépendance significative (p >= 0.05)")

        return pivot

    def analyser_par_section(self, run_path):
        """
        Analyse les différences entre sections (experiences, studies, interests)
        """
        df = self.charger_donnees(run_path)

        if df.empty:
            return None

        print(f"\n{'='*60}")
        print(f"[INFO] ANALYSE PAR SECTION")
        print(f"{'='*60}\n")

        # Taux d'erreur par section et biais
        resultats_section = []

        for section in df['Section'].unique():
            for biais in ['Genre', 'Origine', 'Âge']:
                df_subset = df[(df['Section'] == section) & (df['Biais'] == biais)]
                nb_total = len(df_subset)
                nb_erreurs = (df_subset['coherent'] == False).sum()

                if nb_total > 0:
                    taux = (nb_erreurs / nb_total) * 100
                    resultats_section.append({
                        'Section': section,
                        'Biais': biais,
                        'Erreurs': nb_erreurs,
                        'Total': nb_total,
                        'Taux (%)': round(taux, 2)
                    })

        df_section = pd.DataFrame(resultats_section)
        pivot_section = df_section.pivot(index='Section', columns='Biais', values='Taux (%)')

        print("[STATS] Taux d'erreur (%) par section et biais :")
        print(pivot_section.round(2))

        return df_section


def main():
    """
    Exemple d'utilisation
    """
    analyseur = AnalyseStatistique(alpha=0.05)

    # Analyse de run1
    run_path = "Runs_analyse/run1"

    if not os.path.exists(run_path):
        print(f"[ERR] Run introuvable : {run_path}")
        return

    # 1. Analyse principale
    df_resultats = analyseur.analyser_run(run_path, taux_bruit_fond=0.33)

    # 2. Analyse de sévérité
    analyseur.analyser_severite_erreurs(run_path)

    # 3. Analyse par section
    analyseur.analyser_par_section(run_path)

    print(f"\n{'='*60}")
    print("[OK] ANALYSE TERMINÉE")
    print(f"{'='*60}")


if __name__ == "__main__":
    try:
        import statsmodels
        main()
    except ImportError:
        print("[ERR] Erreur : statsmodels non installé")
        print("   Installez avec : pip install statsmodels")
