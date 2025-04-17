import networkx as nx
import heapq
import matplotlib.pyplot as plt


def load_data():
    installations = [200, 200, 300, 700, 1000, 200]
    frais_approvisionnement = 2000 
    cout_stockage = 2
    
    return installations, frais_approvisionnement, cout_stockage

# --- initialisation graphe ---
def create_graph(installations, frais_approvisionnement, cout_stockage):
    # grace a la bibliotheque networkx
    G = nx.DiGraph()
    # ajouter noeud par mois
    n_months = len(installations) 
    for i in range(n_months + 1):
        G.add_node(i)
    # arcs avec les couts d'approvisionnement + stockage
    for i in range(n_months):
        for j in range(i + 1, n_months + 1):
            cout = frais_approvisionnement
            cout_cabines = sum(installations[i:j])
            cout_stockage_total = 0
            for k in range(i, j-1):
                # calcul des cabines en attente chaque mois
                cabines_en_attente = sum(installations[k+1:j])
                cout_stockage_total += cabines_en_attente * cout_stockage
            cout_total = cout + cout_cabines + cout_stockage_total
            G.add_edge(i, j, weight=cout_total)
    
    return G, n_months

# --- détection des cycles  ---
def detect_cycle(graph):
    visited = set()  # sommets visités
    rec_stack = set()  # pile de récursion pour détecter les cycles

    def dfs(v): #on va definir l'algo dfs vu en cours ici
        visited.add(v)
        rec_stack.add(v)

        for neighbor in graph[v]:
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True  # cycle détecté

        rec_stack.remove(v)
        return False
    
    # et on va l'utiliser ici
    for node in graph:
        if node not in visited:
            if dfs(node):
                return True # si cycle détecté

    return False  # sinon

# --- Dijkstra pour trouver le chemin optimal ---
def dijkstra(graph, start, end):
    # couts pour tous les sommets
    min_heap = [(0, start)]  # (coût, sommet)
    distances = {start: 0}
    predecessors = {start: None}  # prédécesseurs dans un dictionnaire (pour reconstruire le chemin après)

    while min_heap:
        current_dist, current_node = heapq.heappop(min_heap)
        # arret si on est a la fin
        if current_node == end:
            break

        # Si sommet déjà exploré avec coût plus bas on le saute
        if current_dist > distances.get(current_node, float('inf')):
            continue
        
        # voir les voisins
        for neighbor in graph[current_node]:
            edge_weight = graph[current_node][neighbor]['weight']
            distance = current_dist + edge_weight
            if distance < distances.get(neighbor, float('inf')):
                distances[neighbor] = distance
                predecessors[neighbor] = current_node  # suivre ce chemin
                heapq.heappush(min_heap, (distance, neighbor))

    return distances, predecessors


# --- reconstruction du chemin optimal ---
def reconstruct_path(predecessors, start, end):
    if end not in predecessors and end != start:
        return []  # pas de chemin trouvé
        
    path = []
    current_node = end
    while current_node is not None:
        path.append(current_node)
        current_node = predecessors.get(current_node)
    path.reverse()  # on inverse le chemin pour qu'il soit bien du début à la fin
    return path

# --- Calcul des coûts pour les différentes stratégies ---
def calculate_cost_strategies(installations, frais_approvisionnement, cout_stockage):
    n_months = len(installations)
    total_cabines = sum(installations)
    
    # strat 1 : tout au mois 1 (directeur des achats)
    cout_achat_directeur_achats = frais_approvisionnement + total_cabines

    # coût de stockage
    cout_stockage_directeur_achats = 0
    cabines_restantes = total_cabines
    for i in range(n_months):
        cabines_restantes -= installations[i]
        cout_stockage_directeur_achats += cabines_restantes * cout_stockage
    
    total_directeur_achats = cout_achat_directeur_achats + cout_stockage_directeur_achats
    
    # strat 2 : acheter chaque mois (directeur financier)
    cout_directeur_financier = 0
    for i in range(n_months):
        cout_directeur_financier += frais_approvisionnement + installations[i]
    # et donc pas de frais de stockage avec sa methode

    return {
        "directeur_achats": total_directeur_achats,
        "directeur_financier": cout_directeur_financier
    }

