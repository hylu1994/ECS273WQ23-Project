""" train.py

    Main interface to train the GNNs that will be later explained.
"""
import argparse
import os
import pickle
import random
import shutil
import time

import matplotlib
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

import networkx as nx
import numpy as np
import sklearn.metrics as metrics

import torch
import torch.nn as nn
from torch.autograd import Variable

from tensorboardX import SummaryWriter

import inference.configs as configs
import inference.gengraph as gengraph

import inference.utils.math_utils as math_utils
import inference.utils.io_utils as io_utils
import inference.utils.parser_utils as parser_utils
import inference.utils.train_utils as train_utils
import inference.utils.featgen as featgen
import inference.utils.graph_utils as graph_utils

import inference.models as models

def reddit_node(graph_id):
    
    args = configs.arg_parse()
    model = models.GcnEncoderGraph(
        10,
        args.hidden_dim,
        args.output_dim,
        args.num_classes,
        args.num_gc_layers,
        bn=args.bn,
        dropout=args.dropout,
        args=args,
    )

    filename = "/Users/hsiao-yinglu/hsiaoyinglu/network_projects/EHR project/GNNInterpreter-visualization/server/inference/ckpt/REDDIT-BINARY_base_h20_o20.pth.tar"
    ckpt = torch.load(filename, map_location=torch.device('cpu'))
    # ckpt = io_utils.load_ckpt(prog_args)
    cg_dict = ckpt["cg"] # get computation graph
    input_dim = cg_dict["feat"]
    sub_adj = cg_dict["adj"][graph_id]
    sub_feat = cg_dict["feat"][graph_id, :]
    # G_orig = io_utils.denoise_graph(
    #     sub_adj,
    #     0,
    #     feat=sub_feat,
    #     threshold=None,
    #     max_component=False,
    # )
    # num_node = len(G_orig.nodes())
    # print(len(G_orig.nodes()))
    # return
    
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    
    sub_adj = np.expand_dims(sub_adj, axis=0)
    sub_feat = np.expand_dims(sub_feat, axis=0)
    adj   = torch.tensor(sub_adj, dtype=torch.float)
    x     = torch.tensor(sub_feat, requires_grad=True, dtype=torch.float)

    ypred, emb_all = model(x, adj) # emb_all include expanded dimensions.
    emb_all = emb_all.detach().numpy()[0]
    # print(ypred)
    # print(emb_all.shape)
    adj = adj.detach().numpy()
    nodes_id = []
    nodes_emb = {}
    for i in range(100):
        if np.sum(adj[0][i]) != 0:
            nodes_id.append(i)
            nodes_emb[str(i)] = list(emb_all[i])
            for j in range(len(nodes_emb[str(i)])):
                nodes_emb[str(i)][j] = float(nodes_emb[str(i)][j])

    # print(nodes_id)
    # print(nodes_emb)
    # print(len(nodes_id), nodes_id)
    # print(att_adj.detach().numpy())
    # print(len(att_adj))
    return nodes_emb
