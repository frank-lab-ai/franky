'''
File: sparqlEndpoint.py
Description: Interface to various SPARQL-based endpoints.


'''

import urllib.parse

import requests

from frank import config
from frank.alist import Alist
from frank.alist import Attributes as tt


def find_sub_location(entity: str):
    results = []
    if not entity:
        return results

    query = """
            prefix gnp: <http://www.geonames.org/property#>
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?subItemName WHERE {{
            ?s rdfs:label ?place .
            ?l gnp:location ?s .
            ?l rdfs:label ?subItemName .
            FILTER REGEX(str(?place),'^{entity}$','i')
            }}
          """.format(entity=entity)
    params = {'format': 'json', 'query': query}
    response = requests.get(
        url=config.config['sparql_endpoint'], params=params)
    try:
        data = response.json()
        for d in data['results']['bindings']:
            results.append(d['subItemName']['value'])
    except Exception as ex:
        print("error accessing data from sparql endpoint: " + str(ex))
    return results


def getCountryProperty(countryName, countryProperty):
    propvalue = ''
    # compose sparql query
    query = f"""
                prefix gnp: <http://www.geonames.org/property#>
                prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT ?s ?p ?o
                WHERE{{
                ?subj rdfs:label ?s .
                FILTER REGEX(str(?s),'^{countryName.replace("'","").replace("_"," ")}$','i') .
                ?subj gnp:{countryProperty.replace("'","")} ?o .
                }}
        """
    params = {'format': 'json', 'query': query}
    response = requests.get(
        url=config.config['sparql_endpoint'], params=params)
    try:
        data = response.json()
        for d in data['results']['bindings']:
            propvalue = d['o']['value']
    except Exception as ex:
        print("error accessing data from sparql endpoint: " + str(ex))
    return propvalue
