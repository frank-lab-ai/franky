'''
File: frank_api.py
Description: REST-based API for FRANK
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)

'''

import json
import uuid
import argparse
import matplotlib.pyplot as plt
from frank.launcher import Launcher
from frank.config import config
from frank.alist import Alist
from frank.alist import Attributes as tt
import frank.explain
import frank.query_parser.parser
from frank.graph import InferenceGraph
from frank.processLog import pcolors as pcol


inference_graphs = {}
argparser =  argparse.ArgumentParser(
        prog="FRANK CLI", 
        description="Command line interface for FRANK")
argparser.add_argument("-q", "--query", metavar='Q', type=str, 
    default="", help='a query to be answered; a text or alist string query')
argparser.add_argument("-c", "--context", metavar='C', type=str,
    default={}, help='context for the query; (default = {})',
        )

def cli(query="", context={}):
    session_id = uuid.uuid4().hex
    interactive = False
    if query:
        query_json = None
    else:
        print(f"\n{pcol.CYAN}FRANK CLI{pcol.RESETALL}")
        query = input(f"Enter question or alist query: \n {pcol.CYAN}>{pcol.RESETALL} ")
        context = input(f"Enter context: \n {pcol.CYAN}>{pcol.RESETALL} ")
        query_json = None
        interactive = True
    
    # check if input is question or alist
    if '{' in query and '"' in query:
        query_json = json.loads(query)
    else:
        parser = frank.query_parser.parser.Parser()
        parsedQuestion = parser.getNextSuggestion(query)
        query_json = parsedQuestion['alist']

    if query_json:        
        alist = Alist(**query_json)
        if context:
            context_json = json.loads(context)
            alist.set(tt.CONTEXT, context_json)
        print(f"{pcol.YELLOW} ├── query alist:{json.dumps(alist.attributes)} {pcol.RESETALL}")
        print(f"{pcol.YELLOW} └── session id:{session_id} {pcol.RESETALL}\n")
        launch = Launcher()
        launch.start(alist, session_id, inference_graphs)

        if session_id in inference_graphs:
            graph:InferenceGraph = inference_graphs[session_id]['graph']
            graph.plot_plotly(query)
        if interactive:
            input("\npress any key to exit")
    else:
        print("\nCould not parse question. Please try again.")


if __name__ == '__main__':
    args = argparser.parse_args()
    cli(args.query, args.context)
 