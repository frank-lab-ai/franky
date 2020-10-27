'''
File: wikidata.py
Description: Interface to Wikidata
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)

'''

import requests
import urllib.parse
from pymongo import MongoClient
from frank.alist import Alist
from frank.alist import Attributes as tt
from frank import config
from frank.kb import mongo
import frank.util.utils
from datetime import datetime


def search_properties(search_term):
    results = []
    if search_term == 'type':
        results.append(('P31', 'type'))
    else:
        try:
            # client = MongoClient(host=config.config['mongo_host'], port=config.config['mongo_port'])
            client = mongo.getClient()
            db = client[config.config['mongo_db']]
            db_result = db['wikidataprops'].find(
                {'$text': {'$search': search_term}}, {
                    'score': {'$meta': 'textScore'}}
            )
            db_result.sort([('score', {'$meta': 'textScore'})]).limit(10)
            for r in db_result:
                results.append((r['id'], r['label'], r['score']))
        except Exception as ex:
            print('Error retreiving data from MongoDB: ' + str(ex.args))

    return results


def find_entity(entity_name: str):
    if not isinstance(entity_name, str):
        return ''
    if entity_name.strip() == '':
        return ''
    if entity_name.lower() == 'country':
        return 'Q6256'
    params = {
        'action': 'wbsearchentities',
        'search': entity_name,
        'language': 'en',
        'format': 'json'
    }
    response = requests.get(
        url='https://www.wikidata.org/w/api.php',
        params=params
    )
    data = response.json()
    ids = [x['id'] for x in data['search']]
    return ids[0] if len(ids) > 0 else ''


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
    entity_id = find_entity(alist.instantiation_value(tt.OBJECT))
    if not entity_id:
        return []

    # compose wikidata query
    query = ""
    if alist.get(tt.TIME):
        query = """
                SELECT DISTINCT ?sLabel (YEAR(?date) as ?year) WHERE{{
                ?s wdt:{property_id} wd:{entity_id}.
                OPTIONAL {{wd:{entity_id} pq:P585 ?date .}}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en".}} }
                }
                """.format(
            entity_id=entity_id,
            property_id=alist.get(tt.PROPERTY))
    else:
        query = """
                SELECT DISTINCT ?s ?sLabel  WHERE {{
                ?s wdt:{property_id} wd:{entity_id}.
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en".}}
                }}
                """.format(entity_id=entity_id, property_id=alist.get(tt.PROPERTY))

    params = {'format': 'json', 'query': query}
    response = requests.get(
        url='https://query.wikidata.org/sparql', params=params)
    alist_arr = []
    try:
        data = response.json()
        for d in data['results']['bindings']:
            data_alist = alist.copy()
            data_alist.set(tt.SUBJECT, d['sLabel']['value'])
            if 'year' in d:
                data_alist.set(tt.TIME, d['year']['value'])
            data_alist.data_sources= list(set(data_alist.data_sources + ['wikidata']))
            alist_arr.append(data_alist)
    except Exception as e:
        print("wikidata query response error: " + str(e))

    return alist_arr


