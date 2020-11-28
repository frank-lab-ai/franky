'''
File: min.py
Description: minimum reduce operation


'''

from typing import List
from frank.alist import Alist
from frank.alist import Attributes as tt
from frank.alist import VarPrefix as vx
from frank.alist import Branching as br
from frank.alist import States as states
from frank.alist import NodeTypes as nt
from frank.util import utils
from frank.uncertainty.aggregateUncertainty import estimate_uncertainty
from frank.reduce import propagate
from frank.graph import InferenceGraph


def reduce(alist: Alist, children: List[Alist], G: InferenceGraph):
    data = {x: utils.get_number(x.instantiation_value(
        alist.get(tt.OPVAR)), 999999999999999) for x in children}
    minAlist = min(data, key=data.get)
    minValue = data[minAlist]
    alist.instantiate_variable(alist.get(tt.OPVAR), minValue)

    propagate.projections(alist, (minAlist,))

    alist.instantiate_variable(tt.COV, estimate_uncertainty(
        children, True, alist.get(tt.OP), len(children)
    ))
    return alist
