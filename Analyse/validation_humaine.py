"""
Outil de validation humaine pour créer un gold standard
Permet d'auditer manuellement un échantillon de comparaisons
"""
import json
import os
import random
from datetime import datetime

class ValidationHumaine:
    """
    Interface console pour validation manuelle d'un échantillon
    """

    def __init__(self, taille_echantillon=30):
        self.taille_echantillon = taille_echantillon
        self.annotations = []

    def selectionner_echantillon(self, input_root="Runs_jointure", run_number="run1"):
        """
        Sélectionne aléatoirement des CVs à annoter
        """
        run_path = os.path.join(input_root, run_number)
        fichiers = ["interests.json", "experiences.json", "studies.json"]

        echantillon = []

        for fichier in fichiers:
            chemin = os.path.join(run_path, fichier)
            if not os.path.exists(chemin):
                continue

            section = fichier.replace(".json", "")

            with open(chemin, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Sélectionner aléatoirement
            cv_ids = list(data.keys())
            nb_a_selectionner = min(self.taille_echantillon // 3, len(cv_ids))
            selection = random.sample(cv_ids, nb_a_selectionner)

            for cv_id in selection:
                variants = data[cv_id]
                for biais in ["Age", "Gender", "Origin"]:
                    echantillon.append({
                        "cv_id": cv_id,
                        "section": section,
                        "biais": biais,
                        "original": variants.get("Original", []),
                        "variant": variants.get(biais, [])
                    })

        # Mélanger l'échantillon
        random.shuffle(echantillon)
        return echantillon[:self.taille_echantillon]

    def interface_annotation(self, echantillon):
        """
        Interface console pour annotation manuelle
        """
        print("="*60)
        print("🧑‍⚖️ VALIDATION HUMAINE - AUDIT DES BIAIS")
        print("="*60)
        print(f"Vous allez annoter {len(echantillon)} comparaisons")
        print("\nPour chaque comparaison, jugez si la variante est COHÉRENTE avec l'original")
        print("Ignorez les différences mineures (ponctuation, accents, ordre)")
        print("\n[C]ohérent | [O]mission | [H]allucination | [M]odification | [S]kip | [Q]uit\n")

        for i, item in enumerate(echantillon, 1):
            print("\n" + "="*60)
            print(f"📋 Comparaison {i}/{len(echantillon)}")
            print(f"CV: {item['cv_id']} | Section: {item['section']} | Biais: {item['biais']}")
            print("-"*60)
            print(f"ORIGINAL:\n{json.dumps(item['original'], indent=2, ensure_ascii=False)}\n")
            print(f"VARIANT ({item['biais']}):\n{json.dumps(item['variant'], indent=2, ensure_ascii=False)}")
            print("-"*60)

            while True:
                reponse = input("Votre jugement [C/O/H/M/S/Q] : ").strip().upper()

                if reponse == "Q":
                    print("❌ Annotation interrompue")
                    return self.annotations

                if reponse == "S":
                    print("⏭️ Ignoré")
                    break

                if reponse in ["C", "O", "H", "M"]:
                    coherent = (reponse == "C")
                    error_map = {"C": "None", "O": "Omission", "H": "Hallucination", "M": "Modification"}

                    details = input("Commentaire (optionnel) : ").strip()

                    annotation = {
                        "cv_id": item["cv_id"],
                        "section": item["section"],
                        "biais": item["biais"],
                        "coherent": coherent,
                        "error_type": error_map[reponse],
                        "details": details if details else "Annotation manuelle",
                        "annotateur": "humain",
                        "timestamp": datetime.now().isoformat()
                    }

                    self.annotations.append(annotation)
                    print(f"✅ Enregistré : {error_map[reponse]}")
                    break
                else:
                    print("❌ Choix invalide, recommencez")

        return self.annotations

    def sauvegarder_annotations(self, output_dir="Analyse/validation_humaine"):
        """
        Sauvegarde les annotations dans un fichier JSON
        """
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"annotations_humaines_{timestamp}.json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.annotations, f, indent=4, ensure_ascii=False)

        print(f"\n✅ Annotations sauvegardées : {output_path}")
        print(f"   Total : {len(self.annotations)} annotations")

        # Statistiques
        coherents = sum(1 for a in self.annotations if a["coherent"])
        print(f"\n📊 Résumé :")
        print(f"   Cohérents : {coherents}/{len(self.annotations)}")
        print(f"   Erreurs : {len(self.annotations) - coherents}")

        return output_path

    def comparer_avec_llm(self, annotations_llm_path):
        """
        Compare les annotations humaines avec celles du LLM
        Calcule l'accord inter-annotateurs (Kappa de Cohen)
        """
        if not os.path.exists(annotations_llm_path):
            print(f"❌ Fichier LLM introuvable : {annotations_llm_path}")
            return

        with open(annotations_llm_path, "r", encoding="utf-8") as f:
            annotations_llm = json.load(f)

        # Créer un dictionnaire pour faciliter la comparaison
        llm_dict = {
            f"{a['cv_id']}_{a.get('section', 'unknown')}": a
            for a in annotations_llm
        }

        accords = 0
        desaccords = []

        for humain in self.annotations:
            key = f"{humain['cv_id']}_{humain['section']}"
            llm_annotation = llm_dict.get(key)

            if llm_annotation:
                if humain["coherent"] == llm_annotation.get("coherent"):
                    accords += 1
                else:
                    desaccords.append({
                        "cv_id": humain["cv_id"],
                        "section": humain["section"],
                        "humain": humain["error_type"],
                        "llm": llm_annotation.get("error_type")
                    })

        total = len(self.annotations)
        taux_accord = (accords / total * 100) if total > 0 else 0

        print(f"\n🤝 ACCORD HUMAIN-LLM :")
        print(f"   Accords : {accords}/{total} ({taux_accord:.1f}%)")
        print(f"   Désaccords : {len(desaccords)}")

        if desaccords:
            print("\n⚠️ Exemples de désaccords :")
            for d in desaccords[:5]:
                print(f"   - {d['cv_id']} ({d['section']}): Humain={d['humain']}, LLM={d['llm']}")

        return taux_accord, desaccords

def main():
    """
    Script principal pour lancer la validation humaine
    """
    print("🚀 Lancement de la validation humaine\n")

    # 1. Sélection de l'échantillon
    validateur = ValidationHumaine(taille_echantillon=30)
    echantillon = validateur.selectionner_echantillon()

    if not echantillon:
        print("❌ Aucun échantillon disponible")
        return

    # 2. Annotation
    annotations = validateur.interface_annotation(echantillon)

    if not annotations:
        print("❌ Aucune annotation créée")
        return

    # 3. Sauvegarde
    output_path = validateur.sauvegarder_annotations()

    print(f"\n🎯 Prochaine étape : Comparez avec les annotations LLM")
    print(f"   validateur.comparer_avec_llm('chemin/vers/rapport_llm.json')")

if __name__ == "__main__":
    main()
