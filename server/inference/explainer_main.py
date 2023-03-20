""" explainer_main.py

     Main user interface for the explainer module.
"""
import argparse
import os
import itertools
import json

import sklearn.metrics as metrics

from tensorboardX import SummaryWriter

import pickle
import shutil
import torch

import inference.models as models
import inference.utils.io_utils as io_utils
import inference.utils.parser_utils as parser_utils
from inference.explainer import explain

import inference.node_emb as node_emb

import networkx as nx
from grakel.utils import graph_from_networkx
from grakel.kernels import ShortestPath, GraphletSampling
from grakel import Graph
import numpy as np


def softmax(x):
    return(list(np.exp(x)/np.exp(x).sum()))

def arg_parse():
    parser = argparse.ArgumentParser(description="GNN Explainer arguments.")
    io_parser = parser.add_mutually_exclusive_group(required=False)
    io_parser.add_argument("--dataset", dest="dataset", help="Input dataset.")
    benchmark_parser = io_parser.add_argument_group()
    benchmark_parser.add_argument(
        "--bmname", dest="bmname", help="Name of the benchmark dataset"
    )
    io_parser.add_argument("--pkl", dest="pkl_fname", help="Name of the pkl data file")

    parser_utils.parse_optimizer(parser)

    parser.add_argument("--clean-log", action="store_true", help="If true, cleans the specified log directory before running.")
    parser.add_argument("--logdir", dest="logdir", help="Tensorboard log directory")
    parser.add_argument("--ckptdir", dest="ckptdir", help="Model checkpoint directory")
    parser.add_argument("--cuda", dest="cuda", help="CUDA.")
    parser.add_argument(
        "--gpu",
        dest="gpu",
        action="store_const",
        const=True,
        default=False,
        help="whether to use GPU.",
    )
    parser.add_argument(
        "--epochs", dest="num_epochs", type=int, help="Number of epochs to train."
    )
    parser.add_argument(
        "--hidden-dim", dest="hidden_dim", type=int, help="Hidden dimension"
    )
    parser.add_argument(
        "--output-dim", dest="output_dim", type=int, help="Output dimension"
    )
    parser.add_argument(
        "--num-gc-layers",
        dest="num_gc_layers",
        type=int,
        help="Number of graph convolution layers before each pooling",
    )
    parser.add_argument(
        "--bn",
        dest="bn",
        action="store_const",
        const=True,
        default=False,
        help="Whether batch normalization is used",
    )
    parser.add_argument("--dropout", dest="dropout", type=float, help="Dropout rate.")
    parser.add_argument(
        "--nobias",
        dest="bias",
        action="store_const",
        const=False,
        default=True,
        help="Whether to add bias. Default to True.",
    )
    parser.add_argument(
        "--no-writer",
        dest="writer",
        action="store_const",
        const=False,
        default=True,
        help="Whether to add bias. Default to True.",
    )
    # Explainer
    parser.add_argument("--mask-act", dest="mask_act", type=str, help="sigmoid, ReLU.")
    parser.add_argument(
        "--mask-bias",
        dest="mask_bias",
        action="store_const",
        const=True,
        default=False,
        help="Whether to add bias. Default to True.",
    )
    parser.add_argument(
        "--explain-node", dest="explain_node", type=int, help="Node to explain."
    )
    parser.add_argument(
        "--graph-idx", dest="graph_idx", type=int, help="Graph to explain."
    )
    parser.add_argument(
        "--graph-mode",
        dest="graph_mode",
        action="store_const",
        const=True,
        default=False,
        help="whether to run Explainer on Graph Classification task.",
    )
    parser.add_argument(
        "--multigraph-class",
        dest="multigraph_class",
        type=int,
        help="whether to run Explainer on multiple Graphs from the Classification task for examples in the same class.",
    )
    parser.add_argument(
        "--multinode-class",
        dest="multinode_class",
        type=int,
        help="whether to run Explainer on multiple nodes from the Classification task for examples in the same class.",
    )
    parser.add_argument(
        "--align-steps",
        dest="align_steps",
        type=int,
        help="Number of iterations to find P, the alignment matrix.",
    )

    parser.add_argument(
        "--method", dest="method", type=str, help="Method. Possible values: base, att."
    )
    parser.add_argument(
        "--name-suffix", dest="name_suffix", help="suffix added to the output filename"
    )
    parser.add_argument(
        "--explainer-suffix",
        dest="explainer_suffix",
        help="suffix added to the explainer log",
    )
    parser.add_argument(
        "--http",
        dest="http",
        action="store_const",
        const=True,
        default=True,
        help="debug",
    )

    # TODO: Check argument usage
    parser.set_defaults(
        logdir ="/Users/hsiao-yinglu/hsiaoyinglu/network_projects/EHR project/GNNInterpreter-visualization/server/inference/log",
        ckptdir="/Users/hsiao-yinglu/hsiaoyinglu/network_projects/EHR project/GNNInterpreter-visualization/server/inference/ckpt",
        dataset="REDDIT-BINARY",
        opt="adam",  
        opt_scheduler="none",
        cuda="0",
        lr=0.1,
        clip=2.0,
        batch_size=20,
        num_epochs=100,
        hidden_dim=20,
        output_dim=20,
        num_gc_layers=3,
        dropout=0.0,
        method="base",
        name_suffix="",
        explainer_suffix="",
        align_steps=1000,
        explain_node=None,
        graph_idx=-1,
        mask_act="sigmoid",
        multigraph_class=-1,
        multinode_class=-1,
    )
    return parser.parse_args()

