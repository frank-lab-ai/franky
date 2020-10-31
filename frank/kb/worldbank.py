'''
File: worldbank.py
Description: Interface to the World Bank dataset.
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)

'''

import requests
import urllib.parse
from frank.alist import Alist
from frank.alist import Attributes as tt
from frank.kb import rdf
from frank.kb import mongo
from frank import config
import frank.dataloader

indicators = {
    "population": "SP.POP.TOTL",
    "gdp": "NY.GDP.MKTP.CD",
    "urban population": "SP.URB.TOTL",
    "rural population": "SP.RUR.TOTL",
    "male population": "SP.POP.TOTL.MA.IN",
    "female population": "SP.POP.TOTL.FE.IN",
    "energy consumption": "1.1_TOTAL.FINAL.ENERGY.CONSUM",
    "renewable energy consumption": "3.1_RE.CONSUMPTION",
    "hydro energy consumption": "3.1.3_HYDRO.CONSUM",
    "solar energy consumption": "3.1.6_SOLAR.CONSUM",
    "electricity output": "4.1.1_TOTAL.ELECTRICITY.OUTPUT"
}

common_synonyms = {
        "People's Republic of China": "China",
        "UK": "United Kingdom",
        "USA": "United States of America"
    }


def search_properties(search_term):
    results = []
    if search_term in indicators:
        results.append((indicators[search_term], search_term, 1)) #(property_id, label, match_score)
    return results


def find_property_values(alist: Alist, search_element: str):
    if not alist.get(tt.PROPERTY):
        return {}

    if search_element == tt.SUBJECT:
        pass
    elif search_element == tt.OBJECT:
        return find_property_object(alist)
    elif search_element == tt.TIME:
        pass


def find_property_object(alist: Alist):
    results = []
    subj_instantiation = alist.instantiation_value(tt.SUBJECT)
    if isinstance(subj_instantiation, str):
        country_id = getCountryPropertyDb(subj_instantiation.replace("_", " "), "id")
    else:
        return results
    if not country_id:
        return results

    try:
        params = {'date': str(alist.get(tt.TIME)).replace(
            ".0", ""), 'format': 'json', 'per_page': 1000}
        response = requests.get(
            url=f'http://api.worldbank.org/v2/countries/{country_id}/indicators/{alist.get(tt.PROPERTY)}',
            params=params)
        try:
            data = response.json()
            if len(data) > 1 and data[1]:
                for d in data[1]:
                    data_alist = alist.copy()
                    data_alist.set(tt.OBJECT, d['value'])
                    data_alist.data_sources = list(set(data_alist.data_sources + ['worldbank']))
                    results.append(data_alist)
        except Exception as ex:
            print("worldbank query response error: " + str(ex))
    except Exception as ex:
        print("worldbank query error: " + str(ex))

    return results


def getCountryPropertyDb_db(countryName, countryProperty):
    result = ''
    try:
        client = mongo.getClient()
        db = client[config.config['mongo_db']]
        db_result = db['wb_countries'].find({'name': countryName})
        for r in db_result:
            if countryProperty in r:
                result = r[countryProperty]
                break
    except Exception as ex:
        print('Error retreiving data from MongoDB: ' + str(ex.args))

    return result

def getCountryPropertyDb(countryName, countryProperty):
    if countryName in common_synonyms:
        countryName = common_synonyms[countryName]
    result = ''
    
    if config.config['use_db']:
        return getCountryPropertyDb_db(countryName, countryProperty)
    else:        
        results = []
        df = frank.dataloader.load_worldbank_countries()
        df_filtered_prop = df[df['name'] == countryName][countryProperty]
        if len(df_filtered_prop) > 0:
            result = df_filtered_prop.iloc[0]

        return result

def find_location_of_entity_in_db(entity_name: str):
    """
    Returns an array of (entity id, location id, location_label)
    """
    results = []
    if entity_name in common_synonyms:
        entity_name = common_synonyms[entity_name]
    try:
        client = mongo.getClient()
        db = client[config.config['mongo_db']]
        db_result = db['wb_countries'].find({'name': entity_name})
        for d in db_result:
            results.append((d['id'],
                            d['region']['id'],
                            d['region']['value']
                           ))            

        db_result2 = db['wb_countries'].find({'capitalCity': entity_name})
        for d in db_result2:
            results.append((entity_name, d['id'], d['name']))

    except Exception as ex:
        print('Error retreiving WB data from MongoDB: ' + str(ex.args))
    return results

def find_location_of_entity(entity_name: str):
    if config.config['use_db']:
        return find_location_of_entity_in_db(entity_name)
    else:        
        results = []
        df = frank.dataloader.load_worldbank_countries()
        df_filtered = df[df['name'] == entity_name]
        df_filtered  = df_filtered[['id','region.id','region.value']]
        results = [tuple(x) for x in df_filtered.to_numpy()]
        # for d in df_filtered:
        #     results.append((d['id'],
        #                     d['region.id'],
        #                     d['region.value']
        #                    ))

        df_filtered = df[df['capitalcity'] == entity_name]
        df_filtered  = df_filtered[['id','name']]
        result2 = [(entity_name, x[0], x[1]) for x in df_filtered.to_numpy()]
        results.extend(result2)
        # for d in df_filtered:
        #     results.append((entity_name, d['id'], d['name']))
        return results
            