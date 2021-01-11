'''
File: musicbrainz.py
Description: Basic wrapper for the MusicBrainz API.


'''

import requests
from datetime import datetime
import urllib.parse
from frank.alist import Alist
from frank.alist import Attributes as tt
from frank import config

#format : artist sang/recorded title in date

def search_properties(search_term):
    results = []
    if search_term:
        results.append((search_term, search_term, 1.0))
    return results


def find_entity(entity_name: str):
    if entity_name:
        return entity_name
    return None


def find_property_values(alist: Alist, search_element: str):
    prop = alist.get(tt.PROPERTY)
    if not prop or prop not in ['sing', 'sang', 'sung', 'recorded', 'performed']:
        return None

    if search_element == tt.SUBJECT:
        return find_property_subject(alist)
    elif search_element == tt.OBJECT:
        return find_property_object(alist)
    elif search_element == tt.TIME:
        return find_propert_time(alist)


def find_property_subject(alist: Alist):
    alist_arr = []
    results = find_recording(
                artist=None,
                title=alist.get(tt.OBJECT),
                date=alist.get(tt.TIME))
    for item in results:
        data_alist = alist.copy()
        data_alist.set(tt.SUBJECT, item['artist'])
        data_alist.data_sources = list(
            set(data_alist.data_sources + ['musicbrainz']))
        alist_arr.append(data_alist)
        
    return alist_arr


def find_property_object(alist: Alist):
    alist_arr = []
    results = find_recording(
                artist=alist.get(tt.SUBJECT),
                title=None,        
                date=alist.get(tt.TIME))

    for item in results:
        data_alist = alist.copy()
        data_alist.set(tt.OBJECT, item['title'])
        data_alist.data_sources = list(
            set(data_alist.data_sources + ['musicbrainz']))
        alist_arr.append(data_alist)
        
    return alist_arr


def find_propert_time(alist: Alist):
    alist_arr = []
    results = find_recording(
                artist=alist.get(tt.SUBJECT),
                title=alist.get(tt.OBJECT),
                date=None)
    
    # parse date formats and sort in reverse
    FORMATS = ['%Y', '%Y-%m-%d']
    for r in results:
        date = ''
        for fmt in FORMATS:
            try: 
                r['date_fmt'] = datetime.now()
                date = datetime.strptime(r['date'], fmt)
                r['date'] = date.strftime('%Y')
            except:
                pass
    results_sorted = [k for k in sorted(results, key=lambda x: x['date_fmt'])]


    for item in results_sorted:
        data_alist = alist.copy()
        data_alist.set(tt.TIME, item['date'])
        data_alist.data_sources = list(
            set(data_alist.data_sources + ['musicbrainz']))
        alist_arr.append(data_alist)    
        break #  greedy; take only the first answer returned
        
    return alist_arr


def find_recording(title=None, artist=None, date=None):
    date = None if date is None or str(date).strip() == '' else date
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
            maxScore = -1
            for item in obj['recordings']:
                if item['score'] < maxScore:
                    break
                
                maxScore = item['score']
                artists = ', '.join([ac['name'] for ac in item['artist-credit'] ])
                results.append({
                    'title': item['title'], 
                    'date': item['first-release-date'],
                    'artist': artists,
                    'score': item['score']
                })

                
                # print(f"{item['title']} / {item['first-release-date']} / {item['artist-credit'][0]['name']} / item['score']")
    except Exception as ex:
        print("conceptnet query error: " + str(ex))
    return results

