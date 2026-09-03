# Fonctionnement de SpaceWatchers

SpaceWatchers enchaîne la lecture d’une liste de satellites, la récupération de leurs positions et la recherche d’une paire proche. Le traitement est regroupé dans `main.py`, avec une interface Tkinter et des fonctions dédiées aux données et au calcul.

## Entrées et résultat

| Entrée | Contenu utilisé |
| --- | --- |
| CSV des satellites | Identifiants de la colonne `NORAD Number` |
| CSV de configuration local | Clé N2YO de la colonne `api id` |
| Réponses de l’API | Nom, identifiant, latitude, longitude et altitude |

À la fin du traitement, la fenêtre affiche la paire retenue, ses coordonnées et le résultat de la comparaison. Les réponses sont conservées en mémoire ; le programme ne crée pas de base de données ni de fichier de résultats.

## 1. Lecture des fichiers

Depuis l’interface, l’utilisateur choisit les deux CSV. `lire_csv` extrait les identifiants NORAD et `get_api_key` lit la configuration d’accès à N2YO. Les autres colonnes du catalogue satellite ne sont pas nécessaires au traitement.

La lecture attend un séparateur `;` et utilise l’encodage Latin-1. Les noms des colonnes servent à retrouver les informations, indépendamment de leur position dans le fichier.

## 2. Acquisition des positions

Pour chaque identifiant, `call_api` interroge le service `positions` de N2YO avec Requests. Chaque appel demande une seule position et dispose d’un délai maximal de 25 secondes.

Les appels sont lancés par lots avec `ThreadPoolExecutor`, puis leurs réponses JSON sont regroupées. Le nombre de requêtes du lot est calculé à partir du compteur renvoyé par l’API. Cette partie reste à revoir pour borner la concurrence et s’arrêter proprement lorsque le quota est atteint.

`get_position` extrait ensuite les coordonnées de chaque réponse et les associe au nom et à l’identifiant du satellite. Les horodatages ne sont pas conservés : des réponses récupérées successivement ne représentent pas nécessairement le même instant.

## 3. Recherche de la paire

La recherche suit une approche « diviser pour régner » :

1. trier les positions selon la latitude ;
2. séparer l’ensemble en deux groupes ;
3. rechercher récursivement la meilleure paire dans chacun ;
4. comparer les points dans une bande autour de la séparation ;
5. conserver la paire ayant le plus petit score.

Pour un groupe de trois points ou moins, les paires sont comparées directement. La fonction `same_item` applique également un filtre sur les noms pour écarter certaines associations.

| Fonction | Rôle dans la recherche |
| --- | --- |
| `Karatsuba` | Découpage récursif et sélection du meilleur résultat |
| `points_proches` | Comparaison directe des petits ensembles |
| `proche_bande` | Comparaison des points autour de la séparation |
| `same_item` | Exclusion de certaines paires selon leurs noms |

`Karatsuba` est le nom conservé dans le projet, mais il ne s’agit pas de l’algorithme de multiplication du même nom. La comparaison dans la bande reste exhaustive ; cette version ne garantit pas une recherche en O(n log n).

## 4. Affichage

`affichage` construit le message final avec les noms et coordonnées de la paire. `SatelliteInterface` prend en charge la sélection des fichiers, le message de progression et la zone de résultat.

Le programme réalise une analyse ponctuelle. Il n’affiche pas de carte, ne rafraîchit pas continuellement les positions et ne prédit pas de trajectoire.

## Points restant à améliorer

- **Calcul de distance.** La comparaison utilise directement les écarts de latitude, longitude et altitude. Une conversion dans un repère et une unité communs est nécessaire avant de donner une distance en kilomètres.
- **Sélection des paires.** Le filtre de noms peut exclure des objets distincts d’une même famille. Il faudrait préciser ce critère et le distinguer de la suppression des doublons NORAD.
- **Fiabilité du traitement.** Les listes vides, les réponses incomplètes, les erreurs HTTP et l’épuisement du quota doivent être gérés explicitement. Les appels réseau peuvent aussi bloquer l’interface.

Des essais isolés ont comparé la recherche récursive à une comparaison exhaustive sur des données synthétiques, avec la même formule et le même filtre. Ils ne valident ni les distances physiques ni le fonctionnement complet avec N2YO. Aucune suite de tests automatisés n’est actuellement fournie dans le dépôt.

Référence : [documentation de l’API N2YO](https://www.n2yo.com/api/).
