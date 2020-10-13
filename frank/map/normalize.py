'''
File: normalize.py
Description: Normalization decomposition of A
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)
Copyright 2014 - 2020  Kobby K.A. Nuamah
'''

# import _context
from frank.alist import Alist as A
from frank.alist import Attributes as tt
from frank.alist import VarPrefix as vx
from frank.alist import Branching as br
from frank.alist import States as states
from frank.kb import rdf
from .map import Map


class Normalize(Map):
    def __init__(self):
        pass

    def decompose(self, alist: A):
        nest_vars = alist.uninstantiated_nesting_variables()
        for nest_attr, v in nest_vars.items():
            if NormalizeFn.FILTER in v:
                op_alist = alist.copy()
                op_alist.set(tt.OPVAR, nest_attr)
                op_alist.set(tt.OP, 'comp')
                del op_alist.attributes[nest_attr]
                op_alist.cost = alist.cost + 1
                op_alist.branch_type = br.AND
                op_alist.state = states.EXPLORED
                op_alist.parent_decomposition = 'normalize'
                alist.link_child(op_alist)

                # check for filters that heuristics apply to
                # e.g type==country and location==Europs
                filter_patterns = {}
                geo_class = ''
                for x in v[NormalizeFn.FILTER]:
                    prop = str(x['p'])
                    obj = str(x['o'])
                    if prop == 'type' and (obj == 'country' or obj == 'continent'):
                        filter_patterns['geopolitical'] = obj
                    elif prop == 'location':
                        filter_patterns['location'] = obj

                if {'geopolitical', 'location'} <= set(filter_patterns):
                    # use heuristics to create a single alist containing the
                    # conjunction to find the X located in Y
                    child = A(**{})
                    child.set(tt.OP, 'values')
                    child.set(tt.OPVAR, nest_attr)
                    child.set(tt.SUBJECT, nest_attr)
                    child.set(tt.PROPERTY, '__geopolitical:' +
                              filter_patterns['geopolitical'])
                    child.set(tt.OBJECT, filter_patterns['location'])
                    child.cost = op_alist.cost + 1
                    child.state = states.UNEXPLORED
                    op_alist.link_child(child)
                    return op_alist
                else:
                    for x in v[NormalizeFn.FILTER]:
                        child = A(**{})
                        child.set(tt.OP, 'values')
                        child.set(tt.OPVAR, nest_attr)
                        child.set(tt.SUBJECT, nest_attr)
                        for attr, attrval in x.items():
                            child.set(attr, attrval)
                        child.cost = op_alist.cost + 1
                        child.state = states.UNEXPLORED
                        op_alist.link_child(child)
                    return op_alist

            elif NormalizeFn.IN in v:
                op_alist = alist.copy()
                op_alist.set(tt.OPVAR, nest_attr)
                op_alist.set(tt.OP, 'comp')
                del op_alist.attributes[nest_attr]
                op_alist.cost = alist.cost + 1
                op_alist.state = states.EXPLORED
                op_alist.parent_decomposition = 'normalize'
                alist.link_child(op_alist)

                listed_items = []
                if isinstance(v[NormalizeFn.IN], list):
                    for x in v[NormalizeFn.IN]:
                        listed_items.append(str(x))
                elif isinstance(v[NormalizeFn.IN], str):
                    for x in str(v[NormalizeFn.IN]).split(';'):
                        listed_items.append(str(x).strip())
                for x in listed_items:
                    child = A(**{})
                    child.set(tt.OP, 'value')
                    if nest_attr[0] in [vx.AUXILLIARY, vx.PROJECTION, vx.NESTING]:
                        child.set(tt.OPVAR, nest_attr)
                        child.set(nest_attr, x)
                    else:
                        new_var = vx.PROJECTION + '_x' + \
                            str(len(op_alist.attributes))
                        child.set(tt.OPVAR, new_var)
                        child.set(nest_attr, new_var)
                        child.set(new_var, x)
                    child.state = states.UNEXPLORED
                    child.cost = op_alist.cost + 1
                    op_alist.link_child(child)
                return op_alist

            elif NormalizeFn.IS in v:
                op_alist = alist.copy()
                op_alist.set(tt.OPVAR, nest_attr)
                op_alist.set(tt.OP, 'comp')
                del op_alist.attributes[nest_attr]
                op_alist.cost = alist.cost + 1
                op_alist.state = states.EXPLORED
                op_alist.parent_decomposition = 'normalize'
                alist.link_child(op_alist)

                child = A(**{})
                child.set(tt.OP, 'value')
                new_var = vx.PROJECTION + '_x' + str(len(op_alist.attributes))
                child.set(tt.OPVAR, new_var)
                child.set(new_var, v[NormalizeFn.IS])
                child.state = states.REDUCIBLE
                child.cost = op_alist.cost + 1
                op_alist.link_child(child)

                if v[NormalizeFn.IS].startswith((vx.AUXILLIARY, vx.NESTING, vx.PROJECTION)) == False:
                    # this is an instantiation, so a pseudo leaf node should be created
                    leaf = A(**{})
                    leaf.set(tt.OP, 'value')
                    new_var = vx.PROJECTION + '_x' + \
                        str(len(op_alist.attributes))
                    leaf.set(tt.OPVAR, new_var)
                    leaf.set(new_var, v[NormalizeFn.IS])
                    leaf.state = states.REDUCIBLE
                    leaf.cost = op_alist.cost + 1
                    child.link_child(leaf)

                return op_alist

            elif tt.OP in v:
                op_alist = alist.copy()
                op_alist.set(tt.OPVAR, nest_attr)
                op_alist.set(tt.OP, 'comp')
                # del op_alist.attributes[nest_attr]
                op_alist.set(nest_attr, '')
                op_alist.cost = alist.cost + 1
                op_alist.parent_decomposition = 'normalize'
                alist.link_child(op_alist)

                var_ctr = 200
                child = A(**{})
                for ak, av in v.items():
                    if isinstance(av, str):
                        child.set(ak, av.strip())
                    elif ak == tt.CONTEXT:
                        child.set(ak, av)
                    else:
                        new_var = vx.NESTING + str(var_ctr)
                        child.set(ak, new_var)
                        child.set(new_var, av)
                        var_ctr = var_ctr + 1
                child.cost = op_alist.cost + 1
                op_alist.link_child(child)
                return op_alist
        return None


class NormalizeFn:
    IN = '$in'
    IS = '$is'
    FILTER = '$filter'
