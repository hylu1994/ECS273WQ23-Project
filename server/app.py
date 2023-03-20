from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from controller import processPrimitiveSubgraph, overview_scatterplot, getForced, instance_emb
import numpy as np

app = Flask(__name__)
CORS(app)

# @app.route("/")
# @cross_origin()
# def hello_world():
#     return "<p>Hello, World!</p>"

@app.route("/fetchExample", methods=["GET", "POST"])
@cross_origin()
def fetchExample():
    if request.method == "GET":  # handling GET request
        nodes, edges = getForced()
        resp = jsonify(nodes=nodes, edges=edges)
        return resp
    elif request.method == "POST":
        request_context = request.get_json()
        index = request_context['method']
        nodes, edges = getForced(index)
        resp = jsonify(nodes=nodes, edges=edges)
        return resp

@app.route("/fetchPrimitive", methods=["GET", "POST"])
@cross_origin()
def fetchPrimitive():
    if request.method == "GET": # handling GET request
        overview_points = overview_scatterplot()
        resp = jsonify(data=overview_points)
        return resp
    else: # handling POST request, which is only effective when ExampleWithInteractions.vue is loaded
        request_context = request.get_json() # JSON object
        graph_index = request_context['graph_id']
        similarities = processPrimitiveSubgraph(graph_index)
        resp = jsonify(adj=similarities)
        return resp
    
@app.route("/fetchInstance", methods=["GET", "POST"])
@cross_origin()
def fetchInstance():
    if request.method == "GET": # handling GET request
        instance_points = instance_emb()
        resp = jsonify(data=instance_points)
        return resp
    else: # handling POST request, which is only effective when ExampleWithInteractions.vue is loaded
        request_context = request.get_json() # JSON object
        graph_index = request_context['graph_id']
        similarities = processPrimitiveSubgraph(graph_index)
        resp = jsonify(adj=similarities)
        return resp

if __name__ == "__main__":
    app.run(port=3100, debug=True)