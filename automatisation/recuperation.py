import os
import shutil

# Dossier contenant les PDF d'origine
source_dir = "/Users/sachabeaujean/Library/CloudStorage/OneDrive-Personnel/Documents/ENSAI/Stage/Semantikmatch/format cv 2/ilovepdf_split"

# Dossier de sortie
output_dir = "/Users/sachabeaujean/Library/CloudStorage/OneDrive-Personnel/Documents/ENSAI/Stage/Semantikmatch/format cv 2/pdf_renommes"
os.makedirs(output_dir, exist_ok=True)

# Liste des prénoms dans l'ordre
prenoms = ["clara", "hugo", "sarah", "thomasG", "ines", "louis", "amelie", "maxime", "thomasL", "camille"]

# Générer automatiquement la liste des fichiers PDF dans l'ordre numérique
pdf_files = []
for i in range(1, 101):  # de 1 à 100
    pdf_name = f"Semantik match (3)-{i}.pdf"
    pdf_files.append(os.path.join(source_dir, pdf_name))

# Vérification
if len(pdf_files) != 100:
    raise ValueError(f"❌ Il faut exactement 100 PDF (trouvé {len(pdf_files)})")

# Renommage et classement
index = 0
for prenom in prenoms:
    for i in range(1, 11):  # 10 fichiers par prénom
        pdf = pdf_files[index]
        index += 1

        new_name = f"{prenom} {i}"

        # Créer le dossier
        folder_path = os.path.join(output_dir, new_name)
        os.makedirs(folder_path, exist_ok=True)

        # Chemin de destination
        dst_path = os.path.join(folder_path, new_name + ".pdf")

        # Déplacer + renommer
        shutil.move(pdf, dst_path)

print("✅ Renommage et classement des 100 PDF terminés")
