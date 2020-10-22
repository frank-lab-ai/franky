'''
File: frank_api.py
Description: REST-based API for FRANK
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)

'''

from flask import Flask, request, Response
import json
from frank.scheduler import Launcher
from frank.config import config
import frank.explain
import frank.query_parser.parser
from frank.graph import InferenceGraph
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
inference_graphs = {}

@app.route('/status')
def get_status():
    return 'FRANK API is running'


@app.route('/query', methods=['POST'])
def query_frank():
    query = request.json['alist']
    session_id = request.json['sessionId']
    Launcher().start_for_api(query, session_id, inference_graphs)
    response_data = {"session_id": session_id}
    response = Response(
        mimetype="application/json",
        response=json.dumps(response_data)
    )
    return response


@app.route('/answer/<sessionid>', methods=['GET'])
def getAnswer(sessionid):
    graph={'nodes':[], 'edges':[]}
    partial_answer = None
    answer = None
    trace = []
    if sessionid in inference_graphs:
        graph = inference_graphs[sessionid]['graph'].cytoscape_ui_graph()
        partial_answer = inference_graphs[sessionid]['intermediate_answer']
        answer = inference_graphs[sessionid]['answer']

    return Response(
        response=json.dumps({'trace': trace, 'answer': answer, 'graph_nodes': graph['nodes'],
                             'graph_edges': graph['edges'], 'partial_answer': partial_answer}),
        status=200,
        mimetype="application/json"
    )


@app.route('/alist/<sessionid>/<alistid>', methods=['GET'])
def getAlist(sessionid, alistid):
    alist_attributes = {}
    if sessionid in inference_graphs:        
        try:
            alist_attributes = inference_graphs[sessionid]['graph'].alist(alistid).attributes
        except:
            pass
    return Response(
        response=json.dumps(alist_attributes),
        status=200,
        mimetype="application/json"
    )


@app.route('/alist/<sessionid>/<alistid>/blanketlength/<blanketlength>', methods=['GET'])
def getAlistWithExplanationSameLenghts(sessionid, alistid, blanketlength):
    alist_attributes = {}
    explanation = {}
    if sessionid in inference_graphs:        
        try:
            alist_attributes = inference_graphs[sessionid]['graph'].alist(alistid).attributes
            exp = frank.explain.Explanation()
            explanation = exp.generateExplanation(
                            inference_graphs[sessionid]['graph'], 
                            node_id=alistid,
                            descendant_blanket_length=blanketlength, 
                            ancestor_blanket_length=blanketlength)
        except:
            pass
    
    responseObj = {"alist": alist_attributes, "explanation": explanation}

    return Response(
        response=json.dumps(responseObj),
        status=200,
        mimetype="application/json"
    )


@app.route('/alist/<sessionid>/<alistid>/blanketlengths/<anc_blanketlength>/<desc_blanketlength>', methods=['GET'])
def getAlistWithExplanationIndependentLengths(sessionid, alistid, anc_blanketlength, desc_blanketlength):
    alist_attributes = {}
    explanation = {}
    if sessionid in inference_graphs:        
        try:
            alist_attributes = inference_graphs[sessionid]['graph'].alist(alistid).attributes
            exp = frank.explain.Explanation()
            explanation = exp.generateExplanation(
                            inference_graphs[sessionid]['graph'], 
                            node_id=alistid,
                            descendant_blanket_length=anc_blanketlength, 
                            ancestor_blanket_length=desc_blanketlength)
        except:
            pass

    responseObj = {"alist": alist_attributes, "explanation": explanation}

    return Response(
        response=json.dumps(responseObj),
        status=200,
        mimetype="application/json"
    )


@app.route('/explain/<sessionid>/<alistid>/<blanketlength>')
def getExplanation(sessionid, alistid, blanketlength):
    explanation = {}
    if sessionid in inference_graphs:        
        try:
            exp = frank.explain.Explanation()
            explanation = exp.generateExplanation(
                            inference_graphs[sessionid]['graph'], 
                            node_id=alistid,
                            descendant_blanket_length=blanketlength, 
                            ancestor_blanket_length=blanketlength)
        except:
            pass
    return Response(
        response=json.dumps(explanation),
        status=200,
        mimetype="application/json"
    )

@app.route('/template/<querystring>', methods=['GET'])
def find_templates(querystring):
    parsedQuestion = {'alist': {}, 'templates': []}
    missing_field = False
    required_fields = [querystring]
    # check required fields
    for field in required_fields:
        if field is None:
            missing_field = True

    if not missing_field:
        if len(querystring.strip().split(' ')) >= 3:
            parser = frank.query_parser.parser.Parser()
            parsedQuestion = parser.getNextSuggestion(querystring)
        parsedQuestion['alist_string'] = json.dumps(parsedQuestion['alist'])

    return Response(
        response=json.dumps(parsedQuestion),
        status=200,
        mimetype="application/json"
    )


if __name__ == '__main__':
    app.run(port=config["frank_port"])