def graphlet_distribution(source, graphlets):
    gl_dist = [0 for i in range(len(graphlets))]
    for graphlet_idx in range(len(graphlets)):
        print("graphlet: ", graphlet_idx)
        count = 0
        total = itertools.combinations(source.nodes(),len(graphlets[graphlet_idx].nodes()))
        for sub_nodes in itertools.combinations(source.nodes(),len(graphlets[graphlet_idx].nodes())):
            print(str(count) + " / " + str(total))
            subg = source.subgraph(sub_nodes)
            if nx.is_connected(subg) and nx.is_isomorphic(subg, graphlets[graphlet_idx]):
                gl_dist[graphlet_idx] += 1
            count += 1
    # for graphlet_idx in range(len(graphlets)):
    #     print("graphlet: ", graphlet_idx)
    #     count = 0
    #     total = itertools.combinations(source.nodes(),len(graphlets[graphlet_idx].nodes()))
    #     for sub_nodes in itertools.combinations(source.nodes(),len(graphlets[graphlet_idx].nodes())):
    #         print(str(count) + " / " + str(total))
    #         subg = source.subgraph(sub_nodes)
    #         if nx.is_connected(subg) and nx.is_isomorphic(subg, graphlets[graphlet_idx]):
    #             gl_dist[graphlet_idx] += 1
    #         count += 1
    return gl_dist

