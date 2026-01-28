import os
import shutil

# 1. Configuration des noms cibles dans l'ordre (de 1 à 10)
mapping_noms = [
    "clara 20",    # correspond à temp1-1
    "hugo 20",     # correspond à temp1-2
    "sarah 20",    # correspond à temp1-3
    "thomasg 20",  # correspond à temp1-4
    "ines 20",     # correspond à temp1-5
    "louis 20",    # correspond à temp1-6
    "amelie 20",   # correspond à temp1-7
    "maxime 20",   # correspond à temp1-8
    "thomasl 20",  # correspond à temp1-9
    "camille 20"   # correspond à temp1-10
]

# Dossier source (mettre "." si le script est au même endroit que les fichiers)
dossier_source = "."
# Nom du dossier principal de sortie
dossier_sortie_racine = "nouveaux_cv"

def organiser_fichiers():
    # Création du dossier racine s'il n'existe pas
    if not os.path.exists(dossier_sortie_racine):
        os.makedirs(dossier_sortie_racine)
        print(f"📁 Dossier créé : {dossier_sortie_racine}")

    # Boucle sur la liste des noms
    # enumerate commence à 0, donc on ajoute start=1 pour correspondre à temp1-1, temp1-2...
    for i, nouveau_nom in enumerate(mapping_noms, start=1):

        # Le nom du fichier source actuel (ex: temp2-1.pdf)
        nom_source = f"temp6-{i}.pdf"
        chemin_source = os.path.join(dossier_source, nom_source)

        # Vérification si le fichier source existe bien
        if os.path.exists(chemin_source):
            # Création du sous-dossier spécifique (ex: nouveaux_cv/clara 16)
            chemin_sous_dossier = os.path.join(dossier_sortie_racine, nouveau_nom)
            os.makedirs(chemin_sous_dossier, exist_ok=True)

            # Définition du chemin final (ex: nouveaux_cv/clara 15/clara 15.pdf)
            chemin_destination = os.path.join(chemin_sous_dossier, f"{nouveau_nom}.pdf")

            # Copie et renommage du fichier
            shutil.copy2(chemin_source, chemin_destination)
            print(f"✅ Succès : {nom_source} -> {chemin_destination}")

        else:
            print(f"⚠️ Attention : Le fichier source '{nom_source}' est introuvable.")

if __name__ == "__main__":
    organiser_fichiers()
    print("\n--- Opération terminée ---")
