'''
File: frank_api.py
Description: REST-based API for FRANK
'''

import argparse
import contextlib
import datetime
import io
import json
import re
import uuid
from pathlib import Path

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
argparser.add_argument("-s", "--save-query", type=bool,
    default=False, help="If True, saves alist under ./logs/timestamp.json")

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
        raise ValueError("Could not parse question. Please try again.")
    return answer, session_id, query_json, alist.attributes

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

def save_query(
        timestamp: str,
        session_id: str,
        query_nl: str,
        query_alist: dict,
        graph: list,
        answer_nl: str,
        answer_alist: dict,
        ) -> dict:
    """Save information about a Frank query.
    
    Parameters
    ----------
    timestamp: str
        Timestamp of session as returned by datetime.datetime.now().isoformat()
    session_id: str
        UUID token created for the query.
    query_nl: str
        The natural language query, e.g., "What will the population of France be in 2029?"
    query_alist: json
        The natural language query passed to alist form.
    graph: list
        The output of Frank's inference process. Is converted to leave only intermediate alists.
    answer_nl: str,
        The natural language answer, e.g., 62333000.
    answer_alist: dict
        The answer to the query in alist form.
    """
    # Save only alists from query
    regex = re.compile(r'^.*?(\{.*\}).*')
    matches = [m.group(1) for m in filter(None, map(regex.search, graph))]
    corrected_output = [i.replace("\'", '"').replace('"{', '{').replace('}"', '}') for i in matches]
    output_as_json = [json.loads(i) for i in corrected_output]

    output = {'timestamp': timestamp, 'session_id': session_id, 'query_nl': query_nl,
              'query_alist': query_alist, 'graph': output_as_json,
              'answer_nl': answer_nl, 'answer_alist': answer_alist}

    output_dir = Path('logs')
    if not output_dir.exists():
        output_dir.mkdir()
    with open(output_dir / f'{timestamp}.json', 'w', encoding='utf-8') as outfile:
        json.dump(output, outfile, indent=4)

    return output


if __name__ == '__main__':
    args = argparser.parse_args()
    if args.file and args.query:
        print("\nThe --query option cannot be used with the --file option.")
    if args.file and args.context:
        print("\nCannot use --context together with the --file flag.")

    query_timestamp = datetime.datetime.now().isoformat()
    if args.file:
        batch(args.file, args.output)
    else:
        if args.save_query:
            # HACK: Instead of propagating output through class methods, capture stdout lines into
            #       a string buffer.
            stdoutput = io.StringIO()
            with contextlib.redirect_stdout(stdoutput):
                ans, s_id, q_alist, a_alist = cli(args.query, args.context)
            formatted_output = stdoutput.getvalue().splitlines()
            save_query(query_timestamp, s_id, args.query,
                       q_alist, formatted_output, ans, a_alist)
        else:
            cli(args.query, args.context)
