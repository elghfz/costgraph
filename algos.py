import networkx as nx
import heapq
import matplotlib.pyplot as plt


def load_data():
    installations = [200, 200, 300, 700, 1000, 200]
    frais_approvisionnement = 2000 
    cout_stockage = 2
    
    return installations, frais_approvisionnement, cout_stockage

# --- initialisation graphe ---
def init_graphe(installations, frais_approvisionnement, cout_stockage):
    # grace a la bibliotheque networkx
    G = nx.DiGraph()
    # ajouter noeud par mois
    n_mois = len(installations) 
    for i in range(n_mois + 1):
        G.add_node(i)
    # arcs avec les couts d'approvisionnement + stockage
    for i in range(n_mois):
        for j in range(i + 1, n_mois + 1):
            cout = frais_approvisionnement
            cout_cabines = sum(installations[i:j])
            cout_stockage_total = 0
            for k in range(i, j-1):
                # calcul des cabines en attente chaque mois
                cabines_en_attente = sum(installations[k+1:j])
                cout_stockage_total += cabines_en_attente * cout_stockage
            cout_total = cout + cout_cabines + cout_stockage_total
            G.add_edge(i, j, weight=cout_total)
    
    return G, n_mois

# --- détection des cycles  ---
def detect_cycle(graphe):
    visites = set()  # sommets visités
    pile = set()  # pile de récursion pour détecter les cycles

    def dfs(v): #on va definir l'algo dfs vu en cours ici (comme il est recusrsif)
        visites.add(v)
        pile.add(v)

        for voisin in graphe[v]:
            if voisin not in visites:
                if dfs(voisin):
                    return True
            elif voisin in pile:
                return True  # cycle détecté

        pile.remove(v)
        return False
    
    # et on va l'utiliser ici
    for noeud in graphe:
        if noeud not in visites:
            if dfs(noeud):
                return True # si cycle détecté

    return False  # sinon

# --- Dijkstra pour trouver le chemin optimal ---
def dijkstra(graphe, deb, fin):
    # couts pour tous les sommets
    # on utilise un tas binaire minimal pour la gestion des sommets à explorer
    tas_bin_min = [(0, deb)]  # (coût, sommet)
    distances = {deb: 0}
    precedents = {deb: None}  
    # prédécesseurs dans un dictionnaire (car faudra reconstruire le chemin après)

    while tas_bin_min:
        dist_actuelle, noeud_actuel = heapq.heappop(tas_bin_min)
        # arret si on est a la fin
        if noeud_actuel == fin:
            break

        # Si sommet déjà exploré avec coût plus bas on le saute
        if dist_actuelle > distances.get(noeud_actuel, float('inf')):
            continue
        
        # voir les voisins
        for voisin in graphe[noeud_actuel]:
            cout_arete = graphe[noeud_actuel][voisin]['weight']
            distance = dist_actuelle + cout_arete
            if distance < distances.get(voisin, float('inf')):
                distances[voisin] = distance
                precedents[voisin] = noeud_actuel  # suivre ce chemin
                heapq.heappush(tas_bin_min, (distance, voisin))

    return distances, precedents


# --- reconstruction du chemin optimal ---
def reconstruct_chemin_graphe(precedents, deb, fin):
    if fin not in precedents and fin != deb:
        return []  # pas de chemin trouvé
        
    path = []
    noeud_actuel = fin
    while noeud_actuel is not None:
        path.append(noeud_actuel)
        noeud_actuel = precedents.get(noeud_actuel)
    path.reverse()  # on inverse le chemin pour qu'il soit bien du début à la fin
    return path

# --- Calcul des coûts pour les différentes stratégies ---

# fonction auxiliere définie ici car ce calcul est refait ailleurs 
# (fonction et non variables globales car appelée aussi d'interface.py)
# donne la liste de tous les couts suivant le nb de mois
def calcul_couts_de_base(installations, frais_approvisionnement, cout_stockage):
    n_mois = len(installations)
    total_cabines = sum(installations)

    # strat 1 : tout au début
    cout_une_fois = [0] * (n_mois + 1)
    cout_total = frais_approvisionnement + total_cabines
    cout_une_fois[1] = cout_total
    stock = total_cabines
    for i in range(n_mois):
        stock -= installations[i]
        cout_total += stock * cout_stockage
        cout_une_fois[i + 1] = cout_total

    # strat 2 : achats mensuels
    cout_mensuel = [0] * (n_mois + 1)
    stock = 0
    cout_total = 0
    for i in range(n_mois):
        cout_total += frais_approvisionnement + installations[i]
        # installation dans le mois
        stock += installations[i] - installations[i]
        cout_total += stock * cout_stockage
        cout_mensuel[i + 1] = cout_total

    return cout_une_fois, cout_mensuel

