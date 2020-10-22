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
                         tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 2})
        child2 = Alist(**{tt.ID: '1', tt.SUBJECT: 'a_Ghana', tt.PROPERTY: 'P1082',
                          tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 5})
        grandchild = Alist(**{tt.ID: '1', tt.SUBJECT: 'b_Ghana', tt.PROPERTY: 'P1082',
                              tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 3})
        ggrandchild = Alist(**{tt.ID: '1', tt.SUBJECT: 'c_Ghana', tt.PROPERTY: 'P1082',
                              tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 4})
        # ggrandchild.state = states.EXPLORED
        graph.add_alists_from([parent])  
        graph.link(parent, child, edge_label='TP')
        graph.link(parent, child2, edge_label='GS')
        graph.link(child, grandchild, edge_label='GS')
        graph.link(grandchild, ggrandchild, edge_label='GS')
        return graph

    def test_get_parent(self):
        graph = self.create_graph()
        parent_alist = graph.parent_alists('111')
        print(parent_alist)
        self.assertTrue(parent_alist[0].id == '1')

    def test_get_children(self):
        graph = self.create_graph()
        child_alists = graph.child_alists('1')
        print(child_alists)
        self.assertTrue(len(child_alists) == 2)

    def test_get_alist(self):
        graph = self.create_graph()
        alist = graph.get_alist('111')
        self.assertTrue(alist.id == '111')
    
    def test_get_leaves(self):
        graph = self.create_graph()
        leaves = graph.leaf_nodes()
        print(leaves)
        self.assertTrue(len(leaves) > 0)

    def test_get_leaves_sorted(self):
        graph = self.create_graph2()
        leaves = graph.leaf_alists(sort=True)
        self.assertTrue(leaves[0].cost <= leaves[1].cost)

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
    
        self.assertTrue(graph.number_of_nodes() == 2)
    
    def test_frontier(self):
        graph = self.create_graph2()
        frontier1 = graph.frontier()
        frontier2 = graph.frontier(2)
        frontier3 = graph.frontier(state=states.REDUCIBLE)
        self.assertTrue(len(frontier1)==1 and len(frontier2)==1)

    def test_blanket(self):
        graph = self.create_graph2()
        blanket = graph.blanket_subgraph('111', ancestor_length=1, descendant_length=1)
        self.assertTrue(len(blanket.nodes()) == 3)

    def test_ui_graph(self):
        graph = self.create_graph2()
        gg = graph.ui_graph()

        self.assertTrue(len(gg['nodes']) > 2)
    
    def test_cytoscape_ui_graph(self):
        graph = self.create_graph2()
        gg = graph.cytoscape_ui_graph()

        self.assertTrue(len(gg['nodes']) > 2)

if __name__ == '__main__':
    unittest.main()
