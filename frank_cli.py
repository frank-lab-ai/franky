'''
File: frank_api.py
Description: REST-based API for FRANK
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)

'''

import json
import uuid
import matplotlib.pyplot as plt
from frank.launcher import Launcher
from frank.config import config
from frank.alist import Alist
import frank.explain
import frank.query_parser.parser
from frank.graph import InferenceGraph
from frank.processLog import pcolors as pcol


inference_graphs = {}

def cli():
    session_id = uuid.uuid4().hex
    print(f"\n{pcol.CYAN}FRANK CLI{pcol.RESETALL}")
    query = input(f"Enter question or alist query: \n {pcol.CYAN}>{pcol.RESETALL} ")
    query_json = None
    # check if input is question or alist
    if '{' in query and '"' in query:
        query_json = json.loads(query)
    else:
        parser = frank.query_parser.parser.Parser()
        parsedQuestion = parser.getNextSuggestion(query)
        query_json = parsedQuestion['alist']

    if query_json:
        print(f"{pcol.YELLOW} ├── query alist:{json.dumps(query_json)} {pcol.RESETALL}")
        print(f"{pcol.YELLOW} └── session id:{session_id} {pcol.RESETALL}\n")
        alist = Alist(**query_json)
        launch = Launcher()
        launch.start(alist, session_id, inference_graphs)

        if session_id in inference_graphs:
            plt.ion()
            fig = plt.figure()
            plt.show()
            graph = inference_graphs[session_id]['graph']
            graph.display()  
        input("\npress any key to exit")
    else:
        print("\nCould not parse question. Please try again.")


def show_graph(G):
    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))


if __name__ == '__main__':
    cli()
