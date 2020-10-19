'''
File: frank_api.py
Description: REST-based API for FRANK
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)

'''

from flask import Flask, request, Response
import json
from frank.scheduler import Launcher
from frank.config import config
import redis
import frank.explain
import frank.cache.neo4j
import frank.query_parser.parser
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/status')
def hello_world():
    return 'FRANK API is running'


@app.route('/query', methods=['POST'])
def query_frank():
    query = request.json['alist']
    session_id = request.json['sessionId']
    Launcher().start_for_api(query, session_id)
    response_data = {"session_id": session_id}
    response = Response(
        mimetype="application/json",
        response=json.dumps(response_data)
    )
    return response


@app.route('/answer/<sessionid>', methods=['GET'])
def getAnswer(sessionid):
    r = redis.Redis(host=config['redis_host'], port=6379)
    _trace = r.lrange(sessionid + ':trace', 0, -1)
    _answer = r.lrange(sessionid + ':answer', 0, -1)
    _partialAnswer = r.get(sessionid + ':partialAnswer')
    trace = [x.decode('utf-8') for x in _trace[0:100]]
    answer = [json.loads(x.decode('utf-8')) for x in _answer]
    partialAnswer = {}

    if _partialAnswer is not None:
        try:
            partialAnswer = json.loads(
                _partialAnswer.decode('utf-8').replace("\'", "\""))
        except Exception as ex:
            pass
    if not partialAnswer:
        try:
            partialAnswer = json.loads(
                _partialAnswer.decode('utf-8').replace('"', '\"'))
        except Exception as ex:
            pass
    graph =frank.cache.neo4j.get_graph(sessionId=sessionid)

    return Response(
        response=json.dumps({'trace': trace, 'answer': answer, 'graph_nodes': graph['nodes'],
                             'graph_edges': graph['edges'], 'partial_answer': partialAnswer}),
        status=200,
        mimetype="application/json"
    )


@app.route('/alist/<sessionid>/<alistid>', methods=['GET'])
def getAlist(sessionid, alistid):
    r = redis.Redis(host=config['redis_host'], port=6379)
    _alist = r.get(sessionid + ':alist:' + alistid)
    alist = {}
    if _alist is not None:
        _alist = _alist.decode('utf-8').replace("\'",
                                                "\"").replace("\"{", "{").replace("}\"", "}")
        alist = json.loads(_alist)
    return Response(
        response=json.dumps(alist),
        status=200,
        mimetype="application/json"
    )


@app.route('/alist/<sessionid>/<alistid>/blanketlength/<blanketlength>', methods=['GET'])
def getAlistWithExplanationSameLenghts(sessionid, alistid, blanketlength):
    alist = {}
    explanation = {}
    # get alist
    alist = frank.cache.neo4j.get_node(sessionid, alistid)

    # get explanation
    exp = frank.explain.Explanation()
    alists = exp.read_blanket_nodes(sessionid, alistid, blanketlength)
    explanation = exp.generateExplanation(node_id=alistid, graph_alists=alists,
                                          descendant_blanket_length=blanketlength, ancestor_blanket_length=blanketlength)

    responseObj = {"alist": alist, "explanation": explanation}

    return Response(
        response=json.dumps(responseObj),
        status=200,
        mimetype="application/json"
    )


@app.route('/alist/<sessionid>/<alistid>/blanketlengths/<anc_blanketlength>/<desc_blanketlength>', methods=['GET'])
def getAlistWithExplanationIndependentLengths(sessionid, alistid, anc_blanketlength, desc_blanketlength):
    alist = {}
    explanation = {}
    # get alist
    alist = frank.cache.neo4j.get_node(sessionid, alistid)

    # get explanation
    exp = frank.explain.Explanation()
    alists = exp.read_blanket_nodes(sessionid, alistid, max(
        anc_blanketlength, desc_blanketlength))
    explanation = exp.generateExplanation(node_id=alistid, graph_alists=alists,
                                          descendant_blanket_length=desc_blanketlength, ancestor_blanket_length=anc_blanketlength)

    responseObj = {"alist": alist, "explanation": explanation}

    return Response(
        response=json.dumps(responseObj),
        status=200,
        mimetype="application/json"
    )


@app.route('/explain/<sessionid>/<alistid>/<blanketlength>')
def getExplanation(sessionid, alistid, blanketlength):
    exp = frank.explain.Explanation()
    alists = exp.read_blanket_nodes(sessionid, alistid, blanketlength)
    explanation = exp.generateExplanation(node_id=alistid, graph_alists=alists,
                                          descendant_blanket_length=blanketlength, ancestor_blanket_length=blanketlength)
    return Response(
        response=json.dumps(explanation),
        status=200,
        mimetype="application/json"
    )

# Find a template


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