def inference_primitive(graph_index, graphlets):
    # Load a configuration
    prog_args = arg_parse()

    # Load a model checkpoint
    ckpt = io_utils.load_ckpt(prog_args)
    cg_dict = ckpt["cg"] # get computation graph
    input_dim = cg_dict["feat"].shape[2] 
    num_classes = cg_dict["pred"].shape[2]
    print("Loaded model from {}".format(prog_args.ckptdir))
    print("input dim: ", input_dim, "; num classes: ", num_classes)

    # Determine explainer mode
    graph_mode = True

    # build model
    print("Method: ", prog_args.method)
    if graph_mode: 
        # Explain Graph prediction
        model = models.GcnEncoderGraph(
            input_dim=input_dim,
            hidden_dim=prog_args.hidden_dim,
            embedding_dim=prog_args.output_dim,
            label_dim=num_classes,
            num_layers=prog_args.num_gc_layers,
            bn=prog_args.bn,
            args=prog_args,
        )
    
    # load state_dict (obtained by model.state_dict() when saving checkpoint)
    model.load_state_dict(ckpt["model_state"]) 

    path = os.path.join(prog_args.logdir, io_utils.gen_explainer_prefix(prog_args))
    writer = SummaryWriter(path)

    # Create explainer
    explainer = explain.Explainer(
        model=model,
        adj=cg_dict["adj"],
        feat=cg_dict["feat"],
        label=cg_dict["label"],
        pred=cg_dict["pred"],
        train_idx=cg_dict["train_idx"],
        args=prog_args,
        writer=writer,
        print_training=True,
        graph_mode=graph_mode,
        graph_idx=prog_args.graph_idx,
    )
    
    # for tmp in range(len(cg_dict["pred"][0])):
    #     print(cg_dict["label"].detach().numpy()[tmp], np.argmax(softmax(cg_dict["pred"][0][tmp])), cg_dict["pred"][0][tmp])
    

    Gs_original, Gs_denoised, Nx_original, Nx_denoised = explainer.explain_graphs_return_graph(graph_indices=graph_index)
    sp_kernel = ShortestPath(normalize=True)
    gs_kernel = GraphletSampling(normalize=True, k=5, sampling=None)

    overview_data = []
    skip_graph_id = []
    for i in range(len(Gs_original)):
        print("graph id: ", graph_index[i], "#node: ", len(list(Nx_original[i].nodes())))
        if len(list(Nx_original[i].nodes())) <= 50: continue
        if Gs_original[i] == -1:
            skip_graph_id.append(graph_index[i])
        else:
            tmp_data = {"id": int(graph_index[i]), "label": int(cg_dict["label"].detach().numpy()[graph_index[i]]), "pred_softmax": softmax(cg_dict["pred"][0][graph_index[i]]), "pred": list(cg_dict["pred"][0][graph_index[i]])}
            tmp_data["orig_nodes"] = list(Nx_original[i].nodes())
            tmp_data["graphlets_orig"] = []
            # tmp_data["graphlets_deno"] = []
            tmp_data["graphlets_node_orig"] = []
            # tmp_data["graphlets_node_deno"] = []

            # sp_kernel.fit_transform([Gs_original[i]])[0][0]
            # tmp_data["similarities_sp"] = sp_kernel.transform([Gs_denoised[i]])[0][0]

            # gs_kernel.fit_transform([Gs_original[i]])[0][0]
            for j in range(len(graphlets)):
                print("graphlet id: ", j+1)
                gs_kernel.fit_transform([graphlets[j]])[0][0]
                orig_tmp = gs_kernel.transform([Gs_original[i]], list(Nx_original[i].nodes()))
                # deno_tmp = gs_kernel.transform([Gs_denoised[i]], list(Nx_denoised[i].nodes()))
                tmp_data["graphlets_node_orig"].append(orig_tmp[0:len(list(Nx_original[i].nodes()))])
                # tmp_data["graphlets_node_deno"].append(deno_tmp[0:len(list(Nx_denoised[i].nodes()))])
                tmp_data["graphlets_orig"].append(orig_tmp[len(list(Nx_original[i].nodes()))])
                # tmp_data["graphlets_deno"].append(deno_tmp[len(list(Nx_denoised[i].nodes()))])
            tmp_data["node_emb"] = node_emb.reddit_node(graph_index[i])
            # gs_kernel.fit_transform([Gs_denoised[i]])[0][0]
            # for j in range(len(graphlets)):
            #     gs_kernel.fit_transform([graphlets[j]])[0][0]
            #     tmp_data["graphlets_deno"].append(gs_kernel.transform([Gs_denoised[i]], list(Nx_denoised[i].nodes())))
                
            overview_data.append(tmp_data)
            # print(tmp_data)
    
    # with open("/Users/hsiao-yinglu/hsiaoyinglu/network_projects/EHR project/GNNInterpreter-visualization/server/data/kernel_prob.json", "w") as outfile:
    #     json.dump(overview_data, outfile)

    return overview_data

# Creat by harrison
def get_inference_graph(graph_index):
    print(graph_index)
    # Load a configuration
    prog_args = arg_parse()
    # Load a model checkpoint
    ckpt = io_utils.load_ckpt(prog_args)
    cg_dict = ckpt["cg"]  # get computation graph
    input_dim = cg_dict["feat"].shape[2]
    num_classes = cg_dict["pred"].shape[2]
    print("Loaded model from {}".format(prog_args.ckptdir))
    print("input dim: ", input_dim, "; num classes: ", num_classes)

    # Determine explainer mode
    graph_mode = True

    # build model
    print("Method: ", prog_args.method)
    if graph_mode:
        # Explain Graph prediction
        model = models.GcnEncoderGraph(
            input_dim=input_dim,
            hidden_dim=prog_args.hidden_dim,
            embedding_dim=prog_args.output_dim,
            label_dim=num_classes,
            num_layers=prog_args.num_gc_layers,
            bn=prog_args.bn,
            args=prog_args,
        )

    # load state_dict (obtained by model.state_dict() when saving checkpoint)
    model.load_state_dict(ckpt["model_state"])

    path = os.path.join(prog_args.logdir,
                        io_utils.gen_explainer_prefix(prog_args))
    writer = SummaryWriter(path)

    # Create explainer
    explainer = explain.Explainer(
        model=model,
        adj=cg_dict["adj"],
        feat=cg_dict["feat"],
        label=cg_dict["label"],
        pred=cg_dict["pred"],
        train_idx=cg_dict["train_idx"],
        args=prog_args,
        writer=writer,
        print_training=True,
        graph_mode=graph_mode,
        graph_idx=prog_args.graph_idx,
    )

    Gs_original, _ = explainer.explain_graphs_return_graph_TMP(
        graph_indices=graph_index)
    return Gs_original, 0

