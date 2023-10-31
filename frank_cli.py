'''
File: frank_api.py
Description: REST-based API for FRANK
'''

import argparse
import contextlib
import datetime
import io
import json
import pickle
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

def execute_query(
        query: str | dict,
        context: str | dict = "",
        plot: bool = False,
        return_type: str = "object"
    ) -> str | dict | None:
    """Command line interface to Frank for a single query.
    
    Parameters
    ----------
    query: str | dict
        Query to Frank in natural language or alist form.
    context: str | dict
        User specific-context as dict in str form or dict.
    plot: bool
        If True, plots the inference graph.
    return_type: str
        If "object", returns the graph object, if "answer", returns a dict representation of the
        alists.
    
    Returns
    -------
    answer: str | dict | None
        Answer returned by Frank in format specified by return_type.
    """

    if return_type not in ["object", "answer"]:
        raise ValueError("return_type must be either 'object' or 'answer'")

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
            if plot:
                graph = inference_graphs[session_id]['graph']
                graph.plot_plotly(query)
        if interactive:
            input("\npress any key to exit")
    else:
        raise ValueError("Could not parse question. Please try again.")

    if return_type == "object":
        return inference_graphs[session_id]
    if return_type == "answer":
        return inference_graphs[session_id]['answer']['answer']


def batch(
        batch_file: str,
        out_file: str,
    ) -> None:
    """Batch processing of multiple Frank queries.
    
    Parameters
    ----------
    batch_file: str
        Source file containing batched questions.
    out_file: str
        Name of file to output results to.
    """
    results = []
    with open(batch_file, 'r', encoding='utf-8') as json_file:
        queries = json.load(json_file)
        for query in queries:
            answer = main(query['question'], query['context'], return_type='answer')
            results.append({'id': query['id'], 'answer': answer})
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(results, f)

    print('Done! \nResults in ' + out_file)


def format_output(
        captured_stdout: list[str],
        timestamp: str,
        session_id: str,
        query_nl: str,
        query_alist: dict,
        answer_nl: str,
        answer_alist: dict,
    ) -> dict:
    """ Format captured stdout into a dict for saving.
    CURRENTLY UNUSED

    Parameters
    ----------
    captured_stdout: list[str]
        Captured stdout from main()
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

    Returns
    -------
    output: dict
        Formatted output.
    """

    # Save only alists from query
    regex = re.compile(r'^.*?(\{.*\}).*')
    matches = [m.group(1) for m in filter(None, map(regex.search, captured_stdout))]
    corrected_output = [i.replace("\'", '"').replace('"{', '{').replace('}"', '}') for i in matches]
    output_as_json = [json.loads(i) for i in corrected_output]

    formatted_output = {'timestamp': timestamp, 'session_id': session_id, 'query_nl': query_nl,
        'query_alist': query_alist, 'graph': output_as_json,
        'answer_nl': answer_nl, 'answer_alist': answer_alist}

    return formatted_output


def save_object(
        query_object: dict,
    ) -> None:
    """Save the inference graph object to ./logs/{timestamp}.pkl
    
    Parameters
    ----------
    query_object: dict
        The output of Frank's inference process in object form (inference_graphs[session_id])
    """

    timestamp = datetime.datetime.now().isoformat()
    output_dir = Path('logs')
    if not output_dir.exists():
        output_dir.mkdir()
    with open(output_dir / f"{timestamp}.pkl", 'wb') as outfile:
        pickle.dump(query_object, outfile)


def main(
        query: str | dict,
        context: str | dict = "",
        plot: bool = False,
        save: bool = False,
        return_type: str = "object",
        suppress_stdout: bool = False,
    ) -> str | dict | None:
    """Command line interface to Frank for a single query. Includes nice formatting of output, and
    saving of query information.
     
    Parameters
    ----------
    query: str | dict
        Query to Frank in natural language or alist form.
    context: str | dict
        User specific-context as dict in str form or dict.
    plot: bool
        If True, plots the inference graph.
    save: bool
        If True, saves alist under ./logs/timestamp.json
    return_type: str
        If "object", returns the full graph object, if "answer", returns the numeric answer itself.
    suppress_stdout: bool
        If True, suppresses Frank's printing of the inference process to stdout.

    Returns
    -------
    output: str | dict | None
        Query output in for specified by return_type.
    """

    if return_type not in ["object", "answer"]:
        raise ValueError("return_type must be either 'object' or 'answer'")

    if save and return_type == 'answer':
        raise ValueError("No reason to save only answer. Run again with save=False or return_type='object'")

    if suppress_stdout:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            output_object = execute_query(query, context, plot, return_type=return_type)
    else:
        output_object = execute_query(query, context, plot, return_type=return_type)

    if save and isinstance(output_object, dict):
        save_object(output_object)

    return output_object


if __name__ == '__main__':

    argparser =  argparse.ArgumentParser(
        prog="FRANK CLI",
        description="Command line interface for FRANK")
    argparser.add_argument("-q", "--query", type=str, nargs='+', # nargs='+' is a HACK for VSCode debugger
        default="", help="a query to be answered; a text or alist string query")
    argparser.add_argument("-c", "--context", type=str,
        default={}, help="context for the query; (default = {})")
    argparser.add_argument("-f", "--file", type=str,
        help="batch file; used when evaluating multiple questions in a file")
    argparser.add_argument("-o", "--output", type=str,
        default="output.json", help="file to output batch query results to; (default = output.json)")
    argparser.add_argument("-s", "--save-output", type=bool,
        default=False, help="If True, saves alist under ./logs/timestamp.json")
    argparser.add_argument("-p", "--plot", type=bool,
        default=False, help="If True, plots the inference graph")
    argparser.add_argument("-x", "--suppress-stdout", type=bool,
        default=False, help="If True, suppresses stdout")
    argparser.add_argument("-r", "--return-type", type=str,
        default="object", help="If 'object', returns the full graph object, if 'answer', returns the answer itself")

    args = argparser.parse_args()
    if args.file and args.query:
        print("\nThe --query option cannot be used with the --file option.")
    if args.file and args.context:
        print("\nCannot use --context together with the --file flag.")

    if args.file:
        batch(args.file, args.output)
    else:
        output = main(' '.join(args.query), args.context, args.plot, args.save_output,
            return_type=args.return_type, suppress_stdout=args.suppress_stdout)
        print(output)
