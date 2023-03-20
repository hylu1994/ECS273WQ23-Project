import pandas as pd
import numpy as np
import csv
import numpy as np
import json

from resources.network_process_template import contsruct_networkx, find_most_influential, force_layout
#from resources.text_processing_template import preprocess
#from resources.time_processing_template import prepare_time_template_data, apply_arima, apply_sarima
from sklearn.datasets import load_wine
from resources.hd_processing_template import perform_PCA, perform_TSNE

import inference.explainer_main as gnnexplainer
import inference.node_emb as node_emb
import networkx as nx
from grakel import Graph

def get_nodes(index):
    print(index)
    return node_emb.reddit_node(index)
# get_nodes(38)

def getForced(index):
    print(index)
    Gs_original, _ = gnnexplainer.get_inference_graph(index)
    nodes = [{'id': int(value)} for key, value in Gs_original[0][0].items()]
    edges = [{
        'source': item[0],
        'target': item[1]
    } for item in Gs_original[0][1]]

    # print("check data format: ", Gs_original)
    # print("nodes: ", nodes)
    # print("edges: ", edges)

    return list(nodes), list(edges)
# getForced()

def construct_graphlets(k=5):
    targets = []
    if k==5:
        # graphlet5_1
        G = nx.Graph()
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(4,5)
        G_nodes = {list(G.nodes())[i]: str(list(G.nodes())[i]) for i in range(len(list(G.nodes())))}
        G_edges = []
        for (edge_s, edge_t) in G.edges():
            G_edges.append((edge_s, edge_t))
            G_edges.append((edge_t, edge_s))
        G_tmp = Graph(initialization_object=G_edges, node_labels=G_nodes)
        targets.append(G_tmp)

        # graphlet5_2
        G = nx.Graph()
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(3,5)
        G_nodes = {list(G.nodes())[i]: str(list(G.nodes())[i]) for i in range(len(list(G.nodes())))}
        G_edges = []
        for (edge_s, edge_t) in G.edges():
            G_edges.append((edge_s, edge_t))
            G_edges.append((edge_t, edge_s))
        G_tmp = Graph(initialization_object=G_edges, node_labels=G_nodes)
        targets.append(G_tmp)

        # graphlet5_3
        G = nx.Graph()
        G.add_edge(1,2)
        G.add_edge(1,3)
        G.add_edge(1,4)
        G.add_edge(1,5)
        G_nodes = {list(G.nodes())[i]: str(list(G.nodes())[i]) for i in range(len(list(G.nodes())))}
        G_edges = []
        for (edge_s, edge_t) in G.edges():
            G_edges.append((edge_s, edge_t))
            G_edges.append((edge_t, edge_s))
        G_tmp = Graph(initialization_object=G_edges, node_labels=G_nodes)
        targets.append(G_tmp)

        # graphlet5_4
        G = nx.Graph()
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(3,5)
        G.add_edge(2,5)
        G_nodes = {list(G.nodes())[i]: str(list(G.nodes())[i]) for i in range(len(list(G.nodes())))}
        G_edges = []
        for (edge_s, edge_t) in G.edges():
            G_edges.append((edge_s, edge_t))
            G_edges.append((edge_t, edge_s))
        G_tmp = Graph(initialization_object=G_edges, node_labels=G_nodes)
        targets.append(G_tmp)

        # graphlet5_5
        G = nx.Graph()
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(3,5)
        G.add_edge(4,5)
        G_nodes = {list(G.nodes())[i]: str(list(G.nodes())[i]) for i in range(len(list(G.nodes())))}
        G_edges = []
        for (edge_s, edge_t) in G.edges():
            G_edges.append((edge_s, edge_t))
            G_edges.append((edge_t, edge_s))
        G_tmp = Graph(initialization_object=G_edges, node_labels=G_nodes)
        targets.append(G_tmp)

        # graphlet5_6
        G = nx.Graph()
        G.add_edge(1,2)
        G.add_edge(1,3)
        G.add_edge(1,4)
        G.add_edge(1,5)
        G.add_edge(2,3)
        G_nodes = {list(G.nodes())[i]: str(list(G.nodes())[i]) for i in range(len(list(G.nodes())))}
        G_edges = []
        for (edge_s, edge_t) in G.edges():
            G_edges.append((edge_s, edge_t))
            G_edges.append((edge_t, edge_s))
        G_tmp = Graph(initialization_object=G_edges, node_labels=G_nodes)
        targets.append(G_tmp)

        # graphlet5_7
        G = nx.Graph()
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(4,5)
        G.add_edge(1,5)
        G_nodes = {list(G.nodes())[i]: str(list(G.nodes())[i]) for i in range(len(list(G.nodes())))}
        G_edges = []
        for (edge_s, edge_t) in G.edges():
            G_edges.append((edge_s, edge_t))
            G_edges.append((edge_t, edge_s))
        G_tmp = Graph(initialization_object=G_edges, node_labels=G_nodes)
        targets.append(G_tmp)

        # graphlet5_8
        G = nx.Graph()
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(4,5)
        G.add_edge(2,5)
        G_nodes = {list(G.nodes())[i]: str(list(G.nodes())[i]) for i in range(len(list(G.nodes())))}
        G_edges = []
        for (edge_s, edge_t) in G.edges():
            G_edges.append((edge_s, edge_t))
            G_edges.append((edge_t, edge_s))
        G_tmp = Graph(initialization_object=G_edges, node_labels=G_nodes)
        targets.append(G_tmp)

        # graphlet5_9
        G = nx.Graph()
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(4,5)
        G.add_edge(2,4)
        G.add_edge(2,5)
        G_nodes = {list(G.nodes())[i]: str(list(G.nodes())[i]) for i in range(len(list(G.nodes())))}
        G_edges = []
        for (edge_s, edge_t) in G.edges():
            G_edges.append((edge_s, edge_t))
            G_edges.append((edge_t, edge_s))
        G_tmp = Graph(initialization_object=G_edges, node_labels=G_nodes)
        targets.append(G_tmp)

        # graphlet5_10
        G = nx.Graph()
        G.add_edge(1,2)
        G.add_edge(1,3)
        G.add_edge(1,4)
        G.add_edge(1,5)
        G.add_edge(2,3)
        G.add_edge(4,5)
        G_nodes = {list(G.nodes())[i]: str(list(G.nodes())[i]) for i in range(len(list(G.nodes())))}
        G_edges = []
        for (edge_s, edge_t) in G.edges():
            G_edges.append((edge_s, edge_t))
            G_edges.append((edge_t, edge_s))
        G_tmp = Graph(initialization_object=G_edges, node_labels=G_nodes)
        targets.append(G_tmp)

        # graphlet5_11
        G = nx.Graph()
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(4,5)
        G.add_edge(2,5)
        G.add_edge(3,5)
        G_nodes = {list(G.nodes())[i]: str(list(G.nodes())[i]) for i in range(len(list(G.nodes())))}
        G_edges = []
        for (edge_s, edge_t) in G.edges():
            G_edges.append((edge_s, edge_t))
            G_edges.append((edge_t, edge_s))
        G_tmp = Graph(initialization_object=G_edges, node_labels=G_nodes)
        targets.append(G_tmp)

        # graphlet5_12
        G = nx.Graph()
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(1,4)
        G.add_edge(2,5)
        G.add_edge(4,5)
        G_nodes = {list(G.nodes())[i]: str(list(G.nodes())[i]) for i in range(len(list(G.nodes())))}
        G_edges = []
        for (edge_s, edge_t) in G.edges():
            G_edges.append((edge_s, edge_t))
            G_edges.append((edge_t, edge_s))
        G_tmp = Graph(initialization_object=G_edges, node_labels=G_nodes)
        targets.append(G_tmp)

        # graphlet5_13
        G = nx.Graph()
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(1,4)
        G.add_edge(2,5)
        G.add_edge(3,5)
        G_nodes = {list(G.nodes())[i]: str(list(G.nodes())[i]) for i in range(len(list(G.nodes())))}
        G_edges = []
        for (edge_s, edge_t) in G.edges():
            G_edges.append((edge_s, edge_t))
            G_edges.append((edge_t, edge_s))
        G_tmp = Graph(initialization_object=G_edges, node_labels=G_nodes)
        targets.append(G_tmp)

        # graphlet5_14
        G = nx.Graph()
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(1,4)
        G.add_edge(2,4)
        G.add_edge(2,5)
        G.add_edge(4,5)
        G_nodes = {list(G.nodes())[i]: str(list(G.nodes())[i]) for i in range(len(list(G.nodes())))}
        G_edges = []
        for (edge_s, edge_t) in G.edges():
            G_edges.append((edge_s, edge_t))
            G_edges.append((edge_t, edge_s))
        G_tmp = Graph(initialization_object=G_edges, node_labels=G_nodes)
        targets.append(G_tmp)

        # graphlet5_15
        G = nx.Graph()
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(2,4)
        G.add_edge(2,5)
        G.add_edge(3,5)
        G.add_edge(4,5)
        G_nodes = {list(G.nodes())[i]: str(list(G.nodes())[i]) for i in range(len(list(G.nodes())))}
        G_edges = []
        for (edge_s, edge_t) in G.edges():
            G_edges.append((edge_s, edge_t))
            G_edges.append((edge_t, edge_s))
        G_tmp = Graph(initialization_object=G_edges, node_labels=G_nodes)
        targets.append(G_tmp)

        # graphlet5_16
        G = nx.Graph()
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(4,5)
        G.add_edge(1,5)
        G.add_edge(2,4)
        G.add_edge(2,5)
        G_nodes = {list(G.nodes())[i]: str(list(G.nodes())[i]) for i in range(len(list(G.nodes())))}
        G_edges = []
        for (edge_s, edge_t) in G.edges():
            G_edges.append((edge_s, edge_t))
            G_edges.append((edge_t, edge_s))
        G_tmp = Graph(initialization_object=G_edges, node_labels=G_nodes)
        targets.append(G_tmp)

        # graphlet5_17
        G = nx.Graph()
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(1,4)
        G.add_edge(1,5)
        G.add_edge(2,5)
        G.add_edge(3,5)
        G_nodes = {list(G.nodes())[i]: str(list(G.nodes())[i]) for i in range(len(list(G.nodes())))}
        G_edges = []
        for (edge_s, edge_t) in G.edges():
            G_edges.append((edge_s, edge_t))
            G_edges.append((edge_t, edge_s))
        G_tmp = Graph(initialization_object=G_edges, node_labels=G_nodes)
        targets.append(G_tmp)

        # graphlet5_18
        G = nx.Graph()
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(1,4)
        G.add_edge(1,5)
        G.add_edge(2,5)
        G.add_edge(4,5)
        G.add_edge(2,4)
        G_nodes = {list(G.nodes())[i]: str(list(G.nodes())[i]) for i in range(len(list(G.nodes())))}
        G_edges = []
        for (edge_s, edge_t) in G.edges():
            G_edges.append((edge_s, edge_t))
            G_edges.append((edge_t, edge_s))
        G_tmp = Graph(initialization_object=G_edges, node_labels=G_nodes)
        targets.append(G_tmp)

        # graphlet5_19
        G = nx.Graph()
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(1,4)
        G.add_edge(1,5)
        G.add_edge(2,5)
        G.add_edge(3,5)
        G.add_edge(4,5)
        G_nodes = {list(G.nodes())[i]: str(list(G.nodes())[i]) for i in range(len(list(G.nodes())))}
        G_edges = []
        for (edge_s, edge_t) in G.edges():
            G_edges.append((edge_s, edge_t))
            G_edges.append((edge_t, edge_s))
        G_tmp = Graph(initialization_object=G_edges, node_labels=G_nodes)
        targets.append(G_tmp)

        # graphlet5_20
        G = nx.Graph()
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(1,4)
        G.add_edge(1,5)
        G.add_edge(2,5)
        G.add_edge(4,5)
        G.add_edge(2,4)
        G.add_edge(3,5)
        G_nodes = {list(G.nodes())[i]: str(list(G.nodes())[i]) for i in range(len(list(G.nodes())))}
        G_edges = []
        for (edge_s, edge_t) in G.edges():
            G_edges.append((edge_s, edge_t))
            G_edges.append((edge_t, edge_s))
        G_tmp = Graph(initialization_object=G_edges, node_labels=G_nodes)
        targets.append(G_tmp)

        # graphlet5_21
        G = nx.Graph()
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(4,5)
        G.add_edge(1,5)
        G.add_edge(1,3)
        G.add_edge(1,4)
        G.add_edge(2,4)
        G.add_edge(2,5)
        G.add_edge(3,5)
        G_nodes = {list(G.nodes())[i]: str(list(G.nodes())[i]) for i in range(len(list(G.nodes())))}
        G_edges = []
        for (edge_s, edge_t) in G.edges():
            G_edges.append((edge_s, edge_t))
            G_edges.append((edge_t, edge_s))
        G_tmp = Graph(initialization_object=G_edges, node_labels=G_nodes)
        targets.append(G_tmp)
    return targets

