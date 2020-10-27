'''
File: comparison.py
Description: Comparison decomposition of Alist
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)

'''

# import _context
from frank.alist import Alist as A
from frank.alist import Attributes as tt
from frank.alist import VarPrefix as vx
from frank.alist import Branching as br
from frank.alist import States as states
from frank.alist import NodeTypes as nt
from .map import Map
from frank.graph import InferenceGraph


class Comparison(Map):
    def __init__(self):
        pass

    def decompose(self, alist: A, G:InferenceGraph ):

        # check for comparison operations: eq, lt, gt, lte, gte and for multiple variables in operation variable
        if alist.get(tt.OP).lower() in ['eq', 'lt', 'gt', 'lte', 'gte'] \
                and len(alist.get(tt.OPVAR).split(' ')) > 1:
            opvars = alist.get(tt.OPVAR).split(' ')

            op_alist = alist.copy()
            # higher cost makes this decomposition more expensive
            op_alist.cost = alist.cost + 1
            op_alist.branch_type = br.OR
            op_alist.parent_decomposition = 'comparison'
            op_alist.node_type = nt.HNODE
            # op_alist.state = states.EXPLORED
            # alist.link_child(op_alist)
            G.link(alist, op_alist, op_alist.parent_decomposition)

            for p in opvars:
                pval = alist.get(p)
                child = Alist()
                child.set(tt.OP, "value")
                child.set(tt.OPVAR, p)
                child.set(p, pval)
                child.cost = op_alist.cost + 1
                child.node_type = nt.ZNODE
                child.set(tt.CONTEXT, op_alist.get(tt.CONTEXT))
                # op_alist.link_child(child)
                G.link(op_alist, child, op_alist.parent_decomposition)

        else:
            return None

        return op_alist
