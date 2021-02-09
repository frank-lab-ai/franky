from typing import List, Any
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
from frank.util.utils import listify
from itertools import chain


def standardize_url(url: str, fallback_url: str):
    parsed_url = urlparse(url)
    fallback_parsed_url = urlparse(fallback_url)
    return urlunparse(('https' if parsed_url.scheme == 'http' else (parsed_url.scheme or fallback_parsed_url.scheme), (parsed_url.netloc or fallback_parsed_url.netloc), parsed_url.path or '/', parsed_url.params, parsed_url.query, None))


def collapse_value(value: Any):
    if isinstance(value, list):
        return chain(*[collapse_value(item) for item in value])
    elif isinstance(value, dict):
        return chain(*[collapse_value(item) for item in value.values()])

    return listify(value)


def crawl_graph(graph: List[dict], url: str, schema_url: str, same_site: bool, external_domain: bool):
    links = set()

    schema_domain = urlparse(schema_url).netloc
    domain = urlparse(url).netloc
    standardized_url = standardize_url(url, url)

    for value in collapse_value(graph):
        value = str(value)
        parsed_url = urlparse(value)
        if standardize_url(value, url) == standardized_url:
            continue

        if parsed_url.netloc:
            if parsed_url.netloc == schema_domain:
                continue

            value_url = urlunparse((parsed_url.scheme, parsed_url.netloc,
                                    parsed_url.path, parsed_url.params, parsed_url.query, None))

            if same_site and parsed_url.netloc == domain:
                links.add(value_url)
            elif external_domain and parsed_url.netloc != domain:
                links.add(value_url)

    return list(links)


def crawl_soup(soup: BeautifulSoup, url: str, schema_url: str, same_site: bool, external_domain: bool):
    links = set()

    schema_domain = urlparse(schema_url).netloc
    domain = urlparse(url).netloc
    standardized_url = standardize_url(url, url)

    for tag in soup.find_all(lambda tag: tag.name == 'a' and tag.has_attr('href')):
        value = tag.get('href')
        parsed_url = urlparse(value)
        if standardize_url(value, url) == standardized_url:
            continue

        if parsed_url.netloc:
            if parsed_url.netloc == schema_domain:
                continue

            value_url = urlunparse((parsed_url.scheme, parsed_url.netloc,
                                    parsed_url.path, parsed_url.params, parsed_url.query, None))

            if same_site and parsed_url.netloc == domain:
                links.add(value_url)
            elif external_domain and parsed_url.netloc != domain:
                links.add(value_url)

    return list(links)