# --- Visualisation des résultats de deux façons : évoltion des coûts par mois par strat et achats optimaux à faire ---
def visualize_graph(installations, frais_approvisionnement, cout_stockage, predecessors, n_months):
    try:
        mois = list(range(n_months + 1))  # de 0 à 6 mois donc 7 éléments
        
        # strat 1 : tout en une fois
        cout_une_fois = [0] * (n_months + 1)
        total_cost = frais_approvisionnement + sum(installations)
        cout_une_fois[1] = total_cost  # Commande au mois 1
        
        stock = sum(installations)
        for i in range(n_months):
            stock -= installations[i]
            cout_stockage_mois = stock * cout_stockage
            total_cost += cout_stockage_mois
            cout_une_fois[i+1] = total_cost

        # strat 2 : achats mensuels
        cout_mensuel = [0] * (n_months + 1)
        stock = 0
        total_cost = 0
        
        for i in range(n_months):
            # commande au début du mois i+1 (nœud i dans le graphe)
            total_cost += frais_approvisionnement + installations[i]
            stock += installations[i]
            
            # installation pendant ce mois là
            stock -= installations[i]
            
            # stockage à la fin du mois (pour le mois suivant)
            cout_stockage_mois = stock * cout_stockage
            total_cost += cout_stockage_mois
            
            cout_mensuel[i+1] = total_cost

        # strat 3 : optimale, obtenue par l'algo
        path_optimal = reconstruct_path(predecessors, 0, n_months)
        cout_optimale = [0] * (n_months + 1)
        achats_optimal = [0] * n_months  # pour le graphique des barres
        
        current_cost = 0
        stock = 0
        next_supply_index = 1  # index dans path_optimal
        
        for i in range(n_months):
            # vérifier si c'est un mois d'approvisionnement
            if next_supply_index < len(path_optimal) and i == path_optimal[next_supply_index-1]:
                mois_debut = path_optimal[next_supply_index-1]
                mois_fin = path_optimal[next_supply_index]
                
                # quantité achetée
                achats_optimal[i] = sum(installations[mois_debut:mois_fin])
                
                # calculer le coût de l'approvisionnement
                current_cost += frais_approvisionnement + achats_optimal[i]
                stock += achats_optimal[i]
                next_supply_index += 1
            
            # installations du mois
            stock -= installations[i]
            
            # stockage des cabines restantes
            cout_stockage_mois = stock * cout_stockage
            current_cost += cout_stockage_mois
            
            cout_optimale[i+1] = current_cost

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
        mois_labels = [f"Mois {i+1}" for i in range(n_months)]
        ax[1].bar(mois_labels, achats_optimal, color='lightgreen')
        ax[1].set_xlabel('Mois')
        ax[1].set_ylabel('Nombre de cabines')
        ax[1].set_title('Stratégie optimale: Quantités commandées par mois')
        for i, v in enumerate(achats_optimal):
            if v > 0:
                ax[1].text(i, v + 20, str(v), ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig('comparaison_strategies.png')
        plt.show()
        
        return True
    except Exception as e:
        print(f"Erreur lors de la génération des graphiques: {e}")
        return False


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

    print("\nTest de la fonction reconstruct_path:")
    path = reconstruct_path(_, 0, 4)
    print(f"Chemin optimal : {path}")
    expected_path = [0, 2, 1, 3, 4]
    if path == expected_path:
        print("Fonction reconstruct_path bien implémentée")
    else:
        print("Fonction reconstruct_path incorrectement implémentée")


# --- Main: Fonction principale ---
def main():
    tests_algos()

    print("\n\n=== Système d'optimisation des approvisionnements de cabines téléphoniques ===\n")
    
    installations, frais_approvisionnement, cout_stockage = load_data()
    print(f"Données chargées :")
    print(f"- Installations mensuelles: {installations}")
    print(f"- Frais fixes d'approvisionnement: {frais_approvisionnement} €")
    print(f"- Coût de stockage par cabine par mois: {cout_stockage} €\n")
    
    # Création du graphe
    G, n_months = create_graph(installations, frais_approvisionnement, cout_stockage)
    
    # Vérification d'acyclicité
    if detect_cycle(G):
        print("ERREUR: Le graphe contient des cycles, ce qui ne devrait pas être le cas.")
        return
    else:
        print("Vérification d'acyclicité : OK - Le graphe ne contient pas de cycles.\n")
    
    # Recherche du plus court chemin (stratégie optimale)
    distances, predecessors = dijkstra(G, 0, n_months)
    if n_months not in distances:
        print("ERREUR: Aucun chemin trouvé du mois 0 au mois final.")
        return
    
    # Reconstruire le chemin optimal
    path = reconstruct_path(predecessors, 0, n_months)
    cout_optimal = distances[n_months]
    
    # Calculer les coûts des autres stratégies
    autres_couts = calculate_cost_strategies(installations, frais_approvisionnement, cout_stockage)
    
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
    
    visualize_graph(installations, frais_approvisionnement, cout_stockage, predecessors, n_months)
    
    # résumé pour les directeurs (il faut montrer ce qui peut etre économisé grâce à la strat optimale)
    print("\n=== Résumé pour la présentation aux directeurs ===\n")

    print("La solution optimale permet d'équilibrer les coûts fixes d'approvisionnement et les coûts de stockage.")
    print(f"Cette approche permet d'économiser {economie_vs_achats:.2f} € par rapport à un approvisionnement unique")
    print(f"et {economie_vs_financier:.2f} € par rapport à des approvisionnements mensuels.")
    print("Cette optimisation maximise la rentabilité de l'entreprise tout en minimisant les risques liés aux stocks.")

if __name__ == "__main__":
    main()