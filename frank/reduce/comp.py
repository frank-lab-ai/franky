'''
File: comp.py
Description: Set comprehension reduce operation
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
from frank.graph import InferenceGraph


def reduce(alist: Alist, children: List[Alist], G:InferenceGraph):
    if not children:
        return None

    nodes_enqueue = []
    nodes_enqueue_process = []

    # get intersection of child values
    common_items = set()
    head, *tail = children
    has_head_children = False
    has_tail_children = False
    for c in head.children:
        has_head_children = True
        if c.get(tt.OP) != 'comp':
            if c.get(tt.OPVAR).startswith(vx.NESTING):
                common_items.add(str(c.instantiation_value(c.get(tt.OPVAR))))
            else:
                projVars = c.projection_variables()
                if projVars != None:
                    for pvkey, pvval in projVars.items():
                        common_items.add(c.instantiation_value(pvkey))

    for t in tail:
        c_items = set()
        for tc in t.children:
            has_tail_children = True
            if tc.get(tt.OPVAR).startswith(vx.NESTING):
                c_items.add(str(c.instantiation_value(tc.get(tt.OPVAR))))
            projVars = tc.projection_variables()
            if projVars != None:
                for pvkey, pvval in projVars.items():
                    c_items.add(tc.instantiation_value(pvkey))
        common_items = common_items.intersection(c_items)

    if not common_items and not has_head_children and not has_tail_children:
        for c in children:
            if c.get(tt.OP) != 'comp':
                if c.get(tt.OPVAR).startswith(vx.NESTING):
                    common_items.add(
                        str(c.instantiation_value(c.get(tt.OPVAR))))
                else:
                    projVars = c.projection_variables()
                    if projVars != None:
                        for pvkey, pvval in projVars.items():
                            common_items.add(c.instantiation_value(pvkey))

    if not common_items:
        return None
    else:
        # if common items not empty, ignore existing siblings before creating new siblings
        sibs = G.child_alists(G.parent_alists(alist.id)[0])
        for x in sibs:
            if x.id != alist.id:
                x.prune()
                print('sibling pruned:>>{} {}'.format(x.id, x))

    # setup new sibling branch(s)
    parent = G.parent_alists(alist.id)[0]
    op_alist = parent.copy()
    op_alist.set(alist.get(tt.OPVAR), '')

    op_alist.set(tt.OP, parent.get(tt.OP))
    op_alist.set(tt.OPVAR, parent.get(tt.OPVAR))
    op_alist.set(op_alist.get(tt.OPVAR), '')
    op_alist.state = states.EXPLORED
    # set as an aggregation node to help with display rendering
    op_alist.node_type = nt.HNODE
    # alist.parent[0].link_child(op_alist)
    G.link(parent, op_alist, 'comp')
    nodes_enqueue.append((op_alist, parent, False, 'comp'))
    print('sibling-branch:>>{} {}'.format(op_alist.id, op_alist))
    if alist.children:
        nodes_enqueue.append((op_alist, alist, False, 'set_comp'))

    # create children of the new branch
    # copy to avoid using different version from another thread in loop
    op_alist_copy = op_alist.copy()
    for ff in common_items:
        new_sibling: Alist = op_alist_copy.copy()
        new_sibling.set(tt.OP, 'value')
        new_sibling.set(tt.OPVAR, op_alist_copy.get(tt.OPVAR))
        new_sibling.set(alist.get(tt.OPVAR), ff)
        new_sibling.instantiate_variable(alist.get(tt.OPVAR), ff)
        for ref in new_sibling.variable_references(alist.get(tt.OPVAR)):
            if ref not in [tt.OPVAR]:
                new_sibling.set(ref, ff)
        # op_alist.link_child(new_sibling)
        new_sibling.node_type = nt.ZNODE
        G.link(op_alist, new_sibling, 'comp')
        nodes_enqueue_process.append(
            (new_sibling, op_alist, True, 'comp_lookup'))
        print('sibling-child:>>{} {}'.format(new_sibling.id, new_sibling))

    alist.state = states.IGNORE
    alist.nodes_to_enqueue_only = nodes_enqueue
    alist.nodes_to_enqueue_and_process = nodes_enqueue_process
    return alist
