# semantikmatch_biais
## **Lancer l'application**

Sur Oxyxia (ou SSPCloud) : lancer VScode

### ** Cloner le projet dans Datalab (VSCode-python).**

```python
git clone https://github.com/Lau-1/semantikmatch_biais.git
```
### **Configurer l'environnement.**

 Dans la racine, créer un fichier .env et copier les lignes suivantes :

```python
OPENAI_API_KEY="sk-xxxxx"

AZURE_AI_ENDPOINT="https://openai-semantik.openai.azure.com/"
AZURE_AI_KEY="xxxx"

OPENAI_API_VERSION="2024-05-01-preview"

AZURE_DEPLOYMENT_NAME="gpt-4o"

```
Et téléchargement des librairies
```python
pip install -r requirements.txt
```

### **Fonctionnement Analyse Biais Format**

1. Extraire les données via l'extraction Semantikmatch, copier le contenu de with criteria et le coller dans un fichier nommé "input.json" dans le dossier "Audit forme"

2. Mise en forme données
Lancer
```python
Analyse_forme_CV/extract_data_v2.py
```
Dossier entrée : "Analyse_forme_CV/Audit_forme/input.json"\
Dossier sortie : "Analyse_forme_CV/Audit_forme/output.json"

3. Analyse
```python
Analyse_forme_CV/analyseforme.py
```
Dossier entrée : "Analyse_forme_CV/Audit_forme/output.json"\
                 "Analyse_forme_CV/Audit_forme/real_cv.json"\
Dossier sortie : "Analyse_forme_CV/Audit_forme/rapport_analyse.json"

4. Synthèse
```python
Analyse_forme_CV/synthese_erreurs.py
```
Dossier entrée : "Analyse_forme_CV/Audit_forme/rapport_analyse.json"\
Dossier sortie : "Analyse_forme_CV/Audit_forme/audit_personnes.csv"\
                 "Analyse_forme_CV/Audit_forme/audit_formats.csv"


Pour refaire des runs, mettre les fichiers que l'on ne veut pas supprimer dans le dossier run_X

5. Synthèse toutes les runs d'une étude
```python
Analyse_forme_CV/synthese_multi_runs.py
```
Dossier entrée : "Analyse_forme_CV/Audit_forme/runs"\
Fichier sortie : "Analyse_forme_CV/Audit_forme/synthese_personnes.csv"\
                 "Analyse_forme_CV/Audit_forme/synthese_formats.csv"


Pour faire une étude sans supprimer la précédente, mettre les fichier dans un dossier Audit forme X et vider le dossier Audit_forme avec un nouveau (ou pas) real_cv.json


### **Fonctionnement Analyse Biais Genre/Age/Origine**

1. Obtention des CV au format PDF
```python
CV/csv_to_pdf.py
```
Fichier entrée : CV/data/cv.csv
Dossier sortie : CV/data/CV_Generes

2. Extraction des CV
```python
Extraction/extract_experiences_with_llm.py
Extraction/extract_interests_with_llm.py
Extraction/extract_studies_with_llm.py
```
Ou passer par semantikmatch interface
Dossier entrée : CV/data/CV_Generes
Dossier sortie : "Extraction/data/run_X/age_interests.json",
                 "Extraction/data/run_X/age_experiences.json",
                 "Extraction/data/run_X/age_studies.json"
                 "Extraction/data/run_X/original_interests.json",
                 ...  12 fichiers


3. Mise en forme
```python
Mise_en_forme/fusion.py
```

4. Analyse binaire des différences
```python
Analyse/analyseage.py
Analyse/analysegenre.py
Analyse/analyseorigin.py
```
Dossier entrée : "Extraction/data/run_X/interests.json",
                 "Extraction/data/run_X/experiences.json",
                 "Extraction/data/run_X/studies.json"
Dossier sortie : "Analyse/data/run_X/?",
                 "Analyse/data/run_X/?",
                 "Analyse/data/run_X/?.json"

4. Analyse finale
! Modifier : # Utilisation
df_run3 = charger_rapport_run3('data/run_3/rapport') en fonction de la run choisie
```python
analyse_rapport.ipynb
```



                 
