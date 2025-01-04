# ⚽ PREDIFOOT

## 📝 Description
Ce projet permet d’automatiser la création des grilles Loto Foot et le remplissage sur le site Parions Sport via Selenium.

Il permet de créer un fichier CSV contenant le nombre de grilles souhaitées et de les remplir automatiquement.

## 📦 Installation
1. Installer si besoin uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Cloner le dépôt :
```bash
git clone https://github.com/clementgitteau/predifoot.git
cd predifoot
```

3. Créer un environnement virtuel Python :
```bash
uv venv --python 3.12 .venv
source .venv/bin/activate  # Sur Windows : venv\Scripts\activate
```

4. Installer les dépendances :
```bash
uv sync
```

## ⚙️ Configuration
**Préparer le fichier de configuration YAML :**

Créer un fichier de configuration _config.yaml_ à partir du fichier _config_exemple.yaml_.

Le fichier de configuration doit contenir :

    - Les probabilités des résultats des matchs
    - Le répertoire dans lequel seront sauvegardées les grilles à jouer
    - Le lien vers la page web de la grille LotoFoot

## 🚀 Utilisation
1. **Génération des grilles :**
```bash
python -m generer_grilles.py --config config.yaml --nombre-grilles 8
```

2. **Remplissage automatique des grilles :**
```bash
python -m remplir_grilles.py --config config.yaml --fichier_predictions ./resultats/liste_xxx.csv
```

## 📋 Prérequis
- **Python** >= 3.12
- **Bibliothèques Python :**
    - black
    - click
    - loguru
    - pandas
    - pyyaml
    - selenium
- **Navigateur supporté :**
    - Google Chrome

## 🛠️ Structure du projet
```
predifoot/
├── resultats/
├──├── .gitkeep
├── .gitignore
├── .python-version
├── config.yaml
├── generer_grilles.py
├── pyproject.toml
├── README.md
├── remplir_grilles.py
├── uv.lock
```

## 👨🏻‍💻 Contributeurs
GITTEAU Clément - gitteauclement@gmail.com

GITTEAU Sidney - gitteau.sidney@gmail.com

Pour toute question ou suggestion, n'hésitez pas à nous contacter !