def processPrimitiveSubgraph(graph_index):
    return 

def overview_scatterplot():

    # dist = []
    # with open("/Users/hsiao-yinglu/hsiaoyinglu/network_projects/EHR project/GNNInterpreter-visualization/server/data/orig_graphs.json", "r") as outfile:
    #     dist = json.load(outfile)

    # graphlets_orig = []
    # for i in range(len(dist)):
    #     graphlets_orig.append(np.array(dist[i]["graphlets_orig"]))
    # # print(np.array(graphlets_orig).shape)
    
    # dr_dist_orig = perform_PCA(np.array(graphlets_orig), comp=1)
    # print(dr_dist_orig)

    # for i in range(len(dist)):
    #     dist[i]["PCA1_graphlets_orig"] = dr_dist_orig[i][0]
    #     # dist[i]["PCA21_graphlets_orig"] = dr_dist_orig[i][0]
    #     # dist[i]["PCA22_graphlets_orig"] = dr_dist_orig[i][1]
    #     # dist[i]["PCA21_graphlets_deno"] = dr_dist_deno[i][0]
    #     # dist[i]["PCA22_graphlets_deno"] = dr_dist_deno[i][1]
    
    # for i in range(len(dist)):
    #     node_embs = []
    #     dist[i]["PCA1_node_emb"] = []
    #     dist[i]["PCA21_node_emb"] = []
    #     dist[i]["PCA22_node_emb"] = []
    #     node_keys = list(dist[i]["node_emb"].keys())
    #     for j in range(len(node_keys)):
    #         node_embs.append(np.array(dist[i]["node_emb"][node_keys[j]]))   
    #     dr_dist_orig = perform_PCA(np.array(node_embs), comp=1)
    #     dr_dist_orig_2 = perform_PCA(np.array(node_embs), comp=2)
    
    #     for j in range(len(node_keys)):
    #         dist[i]["PCA1_node_emb"].append(dr_dist_orig[j][0])
    #         dist[i]["PCA21_node_emb"].append(dr_dist_orig_2[j][0])
    #         dist[i]["PCA22_node_emb"].append(dr_dist_orig_2[j][1])
        
        # print(dist[i]["id"], dist[i]["PCA21_node_emb"], dist[i]["PCA22_node_emb"])

    
    # with open("/Users/hsiao-yinglu/hsiaoyinglu/network_projects/EHR project/GNNInterpreter-visualization/server/data/orig_graphs.json", "w") as outfile:
    #     json.dump(dist, outfile)

    dist = []
    with open("../server/data/kernel_prob.json", "r") as outfile:
        dist = json.load(outfile)
    
    return dist

