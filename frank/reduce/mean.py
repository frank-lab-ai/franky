'''
File: mean.py
Description: mean (average) reduce operation


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
    sum = 0.0
    allNumeric = True
    for c in children:
        for k, v in c.instantiated_attributes().items():
            if k in alist.attributes:
                alist.instantiate_variable(k, v)

        opVarValue = c.get(c.get(tt.OPVAR))
        if utils.is_numeric(opVarValue):
            sum += float(opVarValue)
        else:
            allNumeric = False

    alist.instantiate_variable(
        alist.get(tt.OPVAR), sum / len(children))

    alist.instantiate_variable(tt.COV, estimate_uncertainty(
        children, allNumeric, alist.get(tt.OP), len(children)
    ))
    return alist
