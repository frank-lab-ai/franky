'''
File: frank_api.py
Description: REST-based API for FRANK
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)

'''

import json
import uuid
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
    print(f"\n{pcol.CYAN}FRANK CLI{pcol.RESET}")
    query = input(f"Enter question or alist query: \n {pcol.CYAN}>{pcol.RESET} ")
    query_json = None
    # check if input is question or alist
    if '{' in query and '"' in query:
        query_json = json.loads(query)
    else:
        parser = frank.query_parser.parser.Parser()
        parsedQuestion = parser.getNextSuggestion(query)
        query_json = parsedQuestion['alist']
    if query_json:
        alist = Alist(**query_json)
        launch = Launcher()
        launch.start(alist, session_id, inference_graphs)
    else:
        print("\nCould not parse question. Please try again.")


if __name__ == '__main__':
    cli()
