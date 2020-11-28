from typing import Optional, List


class Entity:

    def __init__(self, name: str, description: Optional[str] = None, instance_of: List['Entity'] = []):
        self.name = name
        self.description = description
        self.instance_of = instance_of
