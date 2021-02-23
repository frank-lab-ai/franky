'''
File: value.py
Description: Value reduce operation that reduces multiple values to a single 
             one in the absence of a specified aggregation operation.


'''

from typing import List
from collections import Counter
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
    delimiter = ';;'
    total = 0.0
    numList = []
    nonNumList = []
    inst_vars = alist.instantiated_attributes().keys()
    for c in children:
        for k, v in c.instantiated_attributes().items():
            if k not in inst_vars and k in alist.attributes and k != tt.OP:
                c.instantiate_variable(k, v)

        opVarValue = c.get(c.get(tt.OPVAR))
        if isinstance(opVarValue, str):
            opVarValue = list(map(str, opVarValue.split(delimiter)))
        else:
            opVarValue = [opVarValue]
        for opval in opVarValue:
            if utils.is_numeric(opval):
                total += float(opval)
                numList.append(float(opval))
                if not str(opval).startswith(vx.NESTING):
                    nonNumList.append(str(opval))

            else:
                # if not c.get(c.get(tt.OPVAR)).startswith(vx.NESTING):
                #     nonNumList.append(c.get(c.get(tt.OPVAR)))
                 nonNumList.append(opval)

    if numList or nonNumList:
        if len(numList) >= len(nonNumList):
            opVar = alist.get(tt.OPVAR)
            valueToReturn = total / len(children)
            if opVar == alist.get(tt.TIME):
                valueToReturn = str(int(valueToReturn))
            alist.instantiate_variable(opVar, valueToReturn)
        else:
            # # get modal value
            # valueToReturn = max(nonNumList, key=nonNumList.count)
            counts = dict(Counter(nonNumList))
            counts_set = set(counts.values())
            max_val = max(counts_set)
            items = [x for x,y in counts.items() if y == max_val]
            valueToReturn = f'{delimiter} '.join(map(str,set(items)))
            

            # if len(nonNumList) == 1:
            #     valueToReturn = nonNumList[0]
            # else:
            #     # return list of different values
            #     valueToReturn = ', '.join(map(str,set(nonNumList)))

            alist.instantiate_variable(alist.get(tt.OPVAR), valueToReturn)
    else:
        return None

    alist.instantiate_variable(tt.COV, estimate_uncertainty(
        children, len(numList) == len(
            children), alist.get(tt.OP), len(children)
    ))
    return alist
