from typing import List, Any, Tuple
from pyld import jsonld
import requests
from bs4 import BeautifulSoup
import json
from itertools import chain

from frank.util.utils import listify
from frank.alist import Alist
from frank.alist import Attributes as tt
from . import KB
from .jsonld_schema import JSONLD_SCHEMA
from .meta import Entity, Relationship


class JSONLD(KB):

    DEFAULT_CONTEXT = {
        '@context': 'https://schema.org/docs/jsonldcontext.jsonld'}
    PROTECTED_PROPERTY_NAMES = ['id', 'value']
    GRAPH_SCHEMA_ID_PREFIX = 'schema:'

    context: Any
    graph: List[Any]
    introspection_graph: List[Any]

    def __init__(self, name: str, document: Any):
        if '@context' in document and 'schema.org' in document['@context']:
            # schema.org, as it is commonly used, has a bug.
            # Very often 'http://schema.org' is used as the '@context' value, but the website does not ever return a valid JSON-LD schema.
            # It appears it used to, with the help of content-negotiation: https://webmasters.stackexchange.com/questions/123409
            # But this has stopped working. So we hard code in this default context to fix.
            document['@context'] = JSONLD.DEFAULT_CONTEXT

        super().__init__(name)
        self.context = document['@context']
        self.graph = jsonld.flatten(document, self.context)['@graph']
        self._introspect()

    @classmethod
    def from_url(cls, name: str, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # TODO: Support many
        element = soup.find('script', type='application/ld+json')
        document = json.loads(element.string)
        return JSONLD(name, document)

    def _introspect(self):
        if self.context == JSONLD.DEFAULT_CONTEXT:
            self.introspection_graph = jsonld.flatten(JSONLD_SCHEMA, JSONLD.DEFAULT_CONTEXT)[
                '@graph'][0]['@graph']

    def _get_nodes(self, name: str):
        name = name.lower()
        nodes = []
        for node in self.graph:
            if 'id' in node:
                if node['id'].lower() == name:
                    nodes.append(node)
                    continue
            if 'name' in node:
                if node['name'].lower() == name:
                    nodes.append(node)

        return nodes

    # TODO: Deprecate
    def search_properties(self, prop_string) -> List[Tuple[str, str, float]]:
        relationships = [(prop_string, prop_string, 1)
                         for relationship in self.get_relationships() if relationship.name == prop_string]
        return relationships

    # TODO: Deprecate
    def find_property_values(self, alist: Alist, search_element: str):
        if search_element == tt.OBJECT:
            subject = alist.instantiation_value(tt.SUBJECT)
            nodes = self._get_nodes(subject)
            results = []
            for node in nodes:
                try:
                    data_alist = alist.copy()
                    data_alist.set(tt.OBJECT, node[alist.get(tt.PROPERTY)])
                    data_alist.data_sources = list(
                        set(data_alist.data_sources + [self.name]))
                    results.append(data_alist)
                except:
                    pass
            return results

    def _get_introspection_entity(self, id: str):
        introspection_entity = next(
            (introspection_entity for introspection_entity in self.introspection_graph if introspection_entity['id'] == id), None)
        if introspection_entity:
            entity = Entity(id.split(JSONLD.GRAPH_SCHEMA_ID_PREFIX)[1],
                            introspection_entity['rdfs:comment'])

            entity_types = listify(introspection_entity['type'])
            entity.instance_of = []
            for entity_type in entity_types:
                instance_of = self._get_introspection_entity(
                    f'{JSONLD.GRAPH_SCHEMA_ID_PREFIX}{entity_type}')
                if instance_of:
                    entity.instance_of.append(instance_of)

            return entity

    def get_entities(self) -> List[Entity]:
        entity_names = set(
            chain(*(listify(entity['type'])[0] for entity in self.graph)))
        entities = [Entity(entity_name) for entity_name in entity_names]

        if self.introspection_graph:
            entities = [self._get_introspection_entity(
                f'{JSONLD.GRAPH_SCHEMA_ID_PREFIX}{entity_name}') for entity_name in entity_names]

        return entities

    def _get_introspection_relationship(self, id: str):
        introspection_relationship = next(
            (introspection_relationship for introspection_relationship in self.introspection_graph if introspection_relationship['id'] == id), None)
        if introspection_relationship:
            relationship = Relationship(id.split(JSONLD.GRAPH_SCHEMA_ID_PREFIX)[1],
                                        introspection_relationship['rdfs:comment'])

            domainIncludes = listify(
                introspection_relationship['domainIncludes'])
            relationship.domain = [self._get_introspection_entity(
                domainInclude['id']) for domainInclude in domainIncludes]

            rangeIncludes = listify(
                introspection_relationship['rangeIncludes'])
            relationship.value_range = [self._get_introspection_entity(
                rangeInclude['id']) for rangeInclude in rangeIncludes]

            # TODO: Recursion! Recursion! Recursion!
            # relationship.inverse = self._get_introspection_relationship(
            #     introspection_relationship['inverseOf']['id'])
            relationship.related = None  # TODO
            relationship.deprecated_by = None  # TODO

            return relationship

    def get_relationships(self) -> List[Relationship]:
        relationship_names = set(
            chain(*[entity.keys() for entity in self.graph]))
        relationships = [Relationship(relationship_name)
                         for relationship_name in relationship_names]

        if self.introspection_graph:
            relationships = []
            for relationship_name in relationship_names:
                relationship = self._get_introspection_relationship(
                    f'{JSONLD.GRAPH_SCHEMA_ID_PREFIX}{relationship_name}')
                if relationship:
                    relationships.append(relationship)

        return relationships