# --- fonction principale ---
# donne uniquement les couts finaux
def calcul_couts_strategies(installations, frais_approvisionnement, cout_stockage):
    cout_une_fois, cout_mensuel = calcul_couts_de_base( installations, frais_approvisionnement, cout_stockage)

    total_directeur_achats = cout_une_fois[-1]  # achat au mois 1
    cout_directeur_financier = cout_mensuel[-1]  # achat chaque mois

    return {
        "directeur_achats": total_directeur_achats,
        "directeur_financier": cout_directeur_financier,
    }


# --- Visualisation des résultats de deux façons : évoltion des coûts par mois par strat et achats optimaux à faire ---

def tracer_graphique(installations, frais_approvisionnement, cout_stockage, precedents, n_mois):
    path_optimal = reconstruct_chemin_graphe(precedents, 0, n_mois)
    mois = list(range(n_mois + 1))  # de 0 à 6 mois donc 7 éléments

    # --- couts des deux stratégies de base ---
    cout_une_fois, cout_mensuel = calcul_couts_de_base(
        installations, frais_approvisionnement, cout_stockage
    )

    # strat 3 : optimale, obtenue par l'algo
    cout_optimale = [0] * (n_mois + 1)
    achats_optimal = [0] * n_mois  # pour le graphique des barres
    
    cout_actuel = 0
    stock = 0
    next_supply_index = 1  # index dans path_optimal
    
    for i in range(n_mois):
        # vérifier si c'est un mois d'approvisionnement
        if next_supply_index < len(path_optimal) and i == path_optimal[next_supply_index-1]:
            mois_debut = path_optimal[next_supply_index-1]
            mois_fin = path_optimal[next_supply_index]
            
            # quantité achetée
            achats_optimal[i] = sum(installations[mois_debut:mois_fin])
            
            # calculer le coût de l'approvisionnement
            cout_actuel += frais_approvisionnement + achats_optimal[i]
            stock += achats_optimal[i]
            next_supply_index += 1
        
        # installations du mois
        stock -= installations[i]
        
        # stockage des cabines restantes
        cout_stockage_mois = stock * cout_stockage
        cout_actuel += cout_stockage_mois
        
        cout_optimale[i+1] = cout_actuel

    # création des graphiques
    fig, ax = plt.subplots(2, 1, figsize=(12, 12))
    
    # graphique 1: comparaison des évolutions des coûts
    ax[0].plot(mois, cout_mensuel, label="Achats mensuels", color='blue', marker='o')
    ax[0].plot(mois, cout_une_fois, label="Achat en une fois", color='red', linestyle='--', marker='x')
    ax[0].plot(mois, cout_optimale, label="Méthode optimale", color='green', marker='s')
    
    ax[0].set_xlabel('Mois')
    ax[0].set_ylabel('Coût total (€)')
    ax[0].set_title("Comparaison des stratégies d'approvisionnement")
    ax[0].legend()
    ax[0].grid(True)
    
    # graphique 2: achats optimaux (distribués sur les 6 mois)
    mois_labels = [f"Mois {i+1}" for i in range(n_mois)]
    ax[1].bar(mois_labels, achats_optimal, color='lightgreen')
    ax[1].set_xlabel('Mois')
    ax[1].set_ylabel('Nombre de cabines')
    ax[1].set_title('Stratégie optimale: Quantités commandées par mois')
    for i, v in enumerate(achats_optimal):
        if v > 0:
            ax[1].text(i, v + 20, str(v), ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    return fig, ax     # pour modifier ensuite dans l'interface     
             



def visualize_graph(installations, frais_approvisionnement, cout_stockage, precedents, n_mois):
    fig, _ = tracer_graphique(installations, frais_approvisionnement, cout_stockage, precedents, n_mois)
    fig.savefig('comparaison_strategies.png')
    plt.show()
    return True



def tests_algos():
    print("=== Tests des algorithmes ===")

    print("Test de detect_cycle:")
    # sans cycle
    graph_no_cycle = {0: [1], 1: [2], 2: [3], 3: [4], 4: [5], 5: []}
    expected_no_cycle = False
    result_no_cycle = detect_cycle(graph_no_cycle)
    print(f"Devrait afficher : {expected_no_cycle} \nAffiche : {result_no_cycle}")
    # avec cycle
    graph_with_cycle = {0: [1], 1: [2], 2: [0]}  # Cycle entre 0, 1 et 2
    expected_with_cycle = True
    result_with_cycle = detect_cycle(graph_with_cycle)
    print(f"Devrait afficher : {expected_with_cycle}, \nAffiche : {result_with_cycle}")
    
    if result_with_cycle == expected_with_cycle and result_no_cycle == expected_no_cycle:
        print("Fonction detect_cycle bien implémentée")
    else:
        print("Fonction detect_cycle incorrectement implémentée")

    print("\nTest de la fonction dijkstra:")
    # Nouveau graphe pour le test
    G = nx.DiGraph()
    G.add_weighted_edges_from([(0, 1, 10), (0, 2, 5), (1, 2, 2), (1, 3, 1), (2, 3, 9), (3, 4, 4)])
    distances, _ = dijkstra(G, 0, 4)
    expected_distances = {0: 0, 1: 7, 2: 5, 3: 8, 4: 12}
    print(f"Devrait afficher : {expected_distances}")
    print(f"Affiche : {distances}")
    if distances == {0: 0, 1: 7, 2: 5, 3: 8, 4: 12}:
        print("Fonction dijkstra bien implémentée")
    else:
        print("Fonction dijkstra incorrectement implémentée")

    print("\nTest de la fonction reconstruct_chemin_graphe:")
    path = reconstruct_chemin_graphe(_, 0, 4)
    print(f"Chemin optimal : {path}")
    expected_path = [0, 2, 1, 3, 4]
    if path == expected_path:
        print("Fonction reconstruct_chemin_graphe bien implémentée")
    else:
        print("Fonction reconstruct_chemin_graphe incorrectement implémentée")


# --- Main: Fonction principale ---
def main():
    tests_algos()

    print("\n\n=== CostGraph : Système d'optimisation des approvisionnements de cabines téléphoniques ===\n")
    
    installations, frais_approvisionnement, cout_stockage = load_data()
    print(f"Données chargées :")
    print(f"- Installations mensuelles: {installations}")
    print(f"- Frais fixes d'approvisionnement: {frais_approvisionnement} €")
    print(f"- Coût de stockage par cabine par mois: {cout_stockage} €\n")
    
    # Création du graphe
    G, n_mois = init_graphe(installations, frais_approvisionnement, cout_stockage)
    
    # Vérification d'acyclicité
    if detect_cycle(G):
        print("ERREUR: Le graphe contient des cycles, ce qui ne devrait pas être le cas.")
        return
    else:
        print("Vérification d'acyclicité : OK - Le graphe ne contient pas de cycles.\n")
    
    # Recherche du plus court chemin (stratégie optimale)
    distances, precedents = dijkstra(G, 0, n_mois)
    if n_mois not in distances:
        print("ERREUR: Aucun chemin trouvé du mois 0 au mois final.")
        return
    
    # Reconstruire le chemin optimal
    path = reconstruct_chemin_graphe(precedents, 0, n_mois)
    cout_optimal = distances[n_mois]
    
    # Calculer les coûts des autres stratégies
    autres_couts = calcul_couts_strategies(installations, frais_approvisionnement, cout_stockage)
    
    # Afficher les résultats
    print("=== Résultats de l'analyse ===\n")
    print("1. Stratégie optimale:")
    print(f"   Coût total: {cout_optimal:.2f} €")
    print("   Politique d'approvisionnement:")
    
    for i in range(1, len(path)):
        mois_debut = path[i-1]
        mois_fin = path[i]
        cabines = sum(installations[mois_debut:mois_fin])
        cout_appro = G[mois_debut][mois_fin]['weight']
        print(f"   - Au début du mois {mois_debut+1}, approvisionner {cabines} cabines pour les mois {mois_debut+1} à {mois_fin}")
        print(f"     Coût: {cout_appro:.2f} €")
    
    print("\n2. Comparaison avec les autres stratégies:")
    print(f"   Stratégie du directeur des achats (tout au mois 1): {autres_couts['directeur_achats']:.2f} €")
    print(f"   Stratégie du directeur financier (mois par mois): {autres_couts['directeur_financier']:.2f} €")
    
    economie_vs_achats = autres_couts['directeur_achats'] - cout_optimal
    economie_vs_financier = autres_couts['directeur_financier'] - cout_optimal
    
    print(f"\n3. Économies réalisées avec la stratégie optimale:")
    print(f"   Par rapport à la stratégie du directeur des achats: {economie_vs_achats:.2f} € ({economie_vs_achats/autres_couts['directeur_achats']*100:.2f}%)")
    print(f"   Par rapport à la stratégie du directeur financier: {economie_vs_financier:.2f} € ({economie_vs_financier/autres_couts['directeur_financier']*100:.2f}%)")
    
    visualize_graph(installations, frais_approvisionnement, cout_stockage, precedents, n_mois)
    
    # résumé pour les directeurs (il faut montrer ce qui peut etre économisé grâce à la strat optimale)
    print("\n=== Résumé pour la présentation aux directeurs ===\n")

    print("La solution optimale permet d'équilibrer les coûts fixes d'approvisionnement et les coûts de stockage.")
    print(f"Cette approche permet d'économiser {economie_vs_achats:.2f} € par rapport à un approvisionnement unique")
    print(f"et {economie_vs_financier:.2f} € par rapport à des approvisionnements mensuels.")
    print("Cette optimisation maximise la rentabilité de l'entreprise tout en minimisant les risques liés aux stocks.")

if __name__ == "__main__":
    main()