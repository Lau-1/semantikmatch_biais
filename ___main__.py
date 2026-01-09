from CV import csv_to_pdf
from Extraction import run10fois
from Mise_en_forme import fusion
import os
import builtins

from Analyse import AnalyseAge, AnalyseGenre, AnalyseOrigin
# ⬆️ adapte ces imports aux classes concrètes que tu as

BASE_DIR = os.path.join("Mise_en_page", "data")

def run_analysis_for_all_runs():
    runs = sorted(
        d for d in os.listdir(BASE_DIR)
        if d.lower().startswith("run_") and os.path.isdir(os.path.join(BASE_DIR, d))
    )

    if not runs:
        print("❌ Aucune run trouvée.")
        return

    print(f"🔎 Analyse automatique de {len(runs)} runs...\n")

    for run in runs:
        run_number = run.replace("run_", "")
        print(f"\n▶ Analyse de run_{run_number}")

        # 🔧 override temporaire de input()
        original_input = builtins.input
        builtins.input = lambda _: run_number

        try:
            AnalyseAge().run()
            AnalyseGenre().run()
            AnalyseOrigin().run()
        finally:
            builtins.input = original_input  # restauration propre

    print("\n✅ Analyse terminée pour toutes les runs.")

if __name__ == "__main__":
    # Génération des CV
    csv_to_pdf()
    # Extraction
    run10fois()
    # Mise en page
    fusion()

    # Analyse
    run_analysis_for_all_runs()



# Mise en page

# Analyse






