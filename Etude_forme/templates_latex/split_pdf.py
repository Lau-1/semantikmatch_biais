import os
import sys
from PyPDF2 import PdfReader, PdfWriter

# ================= CONFIGURATION AUTOMATIQUE =================
dossier_script = os.path.dirname(os.path.abspath(__file__))

DOSSIER_SOURCE = os.path.join(dossier_script, "temps")
# =============================================================

def traiter_cvs():
    print(f"Recherche des fichiers dans : {DOSSIER_SOURCE}")

    # Vérification que le dossier 'temps' existe bien
    if not os.path.exists(DOSSIER_SOURCE):
        print(f"Erreur : Le dossier 'temps' est introuvable ici : {DOSSIER_SOURCE}")
        return

    # Liste des prénoms dans l'ordre des pages (Page 1 à 10)
    noms = [
        "clara", "hugo", "sarah", "thomasg", "ines",
        "louis", "amelie", "maxime", "thomasl", "camille"
    ]

    # Le dossier 'cv_new' sera créé à l'intérieur de 'temps'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "cv_new")
    os.makedirs(output_dir, exist_ok=True)

    # Création du dossier racine s'il n'existe pas
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Dossier de sortie créé : {output_dir}")

    # Boucle sur les 6 fichiers (temp1 à temp6)
    for i in range(1, 7):
        nom_fichier_source = f"temp{i}.pdf"
        chemin_fichier_source = os.path.join(DOSSIER_SOURCE, nom_fichier_source)

        # Vérification de l'existence du fichier source
        if not os.path.exists(chemin_fichier_source):
            print(f"Attention : Le fichier {nom_fichier_source} est introuvable dans 'temps'. Ignoré.")
            continue

        # Calcul du numéro de suffixe (temp1 -> 15, temp2 -> 16, etc.)
        numero_suffixe = i + 14

        try:
            reader = PdfReader(chemin_fichier_source)
            nb_pages = len(reader.pages)

            # Boucle sur les pages (jusqu'à 10 max)
            for page_index in range(min(10, nb_pages)):
                # Construction du nom (ex: "clara 15")
                nom_base = f"{noms[page_index]} {numero_suffixe}"

                # Création du sous-dossier individuel (ex: temps/cv_new/clara 15)
                dossier_individuel = os.path.join(output_dir, nom_base)
                os.makedirs(dossier_individuel, exist_ok=True)

                # Chemin final du fichier PDF
                chemin_sortie_pdf = os.path.join(dossier_individuel, f"{nom_base}.pdf")

                # Extraction et écriture
                writer = PdfWriter()
                writer.add_page(reader.pages[page_index])

                with open(chemin_sortie_pdf, "wb") as f_out:
                    writer.write(f_out)

            print(f"OK : {nom_fichier_source} traité (suffixe {numero_suffixe})")

        except Exception as e:
            print(f"Erreur sur {nom_fichier_source} : {e}")

    print(f"\nTerminé. Vos fichiers sont dans : {output_dir}")

if __name__ == "__main__":
    traiter_cvs()
