import json

def transformer_noms_cv(fichier_entree, fichier_sortie):
    try:
        # 1. Charger le fichier JSON original
        with open(fichier_entree, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 2. Créer un nouveau dictionnaire avec les clés modifiées
        # On remplace "CV 297 Original" par "CV 297" ou "CV297" selon votre préférence
        # Ici, j'enlève " Original" et je supprime l'espace pour avoir "CVXXX"
        data_modifiee = {
            cle.replace(" Original", "").replace(" ", ""): valeur
            for cle, valeur in data.items()
        }

        # 3. Sauvegarder le nouveau fichier JSON
        with open(fichier_sortie, 'w', encoding='utf-8') as f:
            json.dump(data_modifiee, f, indent=4, ensure_ascii=False)

        print(f"Succès ! Le fichier a été transformé et enregistré sous : {fichier_sortie}")

    except FileNotFoundError:
        print("Erreur : Le fichier 'cv_ref.json' est introuvable.")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")

# Appel de la fonction
transformer_noms_cv('cv_ref.json', 'cv_ref_clean.json')
