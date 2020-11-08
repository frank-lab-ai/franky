'''
File: value.py
Description: Value reduce operation that reduces multiple values to a single 
             one in the absence of a specified aggregation operation.


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
    sum = 0.0
    numList = []
    nonNumList = []
    inst_vars = alist.instantiated_attributes().keys()
    for c in children:
        for k, v in c.instantiated_attributes().items():
            if k not in inst_vars and k in alist.attributes and k != tt.OP:
                alist.instantiate_variable(k, v)

        opVarValue = c.get(c.get(tt.OPVAR))
        if utils.is_numeric(opVarValue):
            sum += float(opVarValue)
            numList.append(float(opVarValue))
            if not str(opVarValue).startswith(vx.NESTING):
                nonNumList.append(str(opVarValue))

        else:
            if not c.get(c.get(tt.OPVAR)).startswith(vx.NESTING):
                nonNumList.append(c.get(c.get(tt.OPVAR)))

    if numList or nonNumList:
        if len(numList) >= len(nonNumList):
            alist.instantiate_variable(
                alist.get(tt.OPVAR), sum / len(children))
        else:
            # get modal value
            valueToReturn = max(nonNumList, key=nonNumList.count)
            alist.instantiate_variable(alist.get(tt.OPVAR), valueToReturn)
    else:
        return None

    alist.instantiate_variable(tt.COV, estimate_uncertainty(
        children, len(numList) == len(
            children), alist.get(tt.OP), len(children)
    ))
    return alist
