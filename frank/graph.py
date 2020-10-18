
'''
File: graph.py
Description: InferenceGraph for FRANK
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)
'''

import networkx as nx
import matplotlib.pyplot as plt
from frank.alist_basic import AlistB


class InferenceGraph(nx.DiGraph):
    def __init__(self):
        nx.DiGraph.__init__(self)

    def add_alist(self, alist:AlistB):
        self.add_nodes_from([(alist.id, alist.attributes)])
    
    def add_alists_from(self, alists:list):
        node_list = [(a.id, a.attributes) for a in alists]
        self.add_nodes_from(node_list)
    
    def display(self):
        # plt.plot()        
        pos = nx.spring_layout(self)
        nx.draw(self, pos=pos, with_labels=True, **{'node_size':500, 'node_color': 'red', 'width':1, 'font_size': 8 })
        edge_labels = nx.get_edge_attributes(self, 'label')
        formatted_edge_labels = {(elem[0],elem[1]):edge_labels[elem] for elem in edge_labels}
        nx.draw_networkx_edge_labels(self, pos=pos, edge_labels=edge_labels)
        # plt.show(block=False)

    def parent(self, alist_id):
        pred = self.predecessors(alist_id)
        p_arr = [self.nodes[p] for p in pred]   
        return AlistB(**p_arr[0]) if len(p_arr) > 0 else None
    
    def get_alist(self, alist_id):
        try:
            alist = AlistB(**self.nodes[alist_id])
            return alist
        except:
            return None
        
    def link(self, parent:AlistB, child:AlistB, edge_label=''):
        succ = self.successors(parent.id)
        succ_nodes = [self.nodes[x] for x in succ]
        child.depth = parent.depth + 1
        child.id = f"{parent.depth + 1}{parent.id}{len(succ_nodes) + 1}"
        self.add_alist(child)
        self.add_edge(parent.id, child.id, **{'label': edge_label})

    def leaf_nodes(self):
        return [x for x in self.nodes() if self.out_degree(x) == 0 and self.in_degree(x) > 0]

    def prune(self, alist_id):
        # pred = self.predecessors(alist_id) 
        # pred_edges = [(parent_id, alist_id) for parent_id in pred]
        # succ = self.successors(alist_id)
        # succ_edges = [(alist_id, child_id) for child_id in succ]
        # # for p,c in succ_edges:
        # #     self.
        # self.remove_node(alist_id)
        succ = nx.bfs_successors(self, alist_id)    
        for s in succ:
            self.remove_nodes_from(s[1])
        self.remove_node(alist_id)
        
        
    

    
        
        
        
        
    
    