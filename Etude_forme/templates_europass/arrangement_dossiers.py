import os
import shutil
import re
import unicodedata

# 1. Définition des chemins
dossier_script = os.path.dirname(os.path.abspath(__file__))
dossier_source = os.path.join(dossier_script, "sortie_europass")

dossier_sortie_final = os.path.join(dossier_script, "new_cv")

def remove_accents(input_str):
    """Fonction pour retirer les accents (ex: Amélie -> Amelie)"""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def organiser_fichiers(dossier_src, dossier_dst):
    # Vérification que le dossier source existe
    if not os.path.exists(dossier_src):
        print(f"Erreur : Le dossier source '{dossier_src}' n'existe pas.")
        return

    # Création du dossier de destination global s'il n'existe pas
    if not os.path.exists(dossier_dst):
        os.makedirs(dossier_dst)
        print(f"Dossier de résultat créé : {dossier_dst}")

    # Liste tous les fichiers PDF du dossier source
    fichiers = [f for f in os.listdir(dossier_src) if f.lower().endswith('.pdf')]

    print(f"Traitement de {len(fichiers)} fichiers depuis '{os.path.basename(dossier_src)}' vers '{os.path.basename(dossier_dst)}'...")

    pattern = re.compile(r"^(.+?)\s+(.+?)\s+template(\d+)\.pdf$", re.IGNORECASE)

    for fichier in fichiers:
        match = pattern.match(fichier)

        if match:
            prenom_raw = match.group(1)
            nom_raw = match.group(2)
            numero_template = match.group(3)

            prenom_clean = remove_accents(prenom_raw).lower()
            nom_clean = remove_accents(nom_raw).lower()

            # --- Logique de nommage ---
            if prenom_clean == "thomas":
                if "legrand" in nom_clean:
                    nouveau_nom_base = "thomasl"
                elif "girard" in nom_clean:
                    nouveau_nom_base = "thomasg"
                else:
                    nouveau_nom_base = "thomas_autre"
            else:
                nouveau_nom_base = prenom_clean

            nom_final = f"{nouveau_nom_base} 1{numero_template}"

            # --- Chemins ---
            chemin_origine = os.path.join(dossier_src, fichier)

            # CHANGEMENT ICI : On utilise dossier_dst au lieu de dossier_src
            chemin_dossier_dest = os.path.join(dossier_dst, nom_final)
            chemin_fichier_dest = os.path.join(chemin_dossier_dest, f"{nom_final}.pdf")

            try:
                os.makedirs(chemin_dossier_dest, exist_ok=True)
                shutil.move(chemin_origine, chemin_fichier_dest)
                print(f"✅ OK : {nom_final}")

            except Exception as e:
                print(f"❌ Erreur sur {fichier} : {e}")

        else:
            print(f"⚠️ Ignoré : {fichier}")

organiser_fichiers(dossier_source, dossier_sortie_final)
