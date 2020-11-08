'''
File: map_wrapper.py
Description: A wrapper for various decomposition operations.


'''

from frank.map.geospatial import Geospatial
from frank.map.temporal import Temporal
from frank.map.normalize import Normalize
from frank.map.comparison import Comparison
# from frank.map.isa import IsA


def get_mapper_fn(map_name: str):
    ''' Return the map object for the map_name argument.'''
    if map_name == "temporal":
        return Temporal().decompose
    elif map_name == "geospatial":
        return Geospatial().decompose
    elif map_name == "normalize":
        return Normalize().decompose
    elif map_name == "comparison":
        return Comparison().decompose
    # elif map_name == "isa":
    #     return IsA().decompose
