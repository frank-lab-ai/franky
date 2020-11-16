from typing import Any
from abc import ABC, abstractmethod


class KB:

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def get_entities(self):
        raise NotImplementedError

    @abstractmethod
    def get_relationships(self):
        raise NotImplementedError
