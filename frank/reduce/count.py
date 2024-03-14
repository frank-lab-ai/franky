'''
File: count.py
Description: Count reduce operation


'''

from typing import List

from frank.alist import Alist
from frank.alist import Attributes as tt
from frank.alist import Branching as br
from frank.alist import NodeTypes as nt
from frank.alist import States as states
from frank.alist import VarPrefix as vx
from frank.graph import InferenceGraph
from frank.uncertainty.aggregateUncertainty import estimate_uncertainty
from frank.util import utils


def reduce(alist: Alist, children: List[Alist], G: InferenceGraph):
    variables = alist.variables()
    data = [x.instantiation_value(alist.get(tt.OPVAR)) for x in children
            if (x not in list(variables.keys()) and x not in list(variables.values()))]
    alist.instantiate_variable(alist.get(tt.OPVAR), len(data))

    alist.instantiate_variable(tt.COV, estimate_uncertainty(
        children, False, alist.get(tt.OP), len(children)
    ))
    return alist