def instance_emb():
    dist = []
    with open("../server/data/orig_graphs.json", "r") as outfile:
        dist = json.load(outfile)
    
    return dist

# test = overview_scatterplot()


def overview_scatterplot_preprocess(graph_index):
    graphlets = construct_graphlets(5)
    dist = gnnexplainer.inference_primitive(graph_index, graphlets)
    # dist_emb = []
    # for i in range(len(graph_index)):
    #     embs = get_nodes(graph_index[i])
    #     dist_emb.append({'id': graph_index[i], 'node_emb': embs})
    # print(dist)

    # with open("/Users/hsiao-yinglu/hsiaoyinglu/network_projects/EHR project/GNNInterpreter-visualization/server/data/orig_graphs_large.json", "w") as outfile:
        # json.dump(dist, outfile)


    # dist = []
    # with open("/Users/hsiao-yinglu/hsiaoyinglu/network_projects/EHR project/GNNInterpreter-visualization/server/data/kernel_prob.json", "r") as outfile:
    #     dist = json.load(outfile)
    # graphlets_orig = []
    # graphlets_deno = []
    # for i in range(len(dist)):
    #     graphlets_orig.append(np.array(dist[i]["graphlets_orig"]))
    #     graphlets_deno.append(np.array(dist[i]["graphlets_deno"]))
    # # print(np.array(graphlets_orig).shape)
    
    # # dr_dist_orig = perform_PCA(np.array(graphlets_orig), comp=2)
    # # dr_dist_deno = perform_PCA(np.array(graphlets_deno), comp=2)
    # # print(dr_dist_orig)
    # # print(dr_dist_deno)

    # # graphlets_orig_average = []
    # # for i in range(len(graphlets_orig[0])):
    # #     graphlets_orig_average.append(np.sum(np.array(graphlets_orig)[:, i])/100)
    # # print(graphlets_orig_average)
    
    # for i in range(len(dist)):
    #     dist[i]["PCA21_graphlets_orig"] = dr_dist_orig[i][0]
    #     dist[i]["PCA22_graphlets_orig"] = dr_dist_orig[i][1]
    #     dist[i]["PCA21_graphlets_deno"] = dr_dist_deno[i][0]
    #     dist[i]["PCA22_graphlets_deno"] = dr_dist_deno[i][1]
    
    # with open("/Users/hsiao-yinglu/hsiaoyinglu/network_projects/EHR project/GNNInterpreter-visualization/server/data/kernel_prob.json", "w") as outfile:
    #     json.dump(dist, outfile)

    # dist = []
    # with open("/Users/hsiao-yinglu/hsiaoyinglu/network_projects/EHR project/GNNInterpreter-visualization/server/data/kernel_prob.json", "r") as outfile:
    #     dist = json.load(outfile)
    
    return dist

