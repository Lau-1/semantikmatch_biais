# semantikmatch_biais
## **Lancer l'application**

Sur Oxyxia (ou SSPCloud) : lancer VScode

### ** Cloner le projet dans Datalab (VSCode-python).**

```python
git clone https://github.com/Lau-1/semantikmatch_biais.git
````
### **Configurer l'environnement.**

 Dans la racine, créer un fichier .env et copier les lignes suivantes :

```python 
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```
Et téléchargement des librairies
```python
pip install -r requirements.txt
```
### **Fonctionnement des codes**

1. Obtention des CV au format PDF
```python
cv/csv_to_pdf.py
```
Fichier entrée : cv/data/cv.csv
Dossier sortie : cv/data/CV_Generes

2. Extraction des CV
```python
extract_experiences_with_llm.py
extract_interests_with_llm.py
extract_studies_with_llm.py
```
Ou passer par semantikmatch interface
Dossier entrée : cv/data/CV_Generes
Dossier sortie : "json/data/run_3/jointure/interests.json",
                 "json/data/run_3/jointure/experiences.json",
                 "json/data/run_3/jointure/studies.json"

3. Analyse binaire des différences 
```python
new/analyseage.py
new/analysegenre.py
new/analyseorigin.py
```
Dossier entrée : "json/data/run_3/jointure/interests.json",
                 "json/data/run_3/jointure/experiences.json",
                 "json/data/run_3/jointure/studies.json"
Dossier sortie : "rapports_age"
                 "rapports_genre"
                 "rapports_origin"

4. Analyse finale 
```python
analyse_rapport.ipynb
```
