from typing import List, Any, Tuple, Optional
from pyld import jsonld
from bs4 import BeautifulSoup
import json
import logging
from itertools import chain

from frank.config import config
from frank.util.utils import listify, filter_out_falsy
from frank.alist import Alist
from frank.alist import Attributes as tt
from frank.kb import KB
from frank.kb.meta import Entity, Relationship
from frank.kb.extensions.schemaorg import get_schema as get_schemaorg_schema
from frank.kb.utils.requests import requests
from frank.kb.utils.link_crawler import crawl_graph, crawl_soup


# jsonld.set_document_loader(jsonld.requests_document_loader(headers={
#     'Accept': 'application/ld+json, application/json',
#     'User-Agent': config['user-agent']
# }))


class JSONLD(KB):

    DEFAULT_CONTEXT = 'https://schema.org/docs/jsonldcontext.jsonld'
    PROTECTED_PROPERTY_NAMES = ['id', 'value']
    GRAPH_SCHEMA_ID_PREFIX = 'schema:'

    context: Any
    graph: List[Any]
    introspection_graph: List[Any]
    url: Optional[str]
    soup: Optional[BeautifulSoup]

    def __init__(self, name: str, document: Any, url: Optional[str] = None, soup: Optional[BeautifulSoup] = None):
        if '@context' not in document or 'schema.org' in document['@context']:
            # schema.org, as it is commonly used, has a bug.
            # Very often 'http://schema.org' is used as the '@context' value, but the website does not ever return a valid JSON-LD schema.
            # It appears it used to, with the help of content-negotiation: https://webmasters.stackexchange.com/questions/123409
            # But this has stopped working. So we hard code in this default context to fix.
            document['@context'] = JSONLD.DEFAULT_CONTEXT
        else:
            # TODO: Support other schemas
            logging.warning(
                f"You're using a schema which is not schema.org ({document['@context']}). Support is limited at the moment (particularly for introspection).")

        super().__init__(name)
        self.context = document['@context']
        self.graph = jsonld.flatten(document, self.context)['@graph']
        self._introspect()

        if url:
            self.url = url
        if soup:
            self.soup = soup

    @classmethod
    def from_url(cls, name: str, url: str):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # TODO: Support many
        element = soup.find('script', type='application/ld+json')
        if element:
            document = json.loads(element.string)
            return JSONLD(name, document, url, soup)

    def _introspect(self):
        schema = None
        if self.context == JSONLD.DEFAULT_CONTEXT:
            schema = get_schemaorg_schema()
        else:
            # TODO: Support other schemas
            schema = None

        if schema:
            self.introspection_graph = jsonld.flatten(schema, self.context)[
                '@graph']

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

    def crawl(self, same_site_depth=1, external_domain_depth=1, jsonld_links_only=True):
        if not self.url or not self.soup:
            logging.warning(
                f"{self.name} JSON-LD knowledge base was not initialized with a webpage, and so cannot be crawled.")
            return []

        links = []
        if jsonld_links_only:
            links = crawl_graph(
                self.graph, self.url, self.context, same_site_depth > 0, external_domain_depth > 0)
        else:
            links = crawl_soup(self.soup, self.url, self.context,
                               same_site_depth > 0, external_domain_depth > 0)

        kbs = filter_out_falsy([JSONLD.from_url(link, link) for link in links])
        child_kbs = []

        for kb in kbs:
            child_kbs.extend(kb.crawl(same_site_depth - 1,
                                      external_domain_depth - 1, jsonld_links_only))

        kbs = kbs + child_kbs

        return filter_out_falsy(kbs)

    @classmethod
    def generate_graph_schema_id(cls, id_name: str):
        return f'{JSONLD.GRAPH_SCHEMA_ID_PREFIX}{id_name}'

    @classmethod
    def extract_from_graph_schema_id(cls, id_name: str):
        return id_name.split(JSONLD.GRAPH_SCHEMA_ID_PREFIX)[1]

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

    def _get_introspection_entity(self, id_name: str):
        introspection_entity = next(
            (introspection_entity for introspection_entity in self.introspection_graph if introspection_entity['id'] == id_name), None)
        if introspection_entity:
            entity = Entity(JSONLD.extract_from_graph_schema_id(id_name),
                            introspection_entity.get('rdfs:comment'))

            entity_types = listify(introspection_entity.get('type'))
            entity.instance_of = []
            for entity_type in entity_types:
                instance_of = self._get_introspection_entity(
                    JSONLD.generate_graph_schema_id(entity_type))
                if instance_of:
                    entity.instance_of.append(instance_of)

            return entity

    @KB.memoize()
    def get_entities(self) -> List[Entity]:
        entity_names = set(
            chain(*(listify(entity.get('type')) for entity in self.graph)))
        entities = [Entity(entity_name) for entity_name in entity_names]

        if self.introspection_graph:
            entities = [self._get_introspection_entity(
                JSONLD.generate_graph_schema_id(entity_name)) for entity_name in entity_names]

        return filter_out_falsy(entities)

    def _get_introspection_relationship(self, id_name: str, inverse: Optional[Relationship] = None):
        introspection_relationship = next(
            (introspection_relationship for introspection_relationship in self.introspection_graph if introspection_relationship['id'] == id_name), None)
        if introspection_relationship:
            relationship = Relationship(JSONLD.extract_from_graph_schema_id(id_name),
                                        introspection_relationship.get('rdfs:comment'))

            domainIncludes = listify(
                introspection_relationship.get('domainIncludes'))
            relationship.domain = filter_out_falsy([self._get_introspection_entity(
                domainInclude['id']) for domainInclude in domainIncludes])

            rangeIncludes = listify(
                introspection_relationship.get('rangeIncludes'))
            relationship.value_range = filter_out_falsy([self._get_introspection_entity(
                rangeInclude['id']) for rangeInclude in rangeIncludes])

            if inverse:
                relationship.inverse = inverse
            elif 'inverseOf' in introspection_relationship:
                relationship.inverse = self._get_introspection_relationship(
                    introspection_relationship.get('inverseOf')['id'], relationship)

            relationship.related = None  # TODO

            if 'supersededBy' in introspection_relationship:
                relationship.deprecated_by = self._get_introspection_relationship(
                    introspection_relationship.get('supersededBy')['id'])

            return relationship

    @KB.memoize()
    def get_relationships(self) -> List[Relationship]:
        relationship_names = set(
            chain(*[entity.keys() for entity in self.graph]))
        relationships = [Relationship(relationship_name)
                         for relationship_name in relationship_names]

        if self.introspection_graph:
            relationships = []
            for relationship_name in relationship_names:
                relationship = self._get_introspection_relationship(
                    JSONLD.generate_graph_schema_id(relationship_name))
                if relationship:
                    relationships.append(relationship)

        return filter_out_falsy(relationships)
