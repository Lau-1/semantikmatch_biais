import subprocess
import sys
import time

scripts_to_run = ["Extraction/extract_experiences_with_llm.py", "Extraction/extract_interests_with_llm.py", "Extraction/extract_studies_with_llm.py"]
iterations = 10

print(f"Démarrage OPTIMISÉ (Parallèle) : {iterations} itérations.")
global_start = time.time()

for i in range(1, iterations + 1):
    iter_start = time.time()
    print(f"\n ITÉRATION {i} / {iterations}")
    print(f"   Lancement simultané de : {', '.join(scripts_to_run)}...")

    processes = []

    # 1. Lancer tous les scripts en arrière-plan
    for script in scripts_to_run:
        p = subprocess.Popen([sys.executable, script])
        processes.append((script, p))

    # 2. Attendre qu'ils finissent tous
    for script_name, process in processes:
        exit_code = process.wait()
        if exit_code == 0:
            print(f"   ✅ {script_name} terminé.")
        else:
            print(f"   ❌ {script_name} a échoué (code {exit_code}).")

    iter_duration = time.time() - iter_start
    print(f"Itération {i} terminée en {round(iter_duration)} secondes.")

total_duration = time.time() - global_start
print(f"\Terminé en {round(total_duration / 60, 1)} minutes.")
