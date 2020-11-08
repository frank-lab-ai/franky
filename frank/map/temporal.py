'''
File: temporal.py
Description: Temporal decomposition of Alist


'''

# import _context
import datetime
import math
import frank.config as config
from frank.alist import Alist as A
from frank.alist import Attributes as tt
from frank.alist import VarPrefix as vx
from frank.alist import Branching as br
from frank.alist import States as states
from frank.alist import Contexts as ctx
from frank.alist import NodeTypes as nt
from .map import Map
import frank.context
from frank.graph import InferenceGraph


class Temporal(Map):

    def decompose(self, alist:A, G:InferenceGraph):
        current_year = datetime.datetime.now().year
        branch_factor = config.config["temporal_branching_factor"]
        parent_year = None
        if alist.get(tt.TIME).startswith(vx.NESTING) or \
                not alist.get(tt.TIME):
            return None
        else:

            parent_year = datetime.datetime.strptime(alist.get(tt.TIME), '%Y')

        count = 0
        op_alist = alist.copy()
        op = "regress"
        context = op_alist.get(tt.CONTEXT)
        if context:
            if context[0]:
                if ctx.accuracy in context[0] and context[0][ctx.accuracy] == 'high':
                    op = 'gpregress'
                    if branch_factor <= 10: 
                        # increase number of data points for regression
                        branch_factor = 20
        
            if context[1] and ctx.datetime in context[1]:
                # use the ctx.datetime as current year if specified in context
                current_year = datetime.datetime.strptime(context[1][ctx.datetime], '%Y-%m-%d %H:%M:%S').year

        # flush context: needed to clear any query time context value 
        #   whose corresponding alist attribute (t) has been modified
        frank.context.flush(op_alist, [tt.TIME])
        
        op_alist.set(tt.OP, op)
        op_alist.cost = alist.cost + 2.0
        op_alist.branch_type = br.AND
        op_alist.state = states.EXPLORED
        op_alist.parent_decomposition = 'temporal'
        op_alist.node_type = nt.HNODE
        # alist.link_child(op_alist)
        G.link(alist, op_alist, op_alist.parent_decomposition)
        if (current_year - parent_year.year) > branch_factor/2:
            for i in range(1, math.ceil(branch_factor/2)):
                child_a = alist.copy()
                child_a.set(tt.TIME, str(parent_year.year + i))
                child_a.set(tt.OP, "value")
                child_a.cost = op_alist.cost + 1
                child_a.node_type = nt.ZNODE
                child_a.set(tt.CONTEXT, op_alist.get(tt.CONTEXT))
                frank.context.flush(child_a, [tt.TIME])
                # op_alist.link_child(child_a)
                G.link(op_alist, child_a, 'value')

                child_b = alist.copy()
                child_b.set(tt.TIME, str(parent_year.year - i))
                child_b.set(tt.OP, "value")
                child_b.cost = op_alist.cost + 1
                child_b.set(tt.CONTEXT, op_alist.get(tt.CONTEXT))
                frank.context.flush(child_b, [tt.TIME])
                child_b.node_type = nt.ZNODE
                # op_alist.link_child(child_b)
                G.link(op_alist, child_b, 'value')
                count = count + 2
        elif parent_year.year >= current_year:
            for i in range(1, math.ceil(branch_factor)):
                child_a = alist.copy()
                child_a.set(tt.TIME, str(current_year - i))
                child_a.set(tt.OP, "value")
                child_a.cost = op_alist.cost + 1
                child_a.node_type = nt.ZNODE
                child_a.set(tt.CONTEXT, op_alist.get(tt.CONTEXT))
                frank.context.flush(child_a, [tt.TIME])
                # op_alist.link_child(child_a)
                G.link(op_alist, child_a, 'value')
                count = count + 1

        for i in range(1, (branch_factor - count)):
            child_a = alist.copy()
            child_a.set(tt.TIME, str(parent_year.year - (count + i)))
            child_a.set(tt.OP, "value")
            child_a.cost = op_alist.cost + 1
            child_a.node_type = nt.ZNODE
            child_a.set(tt.CONTEXT, op_alist.get(tt.CONTEXT))
            frank.context.flush(child_a, [tt.TIME])
            # op_alist.link_child(child_a)
            G.link(op_alist, child_a, 'value')

        return op_alist
