import sys
import pandas as pd
import random
import datetime
import yaml
import click
from collections import Counter
from loguru import logger

# Résultats possibles
resultats = ["1", "N", "2"]


def generer_une_grille(probabilites: dict) -> list:
    """Générer une grille basée sur des probabilités

    Args:
        probabilites (dict): Liste des probabilités pour les matchs

    Returns:
        list: Grille générée
    """
    grille = []
    for match, probs in probabilites.items():
        resultat = random.choices(resultats, weights=probs)[0]
        grille.append(resultat)
    return grille


def est_grille_valide(grille: list) -> bool:
    """Vérifie si la grille respecte les contraintes

    Args:
        grille (list): Grille à vérifier

    Returns:
        bool: True si la grille est valide, sinon False
    """
    victoires_domicile = grille.count("1")
    matchs_nuls = grille.count("N")
    victoires_exterieur = grille.count("2")
    # Conditions pour LF14
    if len(grille) == 14:
        return 3 <= victoires_domicile <= 8 and 2 <= matchs_nuls <= 5 and 3 <= victoires_exterieur <= 6
    # Conditions pour LF12
    elif len(grille) == 12:
        return 3 <= victoires_domicile <= 7 and 2 <= matchs_nuls <= 4 and 2 <= victoires_exterieur <= 5
    # Conditions pour LF8
    elif len(grille) == 8:
        return 2 <= victoires_domicile <= 5 and 0 <= matchs_nuls <= 3 and 1 <= victoires_exterieur <= 4
    else:
        return False


def generer_grilles(probabilites: dict, nombre_grilles: int) -> tuple:
    """Générer plusieurs grilles

    Args:
        probabilites (dict): Liste des probabilités pour les matchs
        nombre_grilles (int): Nombre de grilles à générer.

    Returns:
        tuple: Grilles générées et compte des résultats
    """
    grilles = []
    compte_tous_resultats = {match: Counter() for match in probabilites.keys()}

    while len(grilles) < nombre_grilles:
        grille = generer_une_grille(probabilites)
        if est_grille_valide(grille) and grille not in grilles:
            grilles.append(grille)
            # Mettre à jour le compte des résultats
            for match, resultat in zip(probabilites.keys(), grille):
                compte_tous_resultats[match][resultat] += 1

    return grilles, compte_tous_resultats


def charger_config(config_path: str) -> dict:
    """Charge la configuration depuis un fichier YAML

    Args:
        config_path (str): Chemin du fichier de configuration YAML à charger.

    Returns:
        dict: Fichier YAML chargé sous forme de dictionnaire.
    """
    with open(config_path, "r") as fichier:
        return yaml.safe_load(fichier)


@click.command()
@click.option(
    "--config",
    type=click.Path(exists=True),
    required=True,
    help="Chemin du fichier (au format YAML) contenant les probabilités des matchs.",
)
@click.option("--nombre-grilles", default=8, help="Nombre de grilles à générer, par défaut à 8.")
def main(config: str, nombre_grilles: int) -> None:
    """Point d'entrée principal du script."""

    # Initialisation pour les logs
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}",
        level="INFO",
    )

    # Charger les probabilités depuis le fichier config
    logger.info("Chargement du fichier de configuration...")
    config_data = charger_config(config)

    # Charger le fichier config
    probabilites_matchs = config_data.get("probabilites_matchs", {})
    parametres = config_data.get("parametres_generaux", {})
    chemin_sortie = parametres.get("chemin_sortie", "./")

    # Générer les grilles et compter les résultats
    logger.info(f"Génération de {nombre_grilles} grilles...")
    grilles, compte_resultats = generer_grilles(probabilites_matchs, nombre_grilles)

    # Sauvegarde du fichier
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nom_fichier = f"{chemin_sortie}/liste_{timestamp}.csv"
    colonnes = [f"Grille_{i+1}" for i in range(len(grilles))]
    df = pd.DataFrame(list(map(list, zip(*grilles))), columns=colonnes)
    df.to_csv(nom_fichier, index=False)

    # Afficher bilan
    logger.success(f"Fichier écrit : {nom_fichier}")
    logger.info("Résumé des résultats :")
    resume_resultats = {match: dict(comptes) for match, comptes in compte_resultats.items()}
    for match, counts in resume_resultats.items():
        logger.info(f"{match}: {counts}")


if __name__ == "__main__":
    main()
