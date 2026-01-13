# Pipeline Complet - Analyse Biais LLM (Runs 5, 6, 7)

## État actuel du pipeline

### ✅ Étapes terminées :

1. **Extraction via Semantikmatch** : Fichiers dans `Extract_via_semantikmatch/run5,6,7/`
   - original.json, age.json, gender.json, origin.json

2. **Conversion au format standard** : Fichiers dans `Runs_jointure/run5,6,7/`
   - original.json, age.json, gender.json, origin.json (format standardisé)

3. **Préparation des fichiers séparés** : Fichiers dans `Runs_jointure/run5,6,7/`
   - experiences.json, studies.json, interests.json

4. **Analyses d'audit** (en cours) : Fichiers dans `Runs_analyse/run5,6,7/`
   - run6 et run7 : ✅ COMPLET (9 fichiers chacun)
   - run5 : ⏳ EN COURS (7/9 fichiers - manque Age experiences et studies)

### ⏳ Étapes en cours :

Les analyses d'audit pour run5 Age sont en cours d'exécution.

### 📋 Étapes suivantes :

5. **Attendre la fin des analyses** : Les analyses GPT-4 prennent du temps (plusieurs minutes)

6. **Lancer l'analyse statistique** :
   ```bash
   cd Abdoul
   python analyse_statistique_complete.py
   ```
   Cela générera :
   - Affichage console avec résultats détaillés
   - `resultats_statistiques_runs567.csv` avec les données

7. **Mettre à jour le rapport LaTeX** : Utiliser les nouveaux résultats statistiques

## Commandes rapides

### Vérifier l'état des analyses :
```bash
# Compter les fichiers d'audit (attendu : 27 = 9 par run × 3 runs)
find Runs_analyse/run5 Runs_analyse/run6 Runs_analyse/run7 -name "audit_*.json" | wc -l

# Vérifier run5 spécifiquement
ls -la Runs_analyse/run5/Rapport_age/
```

### Relancer une analyse si nécessaire :
```bash
cd "f:\\Semantikmath\\ETUDE_BIAIS\\semantikmatch_biais"
python Analyse/analyseorigin.py  # Pour Origin
python Analyse/analysegenre.py   # Pour Gender
python Analyse/analyseage.py     # Pour Age
```

### Lancer l'analyse statistique :
```bash
cd Abdoul
python analyse_statistique_complete.py > resultats_complets.txt
```

## Résultats attendus

D'après les analyses précédentes sur ces mêmes runs, les résultats attendus sont :

| Dimension | Erreurs | Total | Taux  | p-Bonferroni | Significatif |
|-----------|---------|-------|-------|--------------|--------------|
| Gender    | 7       | 900   | 0.78% | 0.047        | ⚠️ OUI       |
| Origin    | 8       | 900   | 0.89% | 0.023        | ⚠️ OUI       |
| Age       | 2       | 700   | 0.29% | 1.000        | ✅ NON       |
| **Total** | **17**  | **2500** | **0.68%** | - | -           |

**Interprétation** :
- Genre et Origine sont techniquement significatifs (p < 0.05)
- **MAIS** effet pratique négligeable (Cohen's h < 0.15, taux < 1%)
- Amélioration de -77% par rapport aux prompts V1
- Acceptable pour la production

## Fichiers importants

- **Scripts d'analyse** : `Analyse/analyseorigin.py`, `analysegenre.py`, `analyseage.py`
- **Analyse statistique** : `Abdoul/analyse_statistique_complete.py`
- **Résultats CSV** : `Abdoul/resultats_statistiques_runs567.csv`
- **Rapport LaTeX** : `RAPPORT_ETUDE_BIAIS_LLM.tex` (à mettre à jour)

## Notes

- Les analyses GPT-4 prennent environ 5-10 minutes par run/dimension
- Assurez-vous que le fichier `.env` contient les clés API Azure
- Les prompts V2 sont dans `Extract/extract_*_with_llm_v2.py`