def main():
    # Load a configuration
    prog_args = arg_parse()

    if prog_args.gpu:
        os.environ["CUDA_VISIBLE_DEVICES"] = prog_args.cuda
        print("CUDA", prog_args.cuda)
    else:
        print("Using CPU")

    # Configure the logging directory 
    if prog_args.writer:
        path = os.path.join(prog_args.logdir, io_utils.gen_explainer_prefix(prog_args))
        if os.path.isdir(path) and prog_args.clean_log:
           print('Removing existing log dir: ', path)
           if not input("Are you sure you want to remove this directory? (y/n): ").lower().strip()[:1] == "y": sys.exit(1)
           shutil.rmtree(path)
        writer = SummaryWriter(path)
    else:
        writer = None

    # Load a model checkpoint
    ckpt = io_utils.load_ckpt(prog_args)
    cg_dict = ckpt["cg"] # get computation graph
    input_dim = cg_dict["feat"].shape[2] 
    num_classes = cg_dict["pred"].shape[2]
    print("Loaded model from {}".format(prog_args.ckptdir))
    print("input dim: ", input_dim, "; num classes: ", num_classes)

    # Determine explainer mode
    graph_mode = (
        prog_args.graph_mode
        or prog_args.multigraph_class >= 0
        or prog_args.graph_idx >= 0
    )

    # build model
    print("Method: ", prog_args.method)
    if graph_mode: 
        # Explain Graph prediction
        model = models.GcnEncoderGraph(
            input_dim=input_dim,
            hidden_dim=prog_args.hidden_dim,
            embedding_dim=prog_args.output_dim,
            label_dim=num_classes,
            num_layers=prog_args.num_gc_layers,
            bn=prog_args.bn,
            args=prog_args,
        )
    else:
        if prog_args.dataset == "ppi_essential":
            # class weight in CE loss for handling imbalanced label classes
            prog_args.loss_weight = torch.tensor([1.0, 5.0], dtype=torch.float).cuda() 
        # Explain Node prediction
        model = models.GcnEncoderNode(
            input_dim=input_dim,
            hidden_dim=prog_args.hidden_dim,
            embedding_dim=prog_args.output_dim,
            label_dim=num_classes,
            num_layers=prog_args.num_gc_layers,
            bn=prog_args.bn,
            args=prog_args,
        )
    if prog_args.gpu:
        model = model.cuda()
    # load state_dict (obtained by model.state_dict() when saving checkpoint)
    model.load_state_dict(ckpt["model_state"]) 

    # Create explainer
    explainer = explain.Explainer(
        model=model,
        adj=cg_dict["adj"],
        feat=cg_dict["feat"],
        label=cg_dict["label"],
        pred=cg_dict["pred"],
        train_idx=cg_dict["train_idx"],
        args=prog_args,
        writer=writer,
        print_training=True,
        graph_mode=graph_mode,
        graph_idx=prog_args.graph_idx,
    )

    # TODO: API should definitely be cleaner
    # Let's define exactly which modes we support 
    # We could even move each mode to a different method (even file)
    if prog_args.explain_node is not None:
        explainer.explain(prog_args.explain_node, unconstrained=False)
    elif graph_mode:
        if prog_args.multigraph_class >= 0:
            print(cg_dict["label"])
            # only run for graphs with label specified by multigraph_class
            labels = cg_dict["label"].numpy()
            graph_indices = []
            for i, l in enumerate(labels):
                if l == prog_args.multigraph_class:
                    graph_indices.append(i)
                if len(graph_indices) > 30:
                    break
            print(
                "Graph indices for label ",
                prog_args.multigraph_class,
                " : ",
                graph_indices,
            )
            explainer.explain_graphs(graph_indices=graph_indices)

        elif prog_args.graph_idx == -1:
            # just run for a customized set of indices
            explainer.explain_graphs(graph_indices=[5])

        elif prog_args.graph_idx == -2:
            # input the selected graph index.
            explainer.explain_graphs(graph_indices=[1, 2, 3, 4])

        else:
            explainer.explain(
                node_idx=0,
                graph_idx=prog_args.graph_idx,
                graph_mode=True,
                unconstrained=False,
            )
            io_utils.plot_cmap_tb(writer, "tab20", 20, "tab20_cmap")
    else:
        if prog_args.multinode_class >= 0:
            print(cg_dict["label"])
            # only run for nodes with label specified by multinode_class
            labels = cg_dict["label"][0]  # already numpy matrix

            node_indices = []
            for i, l in enumerate(labels):
                if len(node_indices) > 4:
                    break
                if l == prog_args.multinode_class:
                    node_indices.append(i)
            print(
                "Node indices for label ",
                prog_args.multinode_class,
                " : ",
                node_indices,
            )
            explainer.explain_nodes(node_indices, prog_args)

        else:
            # explain a set of nodes
            masked_adj = explainer.explain_nodes_gnn_stats(
                range(400, 700, 5), prog_args
            )

if __name__ == "__main__":
    main()

