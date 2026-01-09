import os
import sys

try:
    from analyseage import AnalyseAge
    from analysegenre import AnalyseGenre
    from analyseorigin import AnalyseOrigin
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Ensure analyseage.py, analysegenre.py, and analyseorigin.py are in the current directory.")
    sys.exit(1)

def run_global_analysis():
    # Define input and output directories once
    input_dir = "Runs_jointure"
    output_dir = "Runs_analyse"

    # Instantiate all analyzers
    analyzers = [
        AnalyseAge(),
        AnalyseGenre(),
        AnalyseOrigin()
    ]

    print(f"🚀 STARTING GLOBAL ANALYSIS ({len(analyzers)} BIAS TYPES)")

    for analyzer in analyzers:
        try:
            analyzer.process_all_runs(
                input_root=input_dir,
                output_root=output_dir
            )
        except Exception as e:
            print(f"❌ Critical Error running {analyzer.biais_name}: {e}")

    print("🏁 ALL ANALYSES COMPLETED")

if __name__ == "__main__":
    run_global_analysis()
