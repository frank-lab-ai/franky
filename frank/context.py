from datetime import datetime

from frank.alist import Alist
from frank.alist import Attributes as tt
from frank.alist import Contexts as ctx
from frank.kb import wikidata, worldbank


def get_user_context(alist, key):
    return _get_context(alist, 0, key)


def set_user_context(alist, key, value):
    _set_context(alist, 0, key, value)


def get_env_context(alist, key):
    return _get_context(alist, 1, key)


def set_env_context(alist, key, value):
    _set_context(alist, 1, key, value)


def get_query_context(alist, key):
    return _get_context(alist, 2, key)


def set_query_context(alist, key, value):
    _set_context(alist, 2, key, value)


def _get_context(alist: Alist, idx, key):
    if not alist.get(tt.CONTEXT):
        return None
    try:
        if key in alist.attributes[tt.CONTEXT][idx]:
            return alist.attributes[tt.CONTEXT][idx][key]
        else:
            return None
    except:
        return None


def _set_context(alist: Alist, idx, key, value):
    if not alist.attributes[tt.CONTEXT]:
        alist.attributes[tt.CONTEXT] = [{}, {}, {}]
    try:
        alist.attributes[tt.CONTEXT][idx][key] = value
    except:
        pass


def inject_retrieval_context(alist: Alist, source) -> Alist:
    """
    Inject context values into alist attributes to be used for Information Retrieval from KBs.
    """

    context = alist.get(tt.CONTEXT)
    if not context:
        return alist

    context = alist.get(tt.CONTEXT)
    context_store = {}
    context_store = {**context[0], **context[1],
                     **context[2]} if context else {}
    for a in alist.attributes.keys():
        if a in context_store:
            if type(context_store[a]) is dict and source in context_store[a]:
                alist.set(a, context_store[a][source])
            elif type(context_store[a]) is not dict:
                alist.set(a, context_store[a])
    return alist


def inject_query_context(alist: Alist) -> Alist:
    """
    Inject context values into query alist.
    """
    context = alist.get(tt.CONTEXT)
    if not context and len(context) < 2:
        return alist

    if len(context) == 3 and \
            ctx.accuracy not in context[0] and \
            ctx.device in context[1]:
        if context[1][ctx.device] == 'phone':
            context[0][ctx.accuracy] = 'low'
        elif context[1][ctx.device] == 'computer':
            context[0][ctx.accuracy] = 'high'

    # alist context
    alist.set(tt.CONTEXT, context)

    # check for time in alist
    if not alist.get(tt.TIME):
        time = get_env_context(alist, ctx.datetime)
        year = ''
        if time:
            year = datetime.strptime(time, '%Y-%m-%d %H:%M:%S').year
            year = str(year)
        alist.set(tt.TIME, year)
        set_query_context(alist, tt.TIME, year)

    # disambiguate entity based on user location context
    user_place = get_env_context(alist, ctx.place)
    user_nationality = get_user_context(alist, ctx.nationality)
    s_context = {}
    if user_place:
        if alist.get(tt.SUBJECT) == '':
            # if subject is empty, use place context
            alist.set(tt.SUBJECT, user_place)
            for source_name, source in {'wikidata': wikidata, 'worldbank': worldbank}.items():
                locations = source.find_location_of_entity(
                    alist.get(tt.SUBJECT))
                set_flag = False
                # use nationality as context for the user's location if no subject
                if user_nationality:
                    for loc in locations:
                        if user_nationality == loc[2]:
                            s_context[source_name] = loc[0]
                            set_flag = True
                            break

                if not set_flag and locations and source_name in ['wikidata']:
                    # if no location matched the nationality, use the first location
                    s_context[source_name] = locations[0][0]
                    # set_query_context(alist, tt.SUBJECT, {source_name: locations[0][0]})
        else:
            for source_name, source in {'wikidata': wikidata, 'worldbank': worldbank}.items():
                locations = source.find_location_of_entity(
                    alist.get(tt.SUBJECT))
                set_flag = False
                for loc in locations:
                    if user_place == loc[2]:
                        s_context[source_name] = loc[0]
                        set_flag = True
                        break
                # if set_flag:
                #     set_query_context(alist, tt.SUBJECT, s_context)
                if not set_flag and locations and source_name in ['wikidata']:
                    # if no location matched the nationality, use the first location
                    s_context[source_name] = locations[0][0]
                    # set_query_context(alist, tt.SUBJECT, {source_name: locations[0][0]})
        if s_context:
            set_query_context(alist, tt.SUBJECT, s_context)

    return alist


def flush(alist: Alist, items) -> Alist:
    """
    Flush query context that whose corresponding alist attribute value is different
    """
    for k in items:
        try:
            if k in alist.get(tt.CONTEXT)[2] and alist.get(tt.CONTEXT)[2][k] != alist.get(k):
                del alist.get(tt.CONTEXT)[2][k]
        except:
            pass

    return alist
