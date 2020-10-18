
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
        nx.draw(self, with_labels=True, **{'node_size':500, 'node_color': 'red', 'width':1, 'font_size': 8 })
        # plt.show(block=False)

    def parent(self, alist_id):
        pred = self.predecessors(alist_id)
        p_arr = []   
        for p in pred:
            p_arr.append(self.nodes[p])            

        return AlistB(**p_arr[0]) if len(p_arr) > 0 else None
    
    def get_alist(self, alist_id):
        try:
            alist = AlistB(**self.nodes[alist_id])
            return alist
        except:
            return None
        
        
        
        
    
    