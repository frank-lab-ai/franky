'''
File: Map.py
Description: Base class for map operations.
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)
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