def find_property_object(alist: Alist):
    entity_id = None
    wikidata_base_uri = 'http://www.wikidata.org/entity/'
    if 'http://www.wikidata.org/entity/' in alist.instantiation_value(tt.SUBJECT):
        entity_id = alist.instantiation_value(tt.SUBJECT)[len(wikidata_base_uri):]
    else:
        entity_id = find_entity(alist.instantiation_value(tt.SUBJECT))
        if not entity_id:
            return []

    # compose wikidata query
    query="""
        SELECT DISTINCT ?oLabel (YEAR(?date) as ?year) WHERE {{
            wd:{entity_id} p:{property_id} ?ob .
            ?ob ps:{property_id} ?o .
            OPTIONAL {{ ?ob pq:P585 ?date . }}
            OPTIONAL {{ ?ob pq:P580 ?date . }}
            OPTIONAL {{ FILTER (YEAR(?date) = {time}) . }}
            SERVICE wikibase:label {{  bd:serviceParam wikibase:language "en" .  }}  }}
            ORDER By DESC(?year)
        """.format(
                entity_id=entity_id,
                property_id=alist.get(tt.PROPERTY),
                time=alist.get(tt.TIME).replace(".0", "") if alist.get(tt.TIME) else '0')

    params = {'format': 'json', 'query': query}
    response = requests.get(
        url='https://query.wikidata.org/sparql', params=params)
    alist_arr = []
    try:
        data = response.json()
        ctx = {}
        if data['results']['bindings']:
            ctx = alist.get(tt.CONTEXT)
            ctx = {**ctx[0], **ctx[1], **ctx[2]} if ctx else {}

        for d in data['results']['bindings']:
            # if alist has explicit time and no context, 
            # or has explicit time not from context 
            # then result must include time
            if (alist.get(tt.TIME) and tt.TIME not in ctx): 
                if ('year' in d) and (d['year']['value'] == alist.get(tt.TIME)):
                    data_alist = alist.copy()
                    data_alist.set(tt.OBJECT, d['oLabel']['value'])                    
                    data_alist.set(tt.TIME, d['year']['value'])
                    data_alist.data_sources= list(set(data_alist.data_sources + ['wikidata']))
                    alist_arr.append(data_alist)

            # else if time is injected from context
            # then only append results that have no time only if the dataset is empty..
            ## wikidata returns bindings with the time attribute first so this works
            elif alist.get(tt.TIME) and tt.TIME in ctx: 
                current_year = str(datetime.now().year)
                if (('year' in d) and (d['year']['value'] == alist.get(tt.TIME))) or  \
                    ((((('year' in d) and (d['year']['value'] != alist.get(tt.TIME))) and len(alist_arr) == 0) or  \
                    (('year' not in d) and len(alist_arr) == 0)) and \
                    (alist.get(tt.TIME) == current_year and (not frank.util.utils.is_numeric(d['oLabel']['value'])))):
                        # last condition: append this value only if time (i.e the context time) is the current year and the data value is not numeric.                        

                        data_alist = alist.copy()
                        data_alist.set(tt.OBJECT, d['oLabel']['value'])                    
                        # if 'year' in d: # use time in dataset optionally
                        #     data_alist.set(tt.TIME, d['year']['value'])                    
                        data_alist.data_sources= list(set(data_alist.data_sources + ['wikidata']))
                        alist_arr.append(data_alist)
            else:
                data_alist = alist.copy()
                data_alist.set(tt.OBJECT, d['oLabel']['value'])
                # if 'year' in d: # use time in dataset optionally
                #     data_alist.set(tt.TIME, d['year']['value'])
                data_alist.data_sources= list(set(data_alist.data_sources + ['wikidata']))
                alist_arr.append(data_alist)

    except Exception as ex:
        print("wikidata query response error: " + str(ex))

    return alist_arr


def find_propert_time(alist: Alist):
    pass


def isLocation(entity_name: str, property_id: str):
    entity_id = find_entity(entity_name)
    if not entity_id:
        return []

    query = """
            SELECT DISTINCT ?o ?oLabel
            WHERE {{wd:{entity_id} wdt:{property_id} ?o .
            SERVICE wikibase:label {{bd:serviceParam wikibase:language "en".}} }}
            """.format(entity_id=entity_id, property_id=property_id)
    params = {'format': 'json', 'query': query}
    response = requests.get(
        url='https://query.wikidata.org/sparql', params=params)
    results = []
    try:
        data = response.json()
        for d in data['results']['bindings']:
            results.append(d['oLabel']['value'])
    except Exception:
        print("wikidata query response error")
    return results


