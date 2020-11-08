'''
File: eq.py
Description: Equality reduce operation


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
    print(children)
    vars_to_compare = alist.get(tt.OPVAR).split(' ')

    # # copy projection vars of min alist to parent
    # for c in children:
    #   if c.get(tt.OP) != 'comp':
    #     for vc in vars_to_compare:
    #       if vc in c.attributes:
    #         projVars = c.projection_variables()
    #         alist.instantiate_variable(vc, c.instantiation_value(vc), insert_missing=True)

    # for x in vars_to_compare:
    #   if alist.is_instantiated(x) == False:
    #     # return None
    #     pass

    # propagate projection vars to parent
    propagate.projections(alist, tuple(children))
    response_var = "?_eq_"
    if len(vars_to_compare) == 0:
        alist.set(response_var, "false")
        return alist

    result = True
    for x in vars_to_compare:
        result = (alist.instantiation_value(x) ==
                  alist.instantiation_value(vars_to_compare[0])) and result

    alist.instantiate_variable(response_var, str(
        result).lower(), insert_missing=True)

    # alist.instantiate_variable(tt.COV, estimate_uncertainty(
    #   children, True, alist.get(tt.OP), len(children)
    # ))
    return alist
# alist.instantiation_value(x) == alist.instantiation_value(vars_to_compare[0]))
