# Cost Graph : Optimisation des Coûts d'Approvisionnement
## Description
Ce projet vise à optimiser les coûts d'approvisionnement et de stockage pour une entreprise en utilisant des algorithmes de graphes. Le programme permet de comparer différentes stratégies d'approvisionnement (achat unique, achat mensuel, stratégie optimale) et de visualiser les résultats sous forme de graphiques et de rapports.
___

## Fonctionnalités

### Interface utilisateur (GUI) :

- Configuration des paramètres d'approvisionnement (nombre de mois, frais fixes, coût de stockage).
- Saisie des besoins mensuels d'installations.
- Affichage des résultats sous forme de texte et de graphiques.

### Algorithmes d'optimisation :

- Création d'un graphe orienté pondéré représentant les coûts d'approvisionnement et de stockage.
- Détection de cycles dans le graphe pour garantir sa validité.
- Utilisation de l'algorithme de Dijkstra pour trouver le chemin optimal (stratégie d'approvisionnement minimale).
- Comparaison des coûts avec d'autres stratégies : achat unique et achats mensuels.

### Visualisation des résultats :

- Graphiques comparant les coûts cumulés des différentes stratégies.
- Graphique en barres montrant les quantités optimales à commander chaque mois.
___

## Configuration de l'environnement

- **Bibliothèques** :
    - networkx : Manipulation des graphes.
    - matplotlib : Visualisation des graphiques.
    - tkinter : Interface utilisateur.
    - ttkthemes : Thèmes pour tkinter.

Pour installer les dépendances :

```shell
pip install matplotlib networkx ttkthemes
```


## Structure du Projet
### Fichiers principaux
- interface.py : Contient l'interface utilisateur.
- algos.py : Contient les algorithmes de graphes et les calculs de coûts (réutilisés ensuite dans `interface.py`).
    - Remarque, `algos.py` est préprogrammé avec des données hardcoded issues de l'énoncé du projet, et permet également, si lancé, de générer des graphiques et, sur le terminal, un rapport de comparaisons
    - `interface.py` est plus joli :)

### Algorithmes
#### a. Création du graphe 
- Chaque nœud représente un mois.
- Les arcs entre les nœuds représentent les coûts d'approvisionnement et de stockage pour couvrir les besoins d'une période donnée.
- Les poids des arcs sont calculés comme la somme de ce qui suit :
    - Coût fixe d'approvisionnement.
    - Coût des installations nécessaires.
    - Coût de stockage des installations non utilisées.
#### b. Détection de cycles
- Utilise une recherche en profondeur (DFS) pour détecter les cycles dans le graphe.
- Garantit que le graphe est un graphe acyclique dirigé (nécessaire pour l'algorithme de Dijkstra)
#### c. Algorithme de Dijkstra
- Trouve le chemin de coût minimal entre le premier mois (nœud 0) et le dernier mois.
- Retourne les distances minimales et les prédécesseurs pour reconstruire le chemin optimal.
#### d. Reconstruction du chemin
- Reconstruit le chemin optimal à partir des prédécesseurs retournés par Dijkstra.
#### e. Calcul des coûts des stratégies
- Stratégie 1 : Achat unique :
    - Tous les besoins sont achetés au début, avec des coûts de stockage élevés.
- Stratégie 2 : Achat mensuel :
    - Les besoins sont achetés chaque mois, sans coûts de stockage.
- Stratégie 3 : Stratégie optimale :
    - Utilise le chemin optimal trouvé par Dijkstra pour minimiser les coûts.

### Utilisation
- Lancer le fichier `interface.py`
- Étape 1 : Configuration des paramètres, saisir :
    - Nombre de mois.
    - Frais fixes d'approvisionnement.
    - Coût de stockage par unité par mois.
- Étape 2 : Entrer les besoins pour chaque mois.
- Résultats :
    - Affichage des coûts optimaux et des stratégies comparées.
- Visualisation des graphiques.
    - **Graphique des coûts cumulés** :
    Compare les coûts cumulés des trois stratégies (achat unique, achat mensuel, stratégie optimale).
    - **Graphique des commandes optimales** :
    Montre les quantités à commander chaque mois pour la stratégie optimale.

### Tests

Le fichier algos.py contient des tests pour vérifier le bon fonctionnement des algorithmes :

- Détection de cycles.
- Algorithme de Dijkstra.
- Reconstruction du chemin.



