'''
File: comparison.py
Description: Comparison decomposition of Alist
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)
Copyright 2014 - 2020  Kobby K.A. Nuamah
'''

# import _context
from frank.alist import Alist as A
from frank.alist import Attributes as tt
from frank.alist import VarPrefix as vx
from frank.alist import Branching as br
from frank.alist import States as states
from .map import Map


class Comparison(Map):
    def __init__(self):
        pass

    def decompose(self, alist: A):

        # check for comparison operations: eq, lt, gt, lte, gte and for multiple variables in operation variable
        if alist.get(tt.OP).lower() in ['eq', 'lt', 'gt', 'lte', 'gte'] \
                and len(alist.get(tt.OPVAR).split(' ')) > 1:
            opvars = alist.get(tt.OPVAR).split(' ')

            op_alist = alist.copy()
            # higher cost makes this decomposition more expensive
            op_alist.cost = alist.cost + 1
            op_alist.branch_type = br.OR
            op_alist.parent_decomposition = 'compare'
            # op_alist.state = states.EXPLORED
            alist.link_child(op_alist)

            for p in opvars:
                pval = alist.get(p)
                child = Alist()
                child.set(tt.OP, "value")
                child.set(tt.OPVAR, p)
                child.set(p, pval)
                child.cost = op_alist.cost + 1
                op_alist.link_child(child)

        else:
            return None

        return op_alist
