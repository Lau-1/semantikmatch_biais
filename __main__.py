from cv import csv_to_pdf
from Extraction.extract_experiences_with_llm import ExtractExperiencesWithLLM
from Extraction.extract_interests_with_llm import ExtractInterestsWithLLM
from Extraction.extract_studies_with_llm import ExtractStudiesWithLLM
from Extraction import run10fois
from Mise_en_forme import fusion
from Analyse.analyseage import AnalyseAge
from Analyse.analysegenre import AnalyseGenre
from Analyse.analyseorigin import AnalyseOrigin

# Génération des CV
csv_to_pdf()

# Extraction
run10fois()
