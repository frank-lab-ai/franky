'''
File: product.py
Description: Multiplication reduce operation
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)

'''
from functools import reduce as ft_reduce
import operator
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
    data = [utils.get_number(x.instantiation_value(
        alist.get(tt.OPVAR)), 1) for x in children]
    alist.instantiate_variable(
        alist.get(tt.OPVAR), ft_reduce(operator.mul, data, 1))

    # TODO: port code for cov calculations
    alist.instantiate_variable(tt.COV, estimate_uncertainty(
        children, True, alist.get(tt.OP), len(children)
    ))
    return alist
