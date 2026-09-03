# Comprendre le code de SpaceWatchers

Ce document décrit le fichier `main.py` transmis, sans lui attribuer des fonctions qui n’y sont pas présentes. Il n’y a ici ni GPIO ni accès direct aux registres comme dans EvalBot : l’application travaille avec des fichiers et une API HTTP.

## 1. Le chemin des données

```text
Fichier satellites (colonne NORAD Number)
              + fichier local de clé API (colonne api id)
              |
              v
Lecture CSV -> requêtes N2YO -> réponses JSON
              |
              v
Dictionnaire {(nom, identifiant): (latitude, longitude, altitude)}
              |
              v
Recherche récursive + filtre de noms -> résultat Tkinter
```

Le fichier satellites original comporte 7 560 lignes de données et 7 551 identifiants NORAD distincts lors de l’inventaire du 3 septembre 2026. Ce nombre décrit le fichier reçu, pas le nombre de satellites récupérés ou validés par l’application.

## 2. L’interface : `SatelliteInterface`

| Méthode | Ce qu’elle fait |
| --- | --- |
| `__init__` | Configure la fenêtre, initialise les chemins de fichiers et charge le fond. |
| `create_widgets` | Crée les boutons, libellés et zone de texte. |
| `load_satellite_file` | Ouvre la boîte de sélection du CSV des satellites. |
| `load_api_key_file` | Ouvre celle du fichier de comptes API. |
| `start_processing` | Vérifie la sélection des deux fichiers et programme la suite. |
| `run_main` | Appelle le traitement et affiche une erreur en cas d’exception. |
| `update_progress` | Change le message de progression. |
| `display_results` | Remplace le texte de résultat dans la fenêtre. |

Un **widget** est un élément de l’interface : bouton, libellé ou zone de texte. Une **callback**, ou fonction de rappel, est une fonction transmise à une autre partie du programme pour qu’elle soit appelée au bon moment. Ici, les fonctions d’affichage sont transmises à `main`.

### Pourquoi les threads ne suffisent pas ici

Le bouton conserve la méthode `start` d’un seul objet `Thread`, créé avec l’interface. Or un même objet thread ne peut pas être démarré deux fois. Un second clic pose donc problème.

De plus, `root.after(100, ...)` programme `run_main` dans la boucle événementielle de Tkinter. Cela ne transforme pas `run_main` en tâche de fond : ses attentes réseau peuvent bloquer la fenêtre. Certaines opérations Tkinter sont également appelées depuis le thread de départ. La solution envisagée est un travailleur séparé, avec une file de messages lue par l’interface ; elle n’est pas implémentée dans la version fournie.

## 3. L’acquisition : `main`

Cette fonction orchestre toute la récupération. Elle contient quatre fonctions locales :

| Fonction | Rôle |
| --- | --- |
| `lire_csv` | Recherche la colonne `NORAD Number` et construit la liste d’identifiants. |
| `get_api_key` | Recherche la colonne `api id` et charge les clés en mémoire. |
| `call_api` | Lance une requête HTTP GET, avec un délai maximal de 25 secondes, puis décode le JSON. |
| `affichage` | Extrait les positions, appelle la recherche et construit le message final. |

Ces fonctions sont définies à l’intérieur de `main`, et non dans des modules distincts.

### Les paramètres de la requête

Le programme utilise cette forme d’adresse, avec une clé personnelle ajoutée localement :

```text
https://api.n2yo.com/rest/v1/satellite/positions/
    {identifiant}/43.633119/1.394142/0/1/
```

L’identifiant désigne le satellite. Les valeurs suivantes sont la latitude et la longitude de l’observateur, son altitude, puis le nombre de positions demandé. Ce sont des paramètres d’API, pas des adresses mémoire matérielles.