def findEntitiesOfGivenType(entity_class: str):
    entity_class_id = ''
    if entity_class == 'country':
        entity_class_id = 'Q6256'
    elif entity_class == 'city':
        entity_class_id = 'Q515'
    else:
        entity_class_id = find_entity(entity_class)

    if not entity_class_id:
        return None

    query = """
            SELECT DISTINCT ?o ?oLabel
            WHERE {{?o wdt:P31 wd:{entity_class_id} .
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en".}} }}
            ORDER BY ?oLabel
            """.format(entity_class_id=entity_class_id)
    params = {'format': 'json', 'query': query}
    response = requests.get(
        url='https://query.wikidata.org/sparql', params=params)
    results = []
    try:
        data = response.json()
        for d in data['results']['bindings']:
            results.append(d['oLabel']['value'])
    except Exception:
        print("wikidata query response error")
    return results


def find_entity_property_with_id(entity_name: str, property_id: str):
    entity_id = find_entity(entity_name)
    if not entity_id:
        return None

    query = """
            SELECT DISTINCT ?o ?oLabel
            WHERE {{wd:{entity_id} wdt:{property_id} ?o .
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en".}} }}
            ORDER BY ?oLabel
            """.format(entity_id=entity_id, property_id=property_id)
    params = {'format': 'json', 'query': query}
    response = requests.get(
        url='https://query.wikidata.org/sparql', params=params)
    results = []
    try:
        data = response.json()
        for d in data['results']['bindings']:
            results.append(d['oLabel']['value'])
    except Exception:
        print("wikidata query response error")
    return results


def find_sub_elements(entity_name: str, entity_class: str, sub_class: str):
    property_id = ''
    if entity_class.lower() == 'country':
        property_id = 'P17'
    elif entity_class.lower() == 'continent':
        property_id = 'P30'
    entity_id = find_entity(entity_name)

    sub_class_id = ''
    if sub_class.lower() == 'country':
        sub_class_id = 'Q6256'
    else:
        sub_class_id = find_entity(sub_class)
    if not entity_id:
        return None

    query = """
            SELECT DISTINCT ?o ?oLabel
            WHERE {{ ?o wdt:{property_id} wd:{entity_id} .
            ?o wdt:P31 wd:{sub_class_id} .
            SERVICE wikibase:label {{bd:serviceParam wikibase:language "en".}}  }}
            ORDER BY ?oLabel
            """.format(entity_id=entity_id, sub_class_id=sub_class_id, property_id=property_id)
    params = {'format': 'json', 'query': query}
    response = requests.get(
        url='https://query.wikidata.org/sparql', params=params)
    results = []
    try:
        data = response.json()
        for d in data['results']['bindings']:
            results.append(d['oLabel']['value'])
    except Exception:
        print("wikidata query response error")
    return results


def find_geopolitical_subelements(entity_name: str, sub_class: str):
    entity_id = find_entity(entity_name)
    sub_class_id = 'P30'
    if sub_class.lower() == 'country':
        sub_class_id = 'Q6256'
        super_class_id = 'P30'
    elif sub_class.lower() == 'city':
        sub_class_id = 'Q515'
        super_class_id = 'P17'
    else:
        sub_class_id = find_entity(sub_class)
    if not entity_id:
        return None

    query = f"""
            SELECT DISTINCT ?o ?oLabel
            WHERE {{ ?o wdt:{super_class_id} wd:{entity_id} .
            ?o wdt:P31 wd:{sub_class_id} .
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en".}} }}
            ORDER BY ?oLabel
            """
    params = {'format': 'json', 'query': query}
    response = requests.get(
        url='https://query.wikidata.org/sparql', params=params)
    results = []
    try:
        data = response.json()
        for d in data['results']['bindings']:
            results.append(d['oLabel']['value'])
    except Exception:
        print("wikidata query response error")
    return results


