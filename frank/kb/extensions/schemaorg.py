import re

from frank.kb.utils import requests

SCHEMAORG_HTTP_SCHEMA_URL = 'https://schema.org/version/latest/schemaorg-all-http.jsonld'
SCHEMAORG_HTTPS_SCHEMA_URL = 'https://schema.org/version/latest/schemaorg-all-http.jsonld'


def get_schema():
    return requests.get(SCHEMAORG_HTTP_SCHEMA_URL).json()
