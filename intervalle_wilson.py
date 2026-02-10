import math

def intervalle_confiance_erreurs(nb_erreurs, n):
    """
    Calcule l'intervalle de confiance de Wilson à 95% pour un taux d'erreur.

    Args:
        nb_erreurs (int): Le nombre d'erreurs observées.
        n (int): Le nombre total d'observations (taille de l'échantillon).

    Returns:
        tuple: (borne_inferieure, borne_superieure) en proportion (0 à 1).
    """
    if n == 0:
        return 0.0, 0.0

    # Paramètre z pour un intervalle de confiance à 95%
    z = 1.96

    # Calcul de la proportion d'erreurs observée (p chapeau)
    p_hat = nb_erreurs / n

    # --- Application de la formule de Wilson ---

    # 1. Le dénominateur : 1 + z²/n
    denominateur = 1 + (z**2) / n

    # 2. Le centre ajusté : p_hat + z²/2n
    centre_ajuste = p_hat + (z**2) / (2 * n)

    # 3. Le terme sous la racine : p(1-p)/n + z²/4n²
    terme_sous_racine = (p_hat * (1 - p_hat) / n) + (z**2) / (4 * n**2)
    racine = math.sqrt(terme_sous_racine)

    # Calcul des bornes
    borne_inf = (centre_ajuste - z * racine) / denominateur
    borne_sup = (centre_ajuste + z * racine) / denominateur

    return borne_inf, borne_sup

# ---- DONNEES ----
nombre_total_observations = 15282
nombre_erreurs_observees = 234
# -----------------

bas, haut = intervalle_confiance_erreurs(nombre_erreurs_observees, nombre_total_observations)

print(f"Pour {nombre_erreurs_observees} erreurs sur {nombre_total_observations} observations :")
print(f"Taux d'erreur observé (p_hat) : {nombre_erreurs_observees/nombre_total_observations:.2%}")
print(f"Intervalle de confiance à 95% : [{bas:.2%}, {haut:.2%}]")