def _part_of_relation_subject(entity_name: str, relationName: str):
    results = []
    entityType = find_entity_property_with_id(entity_name, "P31")
    if entityType:
        if len(set(['continent']) & set(entityType)) > 0 and relationName.lower() == 'location':
            f = Alist(**{tt.PROPERTY: 'P30', tt.OBJECT: entity_name})
            results = [x.get(tt.SUBJECT) for x in find_property_subject(f)]
            return results
        elif len(set(['country','sovereign state']) & set(entityType)) > 0  and relationName.lower() == 'location':
            f = Alist(**{tt.PROPERTY: 'P131', tt.OBJECT: entity_name})
            results = [x.get(tt.SUBJECT) for x in find_property_subject(f)]
            return results
        else:
            return results
    else:
        return results


def part_of_relation_subject(alist: Alist):
    results = []
    for r in _part_of_relation_subject(alist.get(tt.OBJECT), "location"):
        fact_alist = alist.copy()
        fact_alist.data_sources= list(set(fact_alist.data_sources + ['wikidata']))
        fact_alist.set(tt.SUBJECT, r)
        results.append(fact_alist)
    return results


# entity partOf ?x
def _part_of_relation_object(entity_name: str, relationName: str):

    results = []
    entityType = find_entity_property_with_id(entity_name, "P31")
    if entityType:
        if 'country' in entityType and relationName.lower() == 'location':
            f = Alist(**{tt.PROPERTY: 'P30', tt.OBJECT: entity_name})
            results = [x for x in find_entity_property_with_id(
                entity_name, "P30")]
            return results
        elif 'city' in entityType and relationName.lower() == 'location':
            f = Alist(**{tt.PROPERTY: 'P131', tt.OBJECT: entity_name})
            results = [x for x in find_entity_property_with_id(
                entity_name, "P17")]
            return results
        else:
            return results
    else:
        return results


def part_of_relation_object(alist: Alist):
    results = []
    for r in _part_of_relation_object(alist.get(tt.SUBJECT), "location"):
        fact_alist = alist.copy()
        fact_alist.data_sources= list(set(fact_alist.data_sources + ['wikidata']))
        fact_alist.set(tt.OBJECT, r)
        results.append(fact_alist)
    return results


def part_of_geopolitical_subject(alist: Alist):
    results = []
    geopolitical_type = alist.get(tt.PROPERTY).split(':')
    for r in find_geopolitical_subelements(alist.get(tt.OBJECT), geopolitical_type[-1]):
        fact_alist = alist.copy()
        fact_alist.data_sources= list(set(fact_alist.data_sources + ['wikidata']))
        fact_alist.set(tt.SUBJECT, r)
        results.append(fact_alist)
    return results

def find_location_of_entity(entity_name: str):
    """
    Returns an array of (entity_uri, location_uri, location_label)
    """
    # outcomings are a proxy for popularity ranking
    query = f"""
            SELECT DISTINCT ?entity ?entityLabel ?location ?locationLabel ?outcoming
            WHERE {{ 
                VALUES ?town_city_region_country {{wd:Q3957 wd:Q515 wd:Q82794 wd:Q6256 wd:Q3624078}}
                ?entity rdfs:label "{entity_name}"@en .
                ?entity (wdt:P31/(wdt:P279*)) ?town_city_region_country.
                OPTIONAL {{?entity wdt:P131/(wdt:P131)* ?location . }}
                OPTIONAL {{?entity wdt:P30 ?location . }}
                ?entity wikibase:statements ?outcoming .
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en".}} 
            }}
            ORDER BY DESC(?outcoming)
            LIMIT 500            
            """
    params = {'format': 'json', 'query': query}
    response = requests.get(
        url='https://query.wikidata.org/sparql', params=params)
    results = []
    try:
        data = response.json()
        for d in data['results']['bindings']:
            if 'location' in d and 'locationLabel' in d:
                results.append((d['entity']['value'],
                                d['location']['value'],
                                d['locationLabel']['value']
                            ))
    except Exception:
        print("wikidata query response error")
    return results