'''
File: conceptnet.py
Description: Interface to the ConceptNet KB.
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)
Copyright 2014 - 2020  Kobby K.A. Nuamah
'''

import requests
import urllib.parse
from frank.alist import Alist
from frank.alist import Attributes as tt
from frank import config


def search_properties(search_term):
    results = []

    return results


def find_entity(entity_name: str):
    return None


def find_property_values(alist: Alist, search_element: str):
    if not alist.get(tt.PROPERTY):
        return {}

    if search_element == tt.SUBJECT:
        return find_property_subject(alist)
    elif search_element == tt.OBJECT:
        return find_property_object(alist)
    elif search_element == tt.TIME:
        return find_propert_time(alist)


def find_property_subject(alist: Alist):
    return None


def find_property_object(alist: Alist):
    return None


def find_propert_time(alist: Alist):
    pass


def find_instance_elements(entity_name: str):
    results = []
    try:
        response = requests.get(
            f'http://api.conceptnet.io/query?end=/c/en/{entity_name.lower()}&rel=/r/IsA')
        obj = response.json()
        results = [edge['start']['label'] for edge in obj['edges']]
    except Exception as ex:
        print("conceptnet query error: " + str(ex))
    return results


def find_relation_subject(entity_name: str, relationName: str):
    results = []
    try:
        response = requests.get(
            f'http://api.conceptnet.io/query?end=/c/en/{entity_name.lower()}&rel=/r/{relationName}')
        obj = response.json()
        results = [edge['start']['label'] for edge in obj['edges']]
    except Exception as ex:
        print("conceptnet query error: " + str(ex))
    return results


def part_of_relation_subject(alist: Alist):
    results = []
    for r in find_relation_subject(alist.get(tt.OBJECT), "location"):
        factAlist = alist.copy()
        factAlist.data_sources.add('wikidata')
        factAlist.set(tt.SUBJECT, r)
        results.append(factAlist)
    return results


# entity partOf ?x
def find_relation_object(entity_name: str, relationName: str):
    results = []
    try:
        response = requests.get(
            f'http://api.conceptnet.io/query?start=/c/en/{entity_name.lower()}&rel=/r/{relationName}')
        obj = response.json()
        results = [edge['end']['label'] for edge in obj['edges']]
    except Exception as ex:
        print("conceptnet query error: " + str(ex))
    return results


def part_of_relation_object(alist: Alist):
    results = []
    for r in find_relation_object(alist.get(tt.SUBJECT), "PartOf"):
        factAlist = alist.copy()
        factAlist.data_sources.add('wikidata')
        factAlist.set(tt.OBJECT, r)
        results.append(factAlist)
    return results
