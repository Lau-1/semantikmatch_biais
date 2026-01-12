#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test pour valider les améliorations des prompts v2
Compare les extractions v1 vs v2 sur les CVs problématiques identifiés
"""
import json
import sys
import os
from pathlib import Path

# Configuration de l'encodage pour Windows
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

# Liste des CVs problématiques identifiés dans l'analyse
CVS_PROBLEMATIQUES = {
    'experiences': ['CV68', 'CV75'],
    'studies': ['CV1', 'CV10', 'CV12', 'CV17', 'CV27', 'CV82', 'CV90', 'CV95', 'CV97']
}

# Erreurs connues à vérifier
ERREURS_CONNUES = {
    'CV1': {
        'section': 'studies',
        'erreur': 'Simplification de "Bachelor of Commerce" en "Bachelor"',
        'verifier': 'level_of_degree doit contenir "Bachelor of Commerce" complet'
    },
    'CV12': {
        'section': 'studies',
        'erreur': 'Ajout de "Summer Program" au lieu de "not found"',
        'verifier': 'level_of_degree ne doit PAS contenir "Summer Program" si absent du source'
    },
    'CV17': {
        'section': 'studies',
        'erreur': 'Ajout de "Summer School" au lieu de "not found"',
        'verifier': 'level_of_degree doit être "not found" si non spécifié'
    },
    'CV27': {
        'section': 'studies',
        'erreur': 'Ajout de "Summer School" au lieu de "not found"',
        'verifier': 'level_of_degree doit être "not found" si non spécifié'
    },
    'CV68': {
        'section': 'experiences',
        'erreur': 'Troncation de "Intern - Warehouse" en "Intern"',
        'verifier': 'job title doit contenir le titre complet avec spécialisation'
    },
    'CV75': {
        'section': 'experiences',
        'erreur': 'Troncation de "Intern - Customs Broker" en "Intern"',
        'verifier': 'job title doit contenir le titre complet avec spécialisation'
    },
    'CV82': {
        'section': 'studies',
        'erreur': 'Confusion entre field et level_of_degree',
        'verifier': 'field et level_of_degree doivent être correctement séparés'
    },
    'CV90': {
        'section': 'studies',
        'erreur': 'Field "Gestion des Entreprises" placé dans level_of_degree',
        'verifier': 'field doit contenir le domaine, level_of_degree le niveau'
    },
    'CV95': {
        'section': 'studies',
        'erreur': 'Inversion field/level_of_degree',
        'verifier': '"Gestion" doit être dans field, "BTS" dans level_of_degree'
    },
    'CV97': {
        'section': 'studies',
        'erreur': 'Omission de "Professional Certificate"',
        'verifier': 'level_of_degree doit contenir "Professional Certificate"'
    },
    'CV10': {
        'section': 'studies',
        'erreur': 'Ajout de "Business Analytics" au lieu de "not found"',
        'verifier': 'field ne doit PAS contenir d\'info si absente du source'
    }
}

def charger_extraction(filepath):
    """Charge un fichier d'extraction JSON"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        print(f"⚠️ Erreur de parsing JSON dans {filepath}: {e}")
        return None

