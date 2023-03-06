'''
File: frank_api.py
Description: REST-based API for FRANK
'''

import argparse
import json
import uuid

import frank.explain
import frank.query_parser.parser
from frank.alist import Alist
from frank.alist import Attributes as tt
from frank.launcher import Launcher
from frank.processLog import pcolors as pcol


inference_graphs = {}
argparser =  argparse.ArgumentParser(
        prog="FRANK CLI",
        description="Command line interface for FRANK")
argparser.add_argument("-q", "--query", type=str,
    default="", help="a query to be answered; a text or alist string query")
argparser.add_argument("-c", "--context", type=str,
    default={}, help="context for the query; (default = {})")
argparser.add_argument("-f", "--file", type=str,
    help="batch file; used when evaluating multiple questions in a file")
argparser.add_argument("-o", "--output", type=str,
    default="output.json", help="file to output batch query results to; (default = output.json)")


def cli(
        query: str | dict,
        context=None,
        ) -> str:
    """Command line interface to Frank for a single query.
    
    Parameters
    ----------
    query: str | dict
        Query to Frank in natural language or alist form.
    context: str | dict
        User specific-context as dict in str form or dict.
    
    Returns
    -------
    answer: str
        Answer returned by Frank.
    """
    session_id = uuid.uuid4().hex
    interactive = False
    answer = None
    if query:
        query_json = None
    else:
        print(f"\n{pcol.CYAN}FRANK CLI{pcol.RESETALL}")
        query = input(f"Enter question or alist query: \n {pcol.CYAN}>{pcol.RESETALL} ")
        context = input(f"Enter context: \n {pcol.CYAN}>{pcol.RESETALL} ")
        query_json = None
        interactive = True

    # check if input is question or alist
    if isinstance(query, str) and '{' in query and '"' in query:
        query_json = json.loads(query)
    elif isinstance(query, dict):
        query_json = query
    else:
        parser = frank.query_parser.parser.Parser()
        parsed_question = parser.getNextSuggestion(query)
        query_json = parsed_question['alist']

    if query_json:
        alist = Alist(**query_json)
        if context:
            context_json = json.loads(context) if isinstance(context, str) else context
            alist.set(tt.CONTEXT, context_json)
        print(f"{pcol.YELLOW} ├── query alist:{json.dumps(alist.attributes)} {pcol.RESETALL}")
        print(f"{pcol.YELLOW} └── session id:{session_id} {pcol.RESETALL}\n")
        launch = Launcher()
        launch.start(alist, session_id, inference_graphs)

        if session_id in inference_graphs:
            answer = inference_graphs[session_id]['answer']['answer']
            graph = inference_graphs[session_id]['graph']
            graph.plot_plotly(query)
        if interactive:
            input("\npress any key to exit")
    else:
        print("\nCould not parse question. Please try again.")
    return answer

def batch(
        batch_file: str,
        output: str,
        ) -> None:
    """Batch processing of multiple Frank queries.
    
    Parameters
    ----------
    batch_file: str
        Source file containing batched questions.
    output: str
        Name of file to output results to.
    """
    results = []
    with open(batch_file, 'r', encoding='utf-8') as json_file:
        queries = json.load(json_file)
        for query in queries:
            answer = cli(query['question'], query['context'])
            results.append({'id': query['id'], 'answer': answer})
            with open(output, 'w', encoding='utf-8') as out_file:
                json.dump(results, out_file)

    print('Done! \nResults in ' + output)


if __name__ == '__main__':
    args = argparser.parse_args()
    if args.file and args.query:
        print("\nThe --query option cannot be used with the --file option.")
    if args.file and args.context:
        print("\nCannot use --context together with the --file flag.")

    if args.file:
        batch(args.file, args.output)
    else:
        cli(args.query, args.context)
