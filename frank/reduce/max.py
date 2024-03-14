'''
File: max.py
Description: max reduce operation


'''

from typing import List

from frank.alist import Alist
from frank.alist import Attributes as tt
from frank.alist import Branching as br
from frank.alist import NodeTypes as nt
from frank.alist import States as states
from frank.alist import VarPrefix as vx
from frank.graph import InferenceGraph
from frank.reduce import propagate
from frank.uncertainty.aggregateUncertainty import estimate_uncertainty
from frank.util import utils


def reduce(alist: Alist, children: List[Alist], G: InferenceGraph):

    data = {x: utils.get_number(x.instantiation_value(
        alist.get(tt.OPVAR)), -999999999999999) for x in children}
    maxAlist = max(data, key=data.get)
    maxValue = data[maxAlist]
    alist.instantiate_variable(alist.get(tt.OPVAR), maxValue)

    propagate.projections(alist, (maxAlist,))
    alist.instantiate_variable(tt.COV, estimate_uncertainty(
        children, True, alist.get(tt.OP), len(children)
    ))
    return alist