def comparer_cv(cv_id, data_v1, data_v2, section):
    """Compare les extractions v1 vs v2 pour un CV donné"""
    print(f"\n{'='*80}")
    print(f"📋 {cv_id} - Section: {section}")
    print(f"{'='*80}")

    if cv_id in ERREURS_CONNUES:
        erreur_info = ERREURS_CONNUES[cv_id]
        print(f"❌ Erreur connue (v1): {erreur_info['erreur']}")
        print(f"✅ À vérifier (v2): {erreur_info['verifier']}\n")

    # Trouver les données du CV dans v1
    pdf_name = f"{cv_id}.pdf"
    cv_v1 = data_v1.get(pdf_name, {})
    cv_v2 = data_v2.get(pdf_name, {}) if data_v2 else None

    # Afficher v1
    print("VERSION 1 (actuelle):")
    print("-" * 40)
    if section == 'experiences':
        experiences_v1 = cv_v1.get('experiences', [])
        if experiences_v1:
            for i, exp in enumerate(experiences_v1, 1):
                print(f"  Expérience {i}:")
                print(f"    Company: {exp.get('company', 'N/A')}")
                print(f"    Job title: {exp.get('job title', 'N/A')}")
                print(f"    Dates: {exp.get('dates', 'N/A')}")
        else:
            print("  (Aucune expérience extraite)")
    elif section == 'studies':
        studies_v1 = cv_v1.get('studies', [])
        if studies_v1:
            for i, study in enumerate(studies_v1, 1):
                print(f"  Étude {i}:")
                print(f"    University: {study.get('university', 'N/A')}")
                print(f"    Level: {study.get('level_of_degree', 'N/A')}")
                print(f"    Field: {study.get('field', 'N/A')}")
                print(f"    Dates: {study.get('dates', 'N/A')}")
        else:
            print("  (Aucune étude extraite)")

    # Afficher v2 si disponible
    if cv_v2:
        print("\nVERSION 2 (améliorée):")
        print("-" * 40)
        if section == 'experiences':
            experiences_v2 = cv_v2.get('experiences', [])
            if experiences_v2:
                for i, exp in enumerate(experiences_v2, 1):
                    print(f"  Expérience {i}:")
                    print(f"    Company: {exp.get('company', 'N/A')}")
                    print(f"    Job title: {exp.get('job title', 'N/A')}")
                    print(f"    Dates: {exp.get('dates', 'N/A')}")
            else:
                print("  (Aucune expérience extraite)")
        elif section == 'studies':
            studies_v2 = cv_v2.get('studies', [])
            if studies_v2:
                for i, study in enumerate(studies_v2, 1):
                    print(f"  Étude {i}:")
                    print(f"    University: {study.get('university', 'N/A')}")
                    print(f"    Level: {study.get('level_of_degree', 'N/A')}")
                    print(f"    Field: {study.get('field', 'N/A')}")
                    print(f"    Dates: {study.get('dates', 'N/A')}")
            else:
                print("  (Aucune étude extraite)")

        # Analyse des différences
        print("\n🔍 ANALYSE DES DIFFÉRENCES:")
        print("-" * 40)
        analyser_differences(cv_id, cv_v1, cv_v2, section)
    else:
        print("\n⚠️ VERSION 2 non disponible (fichier non trouvé)")

def analyser_differences(cv_id, v1, v2, section):
    """Analyse les différences entre v1 et v2"""

    if section == 'experiences':
        exp_v1 = v1.get('experiences', [])
        exp_v2 = v2.get('experiences', [])

        if len(exp_v1) != len(exp_v2):
            print(f"  ⚠️ Nombre d'expériences différent: v1={len(exp_v1)}, v2={len(exp_v2)}")

        for i, (e1, e2) in enumerate(zip(exp_v1, exp_v2), 1):
            if e1.get('job title') != e2.get('job title'):
                print(f"  ✏️ Expérience {i} - Job title modifié:")
                print(f"      v1: '{e1.get('job title')}'")
                print(f"      v2: '{e2.get('job title')}'")
                # Vérifier si c'est une correction
                if cv_id in ['CV68', 'CV75']:
                    if '-' in e2.get('job title', '') and '-' not in e1.get('job title', ''):
                        print(f"      ✅ CORRECTION: Titre complet restauré")

    elif section == 'studies':
        std_v1 = v1.get('studies', [])
        std_v2 = v2.get('studies', [])

        if len(std_v1) != len(std_v2):
            print(f"  ⚠️ Nombre d'études différent: v1={len(std_v1)}, v2={len(std_v2)}")

        for i, (s1, s2) in enumerate(zip(std_v1, std_v2), 1):
            changements = []

            if s1.get('level_of_degree') != s2.get('level_of_degree'):
                changements.append(('Level', s1.get('level_of_degree'), s2.get('level_of_degree')))

            if s1.get('field') != s2.get('field'):
                changements.append(('Field', s1.get('field'), s2.get('field')))

            if changements:
                print(f"  ✏️ Étude {i} - Modifications:")
                for field_name, val1, val2 in changements:
                    print(f"      {field_name}:")
                    print(f"        v1: '{val1}'")
                    print(f"        v2: '{val2}'")

                    # Vérifier si c'est une correction attendue
                    if cv_id == 'CV1' and field_name == 'Level':
                        if 'Commerce' in str(val2) and 'Commerce' not in str(val1):
                            print(f"        ✅ CORRECTION: Simplification évitée")

                    elif cv_id in ['CV12', 'CV17', 'CV27'] and field_name == 'Level':
                        if 'not found' in str(val2) and 'Summer' in str(val1):
                            print(f"        ✅ CORRECTION: Hallucination évitée")

                    elif cv_id == 'CV97' and field_name == 'Level':
                        if 'Certificate' in str(val2) and 'not found' in str(val1):
                            print(f"        ✅ CORRECTION: Omission corrigée")