# test = overview_scatterplot_preprocess([i for i in range(4)])
# test = processPrimitiveSubgraph([70, 99])
# test = processPrimitiveSubgraph([i for i in range(100)])

# def processExample(method: str = 'PCA') -> tuple[list[dict], list[int]]:
def processExample(method='PCA'):
    data: dict = load_wine()
    X: np.ndarray = data.data
    y: np.ndarray = data.target
    #feat_names: np.ndarray = data.feature_names
    target_names: np.ndarray = data.target_names

    if method == 'PCA':
        Z, _ = perform_PCA(X)
    elif method == 't-SNE':
        Z = perform_TSNE(X, perplexity = 10)
    else:
        raise ValueError("Requested a method that is not supported")
    points = pd.DataFrame(Z, columns=['posX', 'posY'])
    points['cluster'] = y
    # How to JSON serialize pandas dataframes and numpy arrays
    return points.to_dict(orient='records'), list(target_names)

def processTwitchEdge(set, id):
    # node = set
    # link = id
    # note = "ego info"

    # find intersection of ids, if mutual exclusive, no nodes will be shown
    intersection_id = np.zeros((10000))
    if len(set) > 1:
        for i in range(len(set)):
            for j in range(len(set)-i-1):
                # print(i, j+i+1)
                intersection_id_tmp = np.intersect1d(np.array(id[i]), np.array(id[j+1+i]))
                if intersection_id_tmp.shape[0] < intersection_id.shape[0]:
                    intersection_id = intersection_id_tmp
    # print(intersection_id)
    # print(tuple(intersection_id))

    if intersection_id.shape[0] == 0:
        return [], [], [], "No intersection of players in the selected sets."
    if len(set) == 0:
        return [], [], [], "No set selected."
    if len(set) == 1:
        intersection_id = id[0]

    # read edge from csv
    twitchEdge = []
    twitchEdge_tmp = []
    line_count = -1
    intersection_id = list(intersection_id)
    for i in range(len(intersection_id)):
        intersection_id[i] = int(intersection_id[i])
    with open(twitchEdge_filename,'r') as data:
        for line in csv.reader(data):
            if line_count < 0:  
                line_count += 1
                continue
            if (int(line[0]) in intersection_id) and (int(line[1]) in intersection_id):
                twitchEdge.append(tuple([int(line[0]), int(line[1])]))
                twitchEdge_tmp.append([int(np.where(np.array(intersection_id)==int(line[0]))[0][0]), int(np.where(np.array(intersection_id)==int(line[1]))[0][0])])

    netG = contsruct_networkx(nodes=intersection_id, edges=twitchEdge)
    # eigen = find_most_influential(netG)
    posG = force_layout(netG)
    note = "Force-directed network layout for the intersection players on twitch of the selected sets."

    # return node, link, pos, note
    # return intersection_id, twitchEdge_tmp, posG, note
    # print(intersection_id, twitchEdge_tmp, posG, note)
    return intersection_id, twitchEdge_tmp, posG, note

