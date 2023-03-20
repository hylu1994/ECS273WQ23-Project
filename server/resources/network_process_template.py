import networkx as nx
import numpy as np

# def _prepare_toy_data() -> tuple[list[int], list[tuple]]:
#     # define undirected network data.
#     nodes = [0, 1, 2, 3, 4, 5, 122, 6, 7, 8, 9, 120] # 10 nodes indexed from 0 to 9.
#     edges = [(0, 1), (0, 2), (0, 3), (0, 6), (0, 7), (0, 9), 
#              (1, 2), (1, 5), (1, 6), (1, 7), 
#              (2, 4), (2, 9), 
#              (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), 
#              (4, 6), 
#              (5, 7), (5, 9), 
#              (6, 8), (4, 9), 
#              (7, 8), 
#              (8, 9)] # 23 random edges between these node pairs.
#     return nodes, edges

# def contsruct_networkx(nodes: list[int], edges: list[tuple]):
def contsruct_networkx(nodes, edges):
    # if not nodes or not edges: 
    #     nodes, edges = _prepare_toy_data()
    # construct a network using networkx and the predefined nodes and edges.
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    # Networkx graph types
    # Reference: https://networkx.org/documentation/stable/reference/classes/index.html
    return G

def find_most_influential(G):
    eigenvectors: dict = nx.eigenvector_centrality(G) # return dict type with node index as key and the node's eigenvector as value.
    eigenvectors_np = np.array(list(eigenvectors.values())) # turn the eigenvector values into numpy array.
    node_most_influential = list(eigenvectors.keys())[np.argmax(eigenvectors_np)] # find the key (node index) of the largest eigenvector.
    
    return node_most_influential

def force_layout(G):
    pos = nx.spring_layout(G)
    position = []
    for i in pos.keys():
        tmp = {"id": int(i), "x": pos[i][0], "y": pos[i][1]}
        position.append([pos[i][0], pos[i][1]])

    return position


###################        Example     ################### 
# nodes, edges = _prepare_toy_data()
# toy_data_network = contsruct_networkx(nodes, edges)
# node_most_influential = find_most_influential(toy_data_network)
# pos = force_layout(toy_data_network)
# print(pos)
##########################################################
