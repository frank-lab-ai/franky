'''
File: mode.py
Description: mode reduce operation
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)

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


def reduce(alist: Alist, children: List[Alist]):
    sum = 0.0
    nonNumList = []
    for c in children:
        for k, v in c.instantiated_attributes().items():
            if k in alist.attributes:
                alist.instantiate_variable(k, v)

        opVarValue = c.get(c.get(tt.OPVAR))

        if not c.get(c.get(tt.OPVAR)).startswith(vx.NESTING):
            nonNumList.append(c.get(c.get(tt.OPVAR)))

    # get modal value
    valueToReturn = max(nonNumList, key=nonNumList.count)
    alist.instantiate_variable(alist.get(tt.OPVAR), valueToReturn)

    # todo: propagate projection variables of modal alist to parent

    alist.instantiate_variable(tt.COV, estimate_uncertainty(
        children, len(nonNumList) > 0, 'value', len(children)
    ))
    return alist
