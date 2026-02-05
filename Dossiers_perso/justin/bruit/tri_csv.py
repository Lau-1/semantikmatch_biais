import pandas as pd
import io

# 1. LA LISTE DE NUMÉROS
liste_numeros = [
    2, 4, 9, 12, 15, 19, 21, 23, 28, 31,
    33, 37, 39, 41, 44, 45, 48, 50, 52, 56,
    59, 63, 66, 68, 72, 78, 81, 85, 89, 91,
    94, 98, 99, 102, 105, 106, 109, 111, 114, 117,
    119, 121, 125, 128, 131, 134, 139, 142, 145, 147,
    150, 153, 155, 158, 161, 165, 166, 169, 173, 176,
    179, 182, 185, 189, 193, 195, 198, 202, 204, 209,
    211, 215, 217, 220, 223, 226, 229, 231, 233, 235,
    238, 243, 244, 246, 249, 250, 253, 254, 258, 262,
    266, 268, 272, 279, 282, 288, 289, 291, 295, 297
]

df = pd.read_csv('extraction_original.csv', sep=';')

# 3. EXTRACTION DU NUMÉRO
# "CV 298" -> 298
df['id_temp'] = df['Name'].str.extract(r'(\d+)').astype(int)

# 4. FILTRAGE
df_filtered = df[df['id_temp'].isin(liste_numeros)].copy()

# 5. NETTOYAGE
df_filtered = df_filtered.drop(columns=['id_temp'])

# 6. SAUVEGARDE
df_filtered.to_csv('cv_filtres.csv', sep=';', index=False, quoting=1)

print(f"Opération terminée. {len(df_filtered)} CV conservés sur {len(df)}.")
