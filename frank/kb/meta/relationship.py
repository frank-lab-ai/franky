from typing import Optional, List, Type, Any

from .entity import Entity


class Relationship:

    _inverse_inverse: Optional['Relationship']

    def __init__(self, name: str,
                 description: Optional[str] = None,
                 domain: Optional[List[Type[Entity]]] = None,
                 value_range: Optional[Any] = None,  # TODO: Typings
                 inverse: Optional['Relationship'] = None,
                 related: Optional[List['Relationship']] = [],
                 deprecated_by: Optional['Relationship'] = None):
        self.name = name
        self.description = description
        self.domain = domain
        self.value_range = value_range
        self.inverse = inverse
        self.related = related
        self.deprecated_by = deprecated_by