# processTwitchEdge([0, 1, 2], [[5, 6, 7], [5, 6, 7, 8, 9, 10], [1, 2, 3, 4, 5, 6]])

def processTwitchFeat():
    # return ["nodes"], ["links"], ["links_sets"], ["coor_keys"]

    # read feature from csv
    twitchFeat = {"views": [], "life_time": [], "numeric_id": [], "language": []}
    line_count = -1
    coor_keys = ["language", "view_count", "account_life"]
    uniq_lang = ['DA', 'HU', 'NO'] # the least 3 language.
    uniq_view = ["#view_high", "#view_medium", "#view_low"]
    uniq_life = ["#life_high", "#life_medium", "#life_low"]
    # save_ids = []
    # csvfile = open(feat_save, 'w')
    # csvwriter = csv.writer(csvfile) 
    with open(twitchFeat_filename,'r') as data:
        for line in csv.reader(data):
            # row = []
            # for i in range(len(line)):
            #     row.append(line[i])
            if line_count < 0:  
                line_count += 1
                # csvwriter.writerow(row)
                continue
            if str(line[7]) not in uniq_lang:
                continue
            # csvwriter.writerow(row)
            # save_ids.append(int(line[5]))
            twitchFeat["views"].append(int(line[0]))
            twitchFeat["life_time"].append(int(line[2]))
            twitchFeat["numeric_id"].append(int(line[5]))
            twitchFeat["language"].append(str(line[7]))

    
    # construct graph for parallel set chart
    nodes = []
    links = []
    links_sets = []
    max_view = np.max(twitchFeat["views"])
    min_view = np.min(twitchFeat["views"])
    gap_view = float((max_view-min_view)/3)
    value_view = [max_view, max_view-gap_view, min_view+gap_view, min_view-1]
    max_life = np.max(twitchFeat["life_time"])
    min_life = np.min(twitchFeat["life_time"])
    gap_life = float((max_life-min_life)/3)
    value_life = [max_life, max_life-gap_life, min_life+gap_life, min_life-1]
    # uniq_lang = list(np.unique(np.array(twitchFeat["language"])))
    # count_lan = np.zeros((len(uniq_lang)))

    # create sets for all coordinates
    for i in range(len(uniq_lang)):
        nodes.append({"name": uniq_lang[i]})
    for i in range(len(uniq_view)):
        nodes.append({"name": uniq_view[i]})
    for i in range(len(uniq_life)):
        nodes.append({"name": uniq_life[i]})

    # create all combinations between coordinates
    combination_count = 0
    for i in range(len(uniq_lang)):
        for j in range(len(uniq_view)):
            links.append({"source": i, "target": j+len(uniq_lang), "names": [uniq_lang[i], uniq_view[j]], "value": 0})
            links_sets.append([])
            for m in range(len(twitchFeat["numeric_id"])):
                if twitchFeat["language"][m] == uniq_lang[i] and twitchFeat["views"][m] <= value_view[j] and twitchFeat["views"][m] > value_view[j+1]:
                    links[combination_count]["value"] += 1
                    links_sets[combination_count].append(twitchFeat["numeric_id"][m])
            combination_count += 1

    for j in range(len(uniq_view)):
        for k in range(len(uniq_life)):
            links.append({"source": j+len(uniq_lang), "target": k+len(uniq_lang)+len(uniq_view), "names": [uniq_view[j], uniq_life[k]], "value": 0})
            links_sets.append([])
            for m in range(len(twitchFeat["numeric_id"])):
                if twitchFeat["views"][m] <= value_view[j] and twitchFeat["views"][m] > value_view[j+1] and twitchFeat["life_time"][m] <= value_life[k] and twitchFeat["life_time"][m] > value_life[k+1]:
                    links[combination_count]["value"] += 1
                    links_sets[combination_count].append(twitchFeat["numeric_id"][m])
            combination_count += 1

    return nodes, links, links_sets, coor_keys

# N, L, S = processTwitchFeat()
# print(N, L, S)