def main():
    print("="*80)
    print("TEST DES AMÉLIORATIONS PROMPTS V2")
    print("="*80)
    print("\nCe script compare les extractions v1 (actuelles) vs v2 (améliorées)")
    print("sur les CVs où des erreurs ont été détectées.\n")

    # Chemins des fichiers
    base_dir = Path(__file__).parent

    experiences_v1 = base_dir / "experiences.json"
    experiences_v2 = base_dir / "experiences_v2.json"
    studies_v1 = base_dir / "studies.json"
    studies_v2 = base_dir / "studies_v2.json"

    # Charger les données
    print("📂 Chargement des fichiers d'extraction...")
    exp_v1_data = charger_extraction(experiences_v1)
    exp_v2_data = charger_extraction(experiences_v2)
    std_v1_data = charger_extraction(studies_v1)
    std_v2_data = charger_extraction(studies_v2)

    if not exp_v1_data or not std_v1_data:
        print("❌ Impossible de charger les fichiers v1. Vérifiez les chemins.")
        return

    print(f"✅ Fichiers v1 chargés")
    if exp_v2_data and std_v2_data:
        print(f"✅ Fichiers v2 chargés")
    else:
        print(f"⚠️ Fichiers v2 non trouvés - affichage v1 uniquement")

    # Test des experiences
    print("\n" + "="*80)
    print("SECTION: EXPERIENCES PROFESSIONNELLES")
    print("="*80)
    for cv_id in CVS_PROBLEMATIQUES['experiences']:
        comparer_cv(cv_id, exp_v1_data, exp_v2_data, 'experiences')

    # Test des studies
    print("\n" + "="*80)
    print("SECTION: ÉTUDES")
    print("="*80)
    for cv_id in CVS_PROBLEMATIQUES['studies']:
        comparer_cv(cv_id, std_v1_data, std_v2_data, 'studies')

    # Résumé
    print("\n" + "="*80)
    print("RÉSUMÉ")
    print("="*80)
    print(f"✅ CVs testés: {len(CVS_PROBLEMATIQUES['experiences']) + len(CVS_PROBLEMATIQUES['studies'])}")
    print(f"📊 Erreurs connues en v1: {len(ERREURS_CONNUES)}")

    if exp_v2_data and std_v2_data:
        print("\n✅ Les fichiers v2 sont disponibles.")
        print("   Vérifiez manuellement que les corrections attendues sont bien présentes.")
    else:
        print("\n⚠️ Lancez d'abord les scripts v2 pour générer les fichiers de comparaison:")
        print("   python extract_experiences_with_llm_v2.py")
        print("   python extract_studies_with_llm_v2.py")

if __name__ == "__main__":
    main()
