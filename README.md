# SpaceWatchers

**Projet de terminale NSI · Python · Trophées NSI 2025**

SpaceWatchers récupère des positions de satellites auprès de l’API N2YO et recherche une paire de satellites proches parmi les données reçues. Une interface Tkinter permet de choisir la liste à analyser, de lancer le traitement et de consulter le résultat.

Nous avons réalisé ce projet à deux, avec Victor Laurini, en terminale. Il a obtenu un **Prix Coup de cœur académique** et une **distinction nationale** aux Trophées NSI 2025.

## Mon travail sur le projet

Je me suis occupé de la lecture des fichiers CSV et de l’extraction des identifiants NORAD utilisés pour les requêtes. J’ai également développé la recherche récursive de proximité, nommée `Karatsuba` dans notre code, et les fonctions de comparaison associées.

L’application réunit ce travail et l’interface graphique réalisée dans le cadre du binôme.

## Du fichier satellite au résultat

1. **Sélection des données.** L’utilisateur choisit un CSV de satellites et un fichier local contenant sa clé N2YO.
2. **Récupération des positions.** Le programme extrait les identifiants NORAD, interroge l’API et regroupe les réponses. Les requêtes sont envoyées par lots avec `ThreadPoolExecutor`.
3. **Recherche de proximité.** Les positions sont réparties en deux groupes. Le programme recherche une paire dans chaque groupe, puis compare les points situés autour de la séparation.
4. **Affichage.** La fenêtre présente les noms des deux satellites retenus, leurs coordonnées et le résultat du calcul.

La récupération se fait à la demande, sans suivi continu. Le [fonctionnement détaillé](docs/fonctionnement.md) reprend les étapes du traitement et leur correspondance avec le code.

## Technologies

| Élément | Utilisation |
| --- | --- |
| Python | Lecture des données et algorithme de recherche |
| Requests / API N2YO | Récupération des positions par HTTP |
| Tkinter | Sélection des fichiers et affichage |
| ThreadPoolExecutor | Exécution concurrente des requêtes |
| Pillow | Image de fond facultative |
| CSV / JSON | Fichiers d’entrée et réponses de l’API |

## Lancer le projet

Prérequis : Python avec Tkinter, une connexion Internet et une clé personnelle [N2YO](https://www.n2yo.com/api/). Les commandes suivantes utilisent directement le Python de l’environnement virtuel, sans activation préalable.

Sous Windows, depuis PowerShell :

```powershell
git clone https://github.com/RaphaelCordelle/SpaceWatchers.git
cd SpaceWatchers
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Sous Linux ou macOS, remplacer `.\.venv\Scripts\python.exe` par `.venv/bin/python`.

Dans la fenêtre :

- choisir [`examples/satellites.example.csv`](examples/satellites.example.csv) ou un CSV comportant une colonne `NORAD Number` ;
- choisir son fichier de clé, construit à partir de [`compte.example.csv`](examples/compte.example.csv), avec une colonne `api id` ;
- cliquer sur **Commencer**.

Les CSV sont séparés par des points-virgules. Conserver le fichier de clé hors du dépôt et commencer avec quelques satellites seulement. Les exemples ne contiennent aucune clé réelle.

## État du projet

Le dépôt conserve le programme de terminale, avec deux adaptations de publication : le fond d’écran est facultatif et le lancement de la fenêtre est isolé du reste du fichier. L’image et le catalogue d’origine ne sont pas distribués ; un petit CSV d’exemple est fourni.

Le calcul actuel combine latitude, longitude et altitude sans conversion dans un repère commun. Malgré l’unité affichée par le programme, il ne fournit donc pas une distance physique fiable en kilomètres. Le projet n’est pas un outil de prévision des collisions.

Les principales suites possibles sont de corriger ce calcul, de mieux gérer les erreurs réseau et de rendre l’interface plus réactive. Le code contient aussi une rotation de clés qui doit être revue : N2YO interdit leur utilisation pour contourner les quotas. Les essais doivent rester dans les limites d’une seule clé autorisée.

## Fichiers du dépôt

- [`main.py`](main.py) : interface, acquisition des données et recherche de proximité ;
- [`docs/fonctionnement.md`](docs/fonctionnement.md) : déroulement du traitement ;
- [`examples/`](examples/) : modèles de fichiers d’entrée ;
- [`requirements.txt`](requirements.txt) : dépendances Python ;
- [`SECURITY.md`](SECURITY.md) : précautions concernant les clés API.

**Auteurs :** Raphael Cordelle et Victor Laurini — [contributions](AUTHORS.md).

**Licence :** GNU GPL v3 ou ultérieure, conformément à la notice d’origine — [texte de la licence](LICENSE).
