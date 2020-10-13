'''
File: mean.py
Description: mean (average) reduce operation
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)
Copyright 2014 - 2020  Kobby K.A. Nuamah
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
