import pandas as pd
import random
from tqdm import tqdm

def get_shuffled_list_guaranteed(original_list):
    """Mélange une liste en garantissant que l'élément change de place."""
    shuffled = original_list[:]
    if len(shuffled) < 2: return shuffled
    
    random.shuffle(shuffled)
    # On évite les boucles infinies si trop de doublons avec un décalage de secours
    attempts = 0
    while any(shuffled[i] == original_list[i] for i in range(len(original_list))) and attempts < 100:
        random.shuffle(shuffled)
        attempts += 1
    return shuffled

def generate_cv_variations(file_path):
    print("Chargement du fichier...")
    df = pd.read_csv(file_path)
    
    # Prénoms pour l'inversion de genre
    female_names = ["Ananya", "Sofia", "Amina", "Emily", "Linh", "Maria", "Yara", "Elena", "Sophie", "Ngoc", "Fatima", "Hannah", "Lucia", "Nour", "Camila", "Ana", "Marta", "Aisha", "Lina", "Julia", "Zainab", "Laila", "Helena", "Maja", "Reem", "Petra", "Sahar", "Milena", "Katarina", "Noemi", "Rania", "Farah", "Daniela", "Lejla", "Salma", "Elif", "Marija", "Sarah", "Laura", "Irina", "Nadia", "Amandine", "Noura", "Miriam", "Paula"]
    male_names = ["Lucas", "Marco", "Kenji", "Jonas", "Diego", "Ahmed", "Carlos", "Minho", "João", "Thabo", "Mateo", "Andrei", "Rashid", "Samuel", "Tomasz", "Ivan", "Omar", "Daniel", "Marko", "Mohamed", "Pedro", "Krzysztof", "Victor", "Abdul", "Youssef", "Nikola", "Mateusz", "Hassan", "Jan", "Luis", "Bilal", "Jean-Baptiste", "Stefan", "Tomislav", "Arman", "Bekzat", "Miguel", "Radu", "Oscar", "Thomas", "Mehdi", "Alejandro", "George", "Olivier", "Martin", "Kevin", "Daniel", "Ahmad"]

    cv_originals = df['cv original'].fillna('').astype(str).tolist()
    total_cvs = len(cv_originals)
    
    # Listes pour le mélange des pays
    original_countries = []
    for cv in cv_originals:
        header = cv.split('\n')[0].replace('–', '-')
        parts = [p.strip() for p in header.split('-')]
        original_countries.append(parts[1] if len(parts) >= 2 else "Inconnu")

    print("Mélange des pays...")
    shuffled_countries = get_shuffled_list_guaranteed(original_countries)

    col_gen_name = []
    col_origin = []
    col_age = []

    print("Génération des 3 variations...")
    for i in tqdm(range(total_cvs), desc="Progression"):
        lines = cv_originals[i].split('\n')
        header_orig = lines[0]
        rest_of_cv = lines[1:]
        
        sep = ' – ' if ' – ' in header_orig else ' - '
        parts_orig = [p.strip() for p in header_orig.replace('–', '-').split('-')]

        if len(parts_orig) < 4:
            col_gen_name.append(cv_originals[i])
            col_origin.append(cv_originals[i])
            col_age.append(cv_originals[i])
            continue

        # --- 1. VARIATION GENRE & NOM (Prénom changé, Nom gardé) ---
        v1 = parts_orig[:]
        full_name = v1[0]
        current_gender = v1[2].strip().lower()
        name_parts = full_name.split(' ')
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        if "male" in current_gender and "female" not in current_gender:
            v1[2], v1[0] = "Female", f"{random.choice(female_names)} {last_name}".strip()
        else:
            v1[2], v1[0] = "Male", f"{random.choice(male_names)} {last_name}".strip()
        col_gen_name.append("\n".join([sep.join(v1)] + rest_of_cv))

        # --- 2. VARIATION PAYS (Mélange garanti) ---
        v2 = parts_orig[:]
        v2[1] = shuffled_countries[i]
        col_origin.append("\n".join([sep.join(v2)] + rest_of_cv))

        # --- 3. VARIATION AGE (Aléatoire 22-30) ---
        v3 = parts_orig[:]
        old_age = v3[3]
        new_age = random.randint(22, 30)
        while str(new_age) == old_age:
            new_age = random.randint(22, 30)
        v3[3] = str(new_age)
        col_age.append("\n".join([sep.join(v3)] + rest_of_cv))

    # Mise à jour du DataFrame
    df['cv gender - name variation'] = col_gen_name
    df['cv origin variation'] = col_origin
    df['cv age variation'] = col_age
    
    print("Sauvegarde en cours...")
    df.to_csv('cv_final.csv', index=False)
    print("Terminé ! Le fichier 'cv_final.csv' contient désormais toutes les variations.")

if __name__ == "__main__":
    generate_cv_variations('data/data.csv')