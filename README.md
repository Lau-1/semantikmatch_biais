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
Dossier Etude_forme

1. Extraire les données via l'extraction Semantikmatch, copier le contenu de with criteria et le coller dans un fichier nommé "input.json" ou "input.csv" dans le dossier "Audit forme" (selon le format du fichier)

2. Mise en forme données
Lancer si le fichier extrait est un json
```python
Etude_forme/Analyse_forme_CV/extract_data_v2.py
```
Dossier entrée : "Etude_forme/Analyse_forme_CV/Audit_forme/input.json"
Dossier sortie : "Etude_forme/Analyse_forme_CV/Audit_forme/output.json"

Lancer si le fichier extrait est un csv
```python
Etude_forme/Analyse_forme_CV/extract_data_v3.py
```
Dossier entrée : "Etude_forme/Analyse_forme_CV/Audit_forme/input.csv"
Dossier sortie : "Etude_forme/Analyse_forme_CV/Audit_forme/output.json"


3. Analyse
```python
Etude_forme/Analyse_forme_CV/analyseforme.py
```
Dossier entrée : "Etude_forme/Analyse_forme_CV/Audit_forme/output.json"
                 "Etude_forme/Analyse_forme_CV/Audit_forme/real_cv.json"
Dossier sortie : "Etude_forme/Analyse_forme_CV/Audit_forme/rapport_analyse.json"

4. Synthèse
```python
Etude_forme/Analyse_forme_CV/synthese_erreurs.py
```
Dossier entrée : "Etude_forme/Analyse_forme_CV/Audit_forme/rapport_analyse.json"
Dossier sortie : "Etude_forme/Analyse_forme_CV/Audit_forme/audit_personnes.csv"
                 "Etude_forme/Analyse_forme_CV/Audit_forme/audit_formats.csv"


Pour refaire des runs, mettre les fichiers que l'on ne veut pas supprimer dans le dossier run_X

5. Synthèse toutes les runs d'une étude
```python
Etude_forme/Analyse_forme_CV/synthese_multi_runs.py
```
Dossier entrée : "Etude_forme/Analyse_forme_CV/Audit_forme/runs"
Fichier sortie : "Etude_forme/Analyse_forme_CV/Audit_forme/synthese_personnes.csv"
                 "Etude_forme/Analyse_forme_CV/Audit_forme/synthese_formats.csv"


Pour faire une étude sans suprimer la précédente, mettre les fichier dans un dossier Audit forme X et vider le dossier Audit_forme avec un nouveau (ou pas) real_cv.json


### **Fonctionnement Analyse Biais Genre/Age/Origine**

1. Mix des cv
```python
mix_cv.py
```
Fichier entrée : 'CV/300cv.csv'
Fichier sortie : 'CV/cv_final.csv'

2. Obtention des CV au format PDF ou overleaf

PDF
```python
CV/csv_to_pdf.py
```
Fichier entrée : CV/data/cv.csv
Dossier sortie : CV/data/CV_Generes

OVERLEAF
```python
```
3. Extraction semantikmatch
Extraction des CV originaux et biaisés (4 lots), copier l'extration dans ??

4. Mise en forme
```python
Mise_en_forme/extract_data.py
Mise_en_forme/fusion.py
```
Dossier entrée : 
Dossier sortie : 

5. Analyse biniaire plusieurs run
```python
```
Dossier entrée : 
Dossier sortie : 

6. Analyse finale toutes runs
```python
Analyse_rapport.ipynb
```

