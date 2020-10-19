
'''
File: graph.py
Description: InferenceGraph for FRANK
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)
'''

import networkx as nx
import matplotlib.pyplot as plt
from frank.alist import Alist


class InferenceGraph(nx.DiGraph):
    def __init__(self):
        nx.DiGraph.__init__(self)

    def add_alist(self, alist:Alist):
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

    def parent_alists(self, alist_id):
        pred = self.predecessors(alist_id)
        pred_arr = [Alist(**self.nodes[x]) for x in pred]   
        return pred_arr

    def child_alists(self, alist_id):
        succ = self.successors(alist_id)
        succ_arr = [Alist(**self.nodes[x]) for x in succ]   
        return succ_arr

    def parent_ids(self, alist_id):
        pred = self.predecessors(alist_id)
        pred_arr = [x for x in pred]   
        return pred_arr

    def child_ids(self, alist_id):
        succ = self.successors(alist_id)
        succ_arr = [x for x in succ]   
        return succ_arr
    
    def alist(self, alist_id):
        try:
            alist = Alist(**self.nodes[alist_id])
            return alist
        except:
            return None
        
    def link(self, parent:Alist, child:Alist, edge_label=''):
        if parent:
            succ = self.successors(parent.id)
            succ_nodes = [self.nodes[x] for x in succ]
            child.depth = parent.depth + 1
            child.id = f"{parent.depth + 1}{parent.id}{len(succ_nodes) + 1}"
            self.add_alist(child)
            self.add_edge(parent.id, child.id, **{'label': edge_label})
        else:
            self.add_alist(child)

    def leaf_nodes(self):
        return [x for x in self.nodes() if self.out_degree(x) == 0 and self.in_degree(x) > 0]

    def prune(self, alist_id):
        succ = nx.bfs_successors(self, alist_id)    
        for s in succ:
            self.remove_nodes_from(s[1])
        self.remove_node(alist_id)
        
        
    

    
        
        
        
        
    
    