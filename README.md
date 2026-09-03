# SpaceWatchers

SpaceWatchers est un projet réalisé en terminale, en binôme, dans le cadre des Trophées NSI 2025.

Le but était de créer une application capable de récupérer la position de satellites grâce à l’API N2YO, puis de rechercher les deux satellites les plus proches dans les données obtenues. Le résultat est affiché dans une interface graphique développée avec Tkinter.

Le projet a reçu un **Prix Coup de cœur académique** puis une **distinction nationale** aux Trophées NSI 2025.

## Fonctionnement

L’utilisateur sélectionne deux fichiers CSV :

- une liste de satellites contenant leurs identifiants NORAD ;
- un fichier local contenant la clé nécessaire pour interroger l’API.

Le programme récupère ensuite les positions des satellites, stocke les réponses reçues au format JSON et applique un algorithme récursif de recherche de proximité. Plusieurs requêtes peuvent être envoyées en parallèle pour éviter de les traiter une par une.

```text
Fichiers CSV
    ↓
Requêtes vers l’API N2YO
    ↓
Récupération des positions
    ↓
Recherche récursive de la paire la plus proche
    ↓
Affichage du résultat avec Tkinter
```

## Ma contribution

Je me suis principalement occupé de :

- la lecture des fichiers CSV ;
- l’extraction des identifiants NORAD ;
- l’organisation des données récupérées ;
- l’algorithme récursif nommé `Karatsuba` dans le code et des fonctions de comparaison associées.

L’interface graphique a été réalisée dans le cadre du travail en groupe, mais je n’en ai pas développé seul l’ensemble.

## Technologies utilisées

- **Python** pour le traitement principal ;
- **Tkinter** pour l’interface graphique ;
- **Requests** pour les appels à l’API N2YO ;
- **ThreadPoolExecutor** pour lancer plusieurs requêtes ;
- **Pillow** pour la gestion de l’image de fond ;
- fichiers **CSV** pour les données d’entrée ;
- réponses **JSON** pour les données reçues de l’API.

## Installation

Python 3.8 ou une version plus récente est recommandé.

```bash
git clone https://github.com/RaphaelCordelle/SpaceWatchers.git
cd SpaceWatchers
python -m venv .venv
python -m pip install -r requirements.txt
```

Il faut ensuite activer l’environnement virtuel selon le système utilisé.

## Utilisation

1. Préparer un fichier CSV contenant une colonne `NORAD Number`.
2. Préparer séparément un fichier CSV contenant une colonne `api id` et sa propre clé N2YO.
3. Lancer l’application avec `python main.py`.
4. Sélectionner les deux fichiers dans la fenêtre.
5. Cliquer sur **Commencer**.

Des modèles sont disponibles dans le dossier [`examples`](examples/). La valeur présente dans `compte.example.csv` est volontairement fictive.

Pour un premier essai, il est préférable d’utiliser seulement quelques satellites afin de ne pas envoyer trop de requêtes.

## Organisation du dépôt

```text
SpaceWatchers/
├── main.py
├── requirements.txt
├── examples/
│   ├── satellites.example.csv
│   └── compte.example.csv
├── docs/
│   └── fonctionnement.md
├── AUTHORS.md
├── SECURITY.md
└── LICENSE
```

Le fichier [`docs/fonctionnement.md`](docs/fonctionnement.md) explique plus précisément le rôle des fonctions et le chemin suivi par les données.

## Limites actuelles

Cette version correspond au projet réalisé en terminale. Elle permet de travailler sur les données satellites, mais ce n’est pas un outil de prévention des collisions.

Le calcul historique compare directement latitude, longitude et altitude. Ces valeurs ne sont pas exprimées dans la même unité : le résultat ne doit donc pas être considéré comme une distance physique précise en kilomètres. Une amélioration possible serait de convertir les positions dans un même repère avant de les comparer.

La gestion des erreurs réseau, des quotas de l’API et des tâches de fond dans l’interface pourrait également être améliorée.

## Sécurité

Les clés API sont personnelles et ne doivent jamais être publiées. Le fichier utilisé localement est exclu du dépôt grâce au `.gitignore`.

La documentation N2YO demande aussi de respecter les limites du service et de ne pas utiliser plusieurs clés pour contourner les quotas. Les précautions sont détaillées dans [`SECURITY.md`](SECURITY.md).

## Auteurs

Projet réalisé par **Raphael Cordelle** et **Victor Laurini**.

La répartition de notre travail est précisée dans [`AUTHORS.md`](AUTHORS.md).
