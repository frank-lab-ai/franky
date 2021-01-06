'''
File: musicbrainz.py
Description: Basic wrapper for the MusicBrainz API.


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


def find_recording(title=None, artist=None, date=None):
    query = ''
    if title is not None:
        query += (' AND ' if len(query) > 0 else '' ) + f'title:"{title}"'
    if artist is not None:
        query += (' AND ' if len(query) > 0 else '' ) + f'artist:"{artist}"'
    if date is not None:
        query += (' AND ' if len(query) > 0 else '' ) + f'date:"{date}"'
    
    results = []
    try:
        response = requests.get(
            f'http://musicbrainz.org/ws/2/recording/?query={query}&inc=aliases&fmt=json')
        obj = response.json()
        if 'recordings' in obj:
            for item in obj['recordings']:
                results.append([
                    item['title'], 
                    item['first-release-date'],
                    item['artist-credit'][0]['name'],
                    item['score']
                    ])
                print(f"{item['title']} / {item['first-release-date']} / {item['artist-credit'][0]['name']} / item['score']")
    except Exception as ex:
        print("conceptnet query error: " + str(ex))
    return results

