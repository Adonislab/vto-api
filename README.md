# VTO Backend FastAPI

API Backend FastAPI pour un système d'essayage virtuel et d'estimation de mensurations.

## Description

Ce projet fournit une API modulaire pour :
- réaliser un essayage virtuel avec un modèle VTON 
- estimer des mensurations à partir d'une photo et d'une taille donnée

## Prérequis

- Python 3.11 ou supérieur
- `pip`

## Installation

1. Clonez le dépôt ou placez-vous dans le dossier du projet :

```bash
git clone git@github.com:Adonislab/vto-api.git
```

2. Créez un environnement virtuel :

```bash
python -m venv venv
```

3. Activez l'environnement :

```bash
source venv/bin/activate
```

4. Installez les dépendances :

```bash
pip install -r requirements.txt
```

## Configuration

Créez un fichier `.env` à la racine du projet contenant :

```text
REPLICATE_API_TOKEN=your_replicate_api_token_here
```

Remplacez `your_replicate_api_token_here` par votre clé Replicate.

## Lancer l'application

Démarrez le serveur FastAPI avec Uvicorn :

```bash
uvicorn main:app --reload
```

Le service sera disponible par défaut sur `http://127.0.0.1:8000`.

## Endpoints disponibles

### Vérification de santé

- `GET /`
- Retourne un message de statut de l'API.

### Essayage virtuel

- `POST /try-on`
  - Paramètres multipart/form-data :
    - `human_image` : photo de la personne
    - `garment_image` : photo du vêtement
    - `category` : `upper_body`, `lower_body` ou `dresses` (par défaut `upper_body`)
    - `description` : description du vêtement
  - Retourne l'URL du résultat d'essayage.

- `POST /try-on-outfit`
  - Paramètres multipart/form-data :
    - `human_image` : photo de la personne
    - `top_image` : photo du vêtement du haut (optionnel)
    - `bottom_image` : photo du vêtement du bas (optionnel)
  - Au moins un vêtement doit être fourni.
  - Retourne l'URL du rendu final.

### Estimation des mensurations

- `POST /estimate-measurements`
  - Paramètres multipart/form-data :
    - `human_image` : photo de la personne
    - `height_cm` : hauteur réelle de la personne en centimètres
  - Retourne des mesures estimées basées sur l'image et la hauteur.

## Notes

- Le modèle de try-on utilise l'API Replicate via le service `services/replicate_service.py`.
- L'estimation des mensurations s'appuie sur les contours détectés dans l'image via OpenCV.

## Fichiers importants

- `main.py` : configuration FastAPI et routeurs.
- `routers/try_on.py` : routes d'essayage virtuel.
- `routers/measurements.py` : route d'estimation des mensurations.
- `services/pose_service.py` : logique de traitement d'image et extraction de mesures.
- `services/replicate_service.py` : intégration du modèle Replicate.