Le code demande une position par satellite. Il n’enregistre pas les horodatages et les appels ne sont pas nécessairement traités au même instant : les réponses ne constituent donc pas un instantané synchronisé. Le sens des champs et les conditions d’usage sont décrits dans la [documentation officielle N2YO](https://www.n2yo.com/api/).

### Requêtes concurrentes et quotas

`ThreadPoolExecutor` gère un groupe de threads. Une **future** représente le résultat à venir d’une tâche soumise au groupe. `future.result()` attend ce résultat si nécessaire.

Le programme commence chaque lot par une requête sur le satellite 40018 pour consulter `transactionscount`. Il calcule ensuite une capacité à partir de la constante `1000`, lance un lot et change de clé.

Points importants dans cette implémentation :

- le nombre de travailleurs peut être très élevé, et peut devenir nul ou négatif si le quota est épuisé ;
- le compteur de progression augmente de la capacité calculée, pas forcément du nombre réellement demandé ;
- l’absence de champ `info` peut entraîner des tentatives répétées sans progrès ;
- le code ne vérifie pas explicitement le statut HTTP avant le décodage JSON ;
- les exceptions remontent jusqu’à l’interface, sans politique de reprise structurée.

La présence d’un délai de 25 secondes ne remplace pas ces contrôles. La rotation des clés doit être remplacée par un comportement respectant les quotas, sans contournement.

## 4. La préparation des positions : `get_position`

La fonction extrait le premier élément de `positions` et utilise le couple `(satname, satid)` comme clé de dictionnaire.

Un **dictionnaire** associe une clé à une valeur. Un **tuple** regroupe ici les trois coordonnées. Si le même couple apparaît plusieurs fois, l’entrée précédente est remplacée.

La fonction ignore les réponses sans champ `positions`, mais ne vérifie pas que la liste soit non vide ni que tous les sous-champs existent. Il faudrait distinguer les réponses valides, absentes et mal formées.

## 5. Les fonctions de calcul

### `points_proches`

Elle parcourt toutes les paires et conserve celle dont le score est minimal, parmi les paires acceptées par `same_item`. C’est une recherche exhaustive : pour n points, elle considère n(n−1)/2 paires.

La formule utilisée est :

```text
score = racine((latitude2 - latitude1)^2
             + (longitude2 - longitude1)^2
             + (altitude2 - altitude1)^2)
```

Cette formule ressemble à une distance euclidienne en trois dimensions, mais les données ne sont pas des coordonnées cartésiennes dans une unité commune. Un résultat égal à 1 pour un degré d’écart en longitude ne signifie pas un kilomètre. L’affichage actuel du suffixe « km » est donc à corriger.

### `Karatsuba`

Malgré son nom historique, elle effectue les étapes d’une recherche de paire proche :

1. Comparaison exhaustive lorsqu’il reste au plus trois points.
2. Tri selon la latitude.
3. Découpage en deux sous-ensembles.
4. Appels récursifs sur chacun.
5. Recherche dans une bande autour de la séparation.
6. Conservation du meilleur résultat.

Ce principe est appelé **diviser pour régner**. La récursivité décrit la façon d’exprimer le problème, mais ne garantit pas à elle seule une meilleure performance.

### `proche_bande`

Elle compare toutes les paires de la bande. Si cette bande contient beaucoup de points, le coût reste élevé. On ne peut pas annoncer une complexité garantie en O(n log n) pour cette implémentation : une bande de taille n entraîne déjà un travail quadratique.

### `same_item`

Elle tente d’écarter certaines paires à partir de leurs noms, avec des traitements particuliers pour INTELSAT/MEV et TANDEM/TERRA et des comparaisons de préfixes.

Ce filtre ne se limite pas aux doublons NORAD. Par exemple, deux noms `STARLINK-1000` et `STARLINK-2000` sont exclus de la comparaison alors qu’ils peuvent désigner deux objets distincts. Les utilisations de `find` sont aussi fragiles : la valeur `-1`, qui signifie « absent », est vraie dans un test booléen Python.

## 6. Tests de relecture réalisés

Le 3 septembre 2026, des vérifications hors réseau ont été effectuées sans lancer la fenêtre ni utiliser les clés :

- analyse syntaxique des 281 lignes de `main.py` : réussie ;
- exécution isolée des fonctions de calcul sur zéro, un et deux points ;
- comparaison récursive/exhaustive sur 100 jeux synthétiques de 12 points : même score dans les 100 cas, avec la même métrique et le même filtre ;
- vérification d’un cas d’exclusion entre deux noms STARLINK ;
- inventaire des formats et identifiants des CSV.

Ces essais ne prouvent ni la validité physique du score, ni la correction de tous les cas de l’algorithme, ni le fonctionnement complet de l’application. Pour zéro ou un point, le résultat contient une distance infinie et des valeurs `None`, que la construction du message final ne sait pas gérer correctement.

## 7. Prochaines améliorations possibles

Avant d’ajouter des fonctionnalités, les priorités seraient de protéger les secrets, corriger les unités et la gestion des erreurs, puis séparer l’interface, l’acquisition et le calcul. Des positions fictives permettraient de proposer une démonstration hors ligne reproductible.

Une évolution ultérieure pourrait utiliser des coordonnées cartésiennes avec un repère, un modèle et un instant communs, puis comparer la recherche optimisée à une référence exhaustive. Ce serait un travail supplémentaire, à distinguer du projet de terminale.
