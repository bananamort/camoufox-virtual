---
title: minimal-browser-screenshot-experiment
emoji: 💻
colorFrom: blue
colorTo: red
sdk: docker
app_file: app/server.py
pinned: false
---

# Minimal Browser Screenshot Experiment

Cette application web permet de prendre des captures d'écran de sites web en utilisant un navigateur headless et de les afficher directement dans l'interface utilisateur.

## Fonctionnalités

- Interface web simple et réactive
- Saisie d'URL avec valeur par défaut pointant vers le Open LLM Leaderboard
- Capture d'écran via Playwright (navigateur Chromium)
- Affichage du résultat dans l'interface

## Technologies utilisées

- **Backend**: FastAPI, Playwright
- **Frontend**: HTML/JS avec Tailwind CSS
- **Gestion des dépendances**: Poetry
- **Déploiement**: Docker, Hugging Face Spaces

## Installation locale

### Prérequis

- Python 3.10+
- Poetry
- Docker (optionnel)

### Installation avec Poetry

```bash
# Cloner le dépôt
git clone [url-du-repo]
cd minimal-browser-screenshot-experiment

# Installer les dépendances
poetry install

# Installer les navigateurs Playwright
poetry run playwright install chromium
poetry run playwright install-deps chromium

# Lancer l'application
poetry run uvicorn app.server:app --host 0.0.0.0 --port 7860
```

### Utilisation avec Docker

```bash
# Construire l'image Docker
docker build -t minimal-browser-screenshot .

# Lancer le conteneur
docker run -p 7860:7860 minimal-browser-screenshot
```

## Déploiement sur Hugging Face Spaces

Cette application est conçue pour être facilement déployée sur un Hugging Face Space.

1. Créez un nouveau Space de type Docker
2. Associez ce dépôt GitHub à votre Space
3. Le Space utilisera automatiquement le Dockerfile fourni pour construire et déployer l'application

## Utilisation

1. Accédez à l'application via votre navigateur
2. Entrez l'URL du site dont vous souhaitez prendre une capture d'écran (par défaut: Open LLM Leaderboard)
3. Cliquez sur "Prendre une capture d'écran"
4. Attendez quelques secondes pour que le navigateur headless charge la page et prenne la capture
5. La capture d'écran s'affiche dans l'interface
