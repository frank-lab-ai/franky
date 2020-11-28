'''
File: neo4j.py
Description: 


'''

from neo4j import GraphDatabase
from frank.alist import Alist
from frank.alist import Attributes as tt
from frank.alist import States as states
from frank.alist import Branching as branching
from frank import config


def get_driver():
    uri = f"bolt://{config.config['neo4j_host']}:{config.config['neo4j_port']}"
    driver = GraphDatabase.driver(uri, auth=(
        config.config['neo4j_username'], config.config['neo4j_password']), encrypted=False)
    return driver


def _create_update(tx, alist: Alist, parent: Alist, edge, sessionId):
    pid = -1
    if alist.parent:
        pid = alist.parent[0].id
    sources = ','.join(alist.data_sources)

    s = f"{{ sessionId:'{sessionId}', id:{alist.id}, parentId:'{pid}', ntype:'{alist.node_type}', {alist_attr_reformat(alist.get_alist_json_with_metadata())}, src:'{sources}', nstate:{alist.state} }}"

    if parent is None:
        r = tx.run(f"MERGE (a:Alist {{ sessionId:'{sessionId}', id:'{alist.id}' }})"
                   f"ON CREATE SET a = {s}"
                   f"ON MATCH SET a = {s}"
                   "RETURN id(a)")
        return r.single().value()
    else:
        r = tx.run(f"MATCH (a:Alist {{ sessionId:'{sessionId}', id:'{parent.id}' }}) "
                   f"MERGE (a)-[:{edge}]->(b:Alist {s}) "
                   "RETURN id(a)")
        return r.single().value()


def _get_graph(tx, sessionId):
    alists = {}
    edges = {}
    pendingParentIds = {}
    results = tx.run(f"MATCH p=(n:Alist {{sessionId:'{sessionId}' }})-[]-(m) "
                     f"WITH *, relationships(p) as rp "
                     "RETURN n,m,rp")
    for node in results:
        if node[2]:
            for rel in node[2]:
                if rel.start_node._properties['id'] not in alists:
                    id = rel.start_node._properties["id"]
                    label = id
                    nodeType = rel.start_node._properties["ntype"]
                    nodeState = rel.start_node._properties["nstate"]
                    op = rel.start_node._properties["h"]
                    if len(id) > 5:
                        label = f"{id[0:2]}..{id[-3]}{id[-2]}{id[-1]}"
                    alists[rel.start_node._properties['id']] = {
                        "id": id, "label": label, "ntype": nodeType, "nstate": nodeState, "h": op}
                if rel.end_node._properties['id'] not in alists:
                    id = rel.end_node._properties["id"]
                    label = id
                    nodeType = rel.end_node._properties["ntype"]
                    nodeState = rel.end_node._properties["nstate"]
                    op = rel.end_node._properties["h"]
                    if len(id) > 5:
                        label = f"{id[0:2]}..{id[-3]}{id[-2]}{id[-1]}"
                    alists[rel.end_node._properties['id']] = {
                        "id": id, "label": label, "ntype": nodeType, "nstate": nodeState, "h": op}
            edge_id = f"{rel.start_node._properties['id']}-{rel.end_node._properties['id']}"
            if edge_id not in edges:
                edges[edge_id] = {"source": rel.start_node._properties['id'],
                                  "target": rel.end_node._properties['id'],
                                  "label": str(rel.type).lower()}

    alist_list = [{"data": y} for _, y in alists.items()]
    edges_list = [{"data": y} for _, y in edges.items()]
    return {"nodes": alist_list, "edges": edges_list}


def _get_node(tx, sessionId, alistNodeId):
    alist = {}
    results = tx.run(
        f"MATCH (n:Alist {{sessionId:'{sessionId}', id:'{alistNodeId}' }}) RETURN n")
    for node in results:
        if node[0]:
            alist = node[0]._properties
            alist.pop('sessionId', None)
            alist.pop('parentId', None)
    return alist


def _search_cache(tx, alist_to_instantiate: Alist, attribute_to_instantiate, search_attributes) -> (bool, list):
    alists = []
    conditions = ""
    resultStatus = False
    if not attribute_to_instantiate:
        return (resultStatus, [alist_to_instantiate])
    conditions = " AND ".join(
        [f"n.{x}='{alist_to_instantiate.instantiation_value(x)}'" for x in search_attributes])
    results = tx.run("MATCH (n:Alist)"
                     f"WHERE {conditions}"
                     "RETURN n")
    for node in results:
        if node[0]:
            try:
                alist = Alist(**node[0]._properties)
                if alist.is_instantiated(attribute_to_instantiate):
                    alist.set(attribute_to_instantiate, alist.instantiation_value(
                        attribute_to_instantiate))
                    alist.attributes.pop('sessionId', None)
                    alist.attributes.pop('parentId', None)
                    alist.attributes.pop('src', None)
                    alists.append(alist)
                    resultStatus = True
            except:
                print("Error during alist creation from search result")
    return (resultStatus, alists)


def create_node(alist, parent=None, edge=None, sessionId='0'):
    driver = get_driver()
    with driver.session() as session:
        node_id = session.write_transaction(
            _create_update, alist, parent, edge, sessionId)
        return node_id


def update_node(alist, parent=None, edge=None, sessionId='0'):
    driver = get_driver()
    with driver.session() as session:
        node_id = session.write_transaction(
            _create_update, alist, parent, edge, sessionId)
        return node_id


def get_graph(sessionId='0'):
    driver = get_driver()
    with driver.session() as session:
        node = session.read_transaction(_get_graph, sessionId)
        return node


def get_node(sessionId='0', alistId='0'):
    driver = get_driver()
    with driver.session() as session:
        node = session.read_transaction(_get_node, sessionId, alistId)
        return node


def search_cache(alist_to_instantiate, attribute_to_instantiate, search_attributes=[]):
    ''' Search cache for alist that matches the values of the search attributes

    Args:
      searchAttributes: Attributes whose values will form the conditions of the search.
      attributeToInstantiate: The attribute that will be instantiated.
      alistToInstantiate: The alist to be instantiated.

    Output:
      A tuple of type (Boolean, [Alist]). 
      The boolean value will indicate if the alist was successfully instantiated, 
      and a List containing copies of the alistToInstantiate with unique values 
      for all possible instantiation of the attributeToInstantiate.

    '''
    driver = get_driver()
    with driver.session() as session:
        node = session.read_transaction(
            _search_cache, alist_to_instantiate, attribute_to_instantiate, search_attributes)
        return node


def alist_attr_reformat(attrs):
    a = ""
    for key in attrs:
        # if key == 'fp':
        #   continue
        if attrs[key] is None:
            attrs[key] = ''
        if key[0] in ['?', '#', '$']:
            a += f"`{key}`:"
        # elif key == 'id':
        #   a += f"_{key}:"
        else:
            a += f"{key}:"

        if isinstance(attrs[key], str):
            if '"function"' in attrs[key]:
                a += f"'{attrs[key]}', "
            else:
                a += f'"{attrs[key]}", '
        elif isinstance(attrs[key], dict) or isinstance(attrs[key], list):
            a += f'"{str(attrs[key])}", '
        else:
            a += f"{attrs[key]}, "
    if len(a) > 1:
        a = a[0: -2]

    return a
