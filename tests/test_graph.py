from frank.alist import Alist
from frank.alist_basic import AlistB
from frank.graph import InferenceGraph
from frank.alist import Attributes as tt
from frank.alist import VarPrefix as vx
from frank.alist import Branching as br
from frank.alist import States as states
import unittest
import matplotlib.pyplot as plt


class Test_Alist(unittest.TestCase):
        
    def test_graph_add_node(self):
        graph = InferenceGraph()
        alist1 = AlistB(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1, '$y': 'Ghana'})
        alist2 = AlistB(**{tt.ID: '101', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        graph.add_alist(alist1)
        graph.add_alist(alist2)
        nodes = graph.nodes()
        print(nodes)
        self.assertTrue(len(nodes) == 2)

    def test_graph_add_nodes(self):
        graph = InferenceGraph()
        alist1 = AlistB(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1, '$y': 'Ghana'})
        alist2 = AlistB(**{tt.ID: '101', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        graph.add_alists_from([alist1, alist2])
        nodes = graph.nodes()
        print(nodes)
        self.assertTrue(len(nodes) == 2)
    
    def test_graph_add_nodes_and_edges(self):
        graph = InferenceGraph()
        alist1 = AlistB(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1, '$y': 'Ghana'})
        alist2 = AlistB(**{tt.ID: '101', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        graph.add_alists_from([alist1, alist2])  
        plt.ion()
        # plt.plot()
        fig = plt.figure()
        plt.show()
        graph.display()  
        plt.pause(0.3)    
        graph.add_edge(alist1.id, alist2.id)
        edges = graph.edges()  
        plt.clf()    
        graph.display()        
        plt.pause(2)
        print(edges)
        self.assertTrue(len(edges) == 1)

    def create_graph(self):
        graph = InferenceGraph()
        alist1 = AlistB(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1, '$y': 'Ghana'})
        alist2 = AlistB(**{tt.ID: '101', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        graph.add_alists_from([alist1, alist2])  
        graph.add_edge(alist1.id, alist2.id)
        return graph

    def test_get_parent(self):
        graph = self.create_graph()
        parent_alist = graph.parent('101')
        print(parent_alist)
        self.assertTrue(parent_alist.id == '1')

    def test_get_alist(self):
        graph = self.create_graph()
        alist = graph.get_alist('101')
        self.assertTrue(alist.id == '101')



if __name__ == '__main__':
    unittest.main()
