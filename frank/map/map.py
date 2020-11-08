'''
File: Map.py
Description: Base class for map operations.

'''
import abc
from abc import ABC, abstractmethod
# from frank.alist import Alist


class Map(ABC):
    def __int__(self):
        super().__init__()

    @abstractmethod
    def decompose(self, alist, G):
        pass
