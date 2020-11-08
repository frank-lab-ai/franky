'''
File: gte.py
Description: greater-than-or-equal-to reduce operation


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
    # do comparisons
    vars_to_compare = alist.get(tt.OPVAR).split(' ')

    # propagate projection vars to parent
    propagate.projections(alist, tuple(children))
    response_var = "?_gte_"
    if len(vars_to_compare) == 0:
        alist.set(response_var, "false")
        return alist

    result = True
    if len(vars_to_compare) > 1 and utils.is_numeric(alist.instantiation_value(vars_to_compare[0])):
        for x in vars_to_compare[1:]:
            if utils.is_numeric(alist.instantiation_value(x)):
                result = (utils.get_number(alist.instantiation_value(
                    vars_to_compare[0]), 0) >= utils.get_number(alist.instantiation_value(x), 0)) and result
            else:
                result = False
                break
    else:
        result = False
    alist.set(response_var, str(result).lower())

    # alist.instantiate_variable(tt.COV, estimate_uncertainty(
    #   children, True, alist.get(tt.OP), len(children)
    # ))
    return alist
# alist.instantiation_value(x) == alist.instantiation_value(vars_to_compare[0]))
