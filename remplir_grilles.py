import sys
import os
import pandas as pd
import click
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger
from generer_grilles import charger_config


def remplir_lotofoot(predictions: pd.DataFrame, lien_grille: str) -> None:
    """Automatisation du remplissage des grilles LotoFoot

    Args:
        predictions (DataFrame): DataFrame contenant les grilles.
        lien_grille (str): URL de la grille LotoFoot à remplir.
    """
    # Diviser les colonnes en groupes de 8, nombre maximum de grilles par page
    nb_colonnes = len(predictions.columns)
    taille_groupe = 8
    nb_groupes = (nb_colonnes + taille_groupe - 1) // taille_groupe

    for index_groupe in range(nb_groupes):
        # Initialiser le driver
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(
            options=options,
        )
        driver.get(lien_grille)

        # Gérer les cookies si une bannière apparaît
        try:
            bouton_cookies = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, "popin_tc_privacy_button_2"))
            )
            bouton_cookies.click()
            print("Cookies acceptés.")
        except Exception:
            print("Aucune bannière cookies détectée.")

        # Sélectionner les colonnes pour le groupe actuel
        col_debut = index_groupe * taille_groupe
        col_fin = min(col_debut + taille_groupe, nb_colonnes)
        colonnes_actuelles = predictions.iloc[:, col_debut:col_fin]

        # Rajouter des grilles selon le nombre de colonnes
        for n in range(col_fin - col_debut):
            if n != (col_fin - col_debut - 1):
                bouton_ajouter_grille = driver.find_element(
                    By.CSS_SELECTOR,
                    'button.grid__nav-btn[data="app-loto-grid|it-btAdd"]',
                )
                driver.execute_script("arguments[0].click();", bouton_ajouter_grille)

        # Détecter les cases à cocher
        elements_1 = driver.find_elements(
            By.CSS_SELECTOR,
            '[data="app-grid-outcomes|lt-outcome1GO"]',
        )
        elements_n = driver.find_elements(
            By.CSS_SELECTOR,
            '[data="app-grid-outcomes|lt-outcomeNGO"]',
        )
        elements_2 = driver.find_elements(
            By.CSS_SELECTOR,
            '[data="app-grid-outcomes|lt-outcome2GO"]',
        )

        # Remplissage des grilles
        valeurs_a_remplir = colonnes_actuelles.astype(str).T.values.flatten().tolist()
        for i, prediction in enumerate(valeurs_a_remplir):
            if prediction == "1":
                driver.execute_script("arguments[0].click();", elements_1[i])
            elif prediction == "N":
                driver.execute_script("arguments[0].click();", elements_n[i])
            elif prediction == "2":
                driver.execute_script("arguments[0].click();", elements_2[i])
        print("Toutes les grilles ont été remplies. La page reste ouverte.")
    # La page reste ouverte pour valider les grilles et sauvegarder le QR code
    input("Appuyez sur Entrée pour fermer le navigateur.")
    driver.quit()


def lire_predictions_grilles(
    dossier: str, prefixe: str = "liste_", extension: str = ".csv", fichier_predictions: str = None
) -> pd.DataFrame:
    """Lit le dernier fichier modifié dans un dossier donné avec un préfixe et une extension spécifiques.

    Args:
        dossier (str): Chemin vers le dossier contenant les fichiers.
        prefixe (str): Préfixe des fichiers à rechercher.
        extension (str): Extension des fichiers à rechercher.
        fichier_predictions (str): Optionnel. Chemin du fichier des prédictions des grilles.

    Returns:
        pd.DataFrame: Contenu du fichier sous forme de DataFrame.
    """
    if fichier_predictions:
        if not os.path.exists(fichier_predictions):
            logger.error(f"Le fichier des prédictions des grilles spécifié {fichier_predictions} n'existe pas.")
            raise FileNotFoundError(
                f"Le fichier des prédictions des grilles spécifié {fichier_predictions} n'existe pas."
            )
        logger.info(f"Lecture du fichier des prédictions des grilles spécifié : {fichier_predictions}")
        return pd.read_csv(fichier_predictions)

    # Lister tous les fichiers dans le dossier correspondant au préfixe et à l'extension
    fichiers = [f for f in os.listdir(dossier) if f.startswith(prefixe) and f.endswith(extension)]

    if not fichiers:
        logger.error(f"Aucun fichier correspondant trouvé dans le dossier {dossier}")
        raise FileNotFoundError(f"Aucun fichier correspondant trouvé dans le dossier {dossier}")

    # Obtenir le chemin complet des fichiers
    chemins_fichiers = [os.path.join(dossier, f) for f in fichiers]

    # Conserver le fichier avec la date de modification la plus récente
    dernier_fichier = max(chemins_fichiers, key=os.path.getmtime)

    # Charger le fichier en DataFrame
    logger.info(f"Lecture du fichier : {dernier_fichier}")
    return pd.read_csv(dernier_fichier)


@click.command()
@click.option(
    "--config",
    type=click.Path(exists=True),
    required=True,
    help="Chemin du fichier (au format YAML) contenant les probabilités des matchs.",
)
@click.option(
    "--fichier_predictions",
    type=click.Path(exists=True),
    help="Optionnel. Chemin du fichier spécifique à lire. Si non fourni, le dernier fichier dans le dossier sera lu.",
)
def main(config: str, fichier_predictions: str) -> None:
    """Point d'entrée principal du script"""

    # Initialisation pour les logs
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}",
        level="INFO",
    )

    # Charger le fichier config
    logger.info("Chargement du fichier de configuration...")
    config_data = charger_config(config)
    parametres = config_data.get("parametres_generaux", {})
    dossier_resultats = parametres.get("chemin_sortie", "./")
    lien_grille = parametres.get("lien_grille", "")

    # Lecture du fichier et remplissage des grilles
    predictions = lire_predictions_grilles(
        dossier_resultats, prefixe="liste_", extension=".csv", fichier_predictions=fichier_predictions
    )
    remplir_lotofoot(predictions, lien_grille)


if __name__ == "__main__":
    main()
