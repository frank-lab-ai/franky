'''
File: propagate.py
Description: Operation to propagate child alists to parents
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


def projections(parent: Alist, alists_to_propagate):
    ''' propagate projection from selected child alist to its parent [in place]'''

    # copy projection vars of min alist to parent
    for c in alists_to_propagate:
        projVars = c.projection_variables()
        if projVars:
            for pvkey, pv in projVars.items():
                parent.instantiate_variable(
                    pvkey, c.instantiation_value(pvkey), insert_missing=True)
