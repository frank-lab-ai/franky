from frank.alist import Alist
from frank.alist import Alist
from frank.graph import InferenceGraph
from frank.alist import Attributes as tt
from frank.alist import VarPrefix as vx
from frank.alist import Branching as br
from frank.alist import States as states
import unittest
import matplotlib.pyplot as plt


class Test_Graph(unittest.TestCase):
        
    def test_graph_add_node(self):
        graph = InferenceGraph()
        alist1 = Alist(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1, '$y': 'Ghana'})
        alist2 = Alist(**{tt.ID: '101', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        graph.add_alist(alist1)
        graph.add_alist(alist2)
        nodes = graph.nodes()
        print(nodes)
        self.assertTrue(len(nodes) == 2)

    def test_graph_add_nodes(self):
        graph = InferenceGraph()
        alist1 = Alist(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1, '$y': 'Ghana'})
        alist2 = Alist(**{tt.ID: '101', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        graph.add_alists_from([alist1, alist2])
        nodes = graph.nodes()
        print(nodes)
        self.assertTrue(len(nodes) == 2)
    
    def test_graph_add_nodes_and_edges(self):
        graph = InferenceGraph()
        alist1 = Alist(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1, '$y': 'Ghana'})
        alist2 = Alist(**{tt.ID: '101', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        alist3 = Alist(**{tt.ID: '102', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        graph.add_alists_from([alist1])  
        plt.ion()
        # plt.plot()
        fig = plt.figure()
        plt.show()
        graph.display()  
        plt.pause(0.3)    
        graph.link(alist1, alist2, edge_label='TP')
        graph.link(alist1, alist3, edge_label='GS')
        edges = graph.edges()  
        plt.clf()    
        graph.display()        
        plt.pause(2)
        self.assertTrue(len(edges) > 0)

    def create_graph(self):
        graph = InferenceGraph()
        alist1 = Alist(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1, '$y': 'Ghana'})
        alist2 = Alist(**{tt.ID: '101', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        alist3 = Alist(**{tt.ID: '102', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        graph.add_alists_from([alist1])  
        graph.link(alist1, alist2, edge_label='TP')
        graph.link(alist1, alist3, edge_label='GS')
        return graph

    def create_graph2(self):
        graph = InferenceGraph()
        parent = Alist(**{tt.ID: '1', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                          tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        child = Alist(**{tt.ID: '1', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        child2 = Alist(**{tt.ID: '1', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                          tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        grandchild = Alist(**{tt.ID: '1', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                              tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        ggrandchild = Alist(**{tt.ID: '1', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                              tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        graph.add_alists_from([parent])  
        graph.link(parent, child, edge_label='TP')
        graph.link(parent, child2, edge_label='GS')
        graph.link(child, grandchild, edge_label='GS')
        graph.link(grandchild, ggrandchild, edge_label='GS')
        return graph

    def test_get_parent(self):
        graph = self.create_graph()
        parent_alist = graph.parent('111')
        print(parent_alist)
        self.assertTrue(parent_alist.id == '1')

    def test_get_alist(self):
        graph = self.create_graph()
        alist = graph.get_alist('111')
        self.assertTrue(alist.id == '111')
    
    def test_get_leaves(self):
        graph = self.create_graph()
        leaves = graph.leaf_nodes()
        print(leaves)
        self.assertTrue(len(leaves) > 0)

    def test_prune(self):
        graph = self.create_graph2()
        plt.ion()
        fig = plt.figure()
        plt.show()
        graph.display()  
        plt.pause(0.3)    
        graph.prune('111')
        edges = graph.edges()  
        plt.clf()    
        graph.display()        
        plt.pause(2)
    
        self.assertTrue(true)
    



if __name__ == '__main__':
    unittest.main()
