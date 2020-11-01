
'''
File: graph.py
Description: InferenceGraph for FRANK
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)
'''

import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from frank.alist import Alist
from frank.alist import States as st


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
    
    def alists(self):
        alists = [Alist(**self.nodes[x]) for x in self.nodes()]
        return alists

    def alists_and_edges(self):
        edges = [{'source': x[0], 'target': x[1], 'label':self[x[0]][x[1]]['label']} for x in self.edges()]
        return edges

    def ui_graph(self):
        nodes = [dict(x.attributes) for x in self.alists()]
        nodes_arr = []
        for n in nodes:
            n.update(n['meta'])
            n.pop('meta', None)
            nodes_arr.append(n)
        return {'nodes': nodes, 'edges': self.alists_and_edges()}
    
    def cytoscape_ui_graph(self):
        g = self.ui_graph()
        nodes = [{"data": y} for y in g['nodes']]
        edges = [{"data": y} for y in g['edges']]
        return {'nodes': nodes, 'edges': edges}
        
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

    def leaf_nodes(self, sort=False, sort_key=None):
        nodes = [x for x in self.nodes() if self.out_degree(x) == 0 ]       
        return nodes
    
    def leaf_alists(self, sort=False, sort_key=None):
        nodes = [Alist(**self.nodes[x]) for x in self.nodes() if self.out_degree(x) == 0]

        if sort and sort_key:
            nodes.sort(key=sort_key)
        elif sort and not sort_key:
            nodes.sort(key = lambda x: x.attributes['meta']['cost'])
        
        return nodes

    def prune(self, alist_id):
        succ = nx.bfs_successors(self, alist_id)    
        for s in succ:
            self.remove_nodes_from(s[1])
        self.remove_node(alist_id)

    def frontier(self, size=1, update_state=True, state=st.UNEXPLORED):
        ''' Get a leaf node that are not in a reducible state '''
        sorted_leaves = self.leaf_alists(sort=True)
        top = []
        for n in sorted_leaves:
            if n.state == state:                
                top.append(n)
            if len(top) >= size:
                break
        if update_state:
            for t in top:
                t.state = st.EXPLORING
                self.add_alist(t)
                
        return top

    def blanket_subgraph(self, alist_id, ancestor_length=1, descendant_length=1):
        ancestors = nx.single_target_shortest_path(self, alist_id, cutoff=ancestor_length)
        descendants = nx.single_source_shortest_path(self, alist_id, cutoff=descendant_length)
        nodes = set(list(ancestors.keys()) + list(descendants.keys()))
        blanket = self.subgraph(nodes)
        return blanket

    def plot_plotly(self):
        G = self
        pos = nx.spring_layout(G)
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]][0], pos[edge[0]][1]
            x1, y1 = pos[edge[1]][0], pos[edge[1]][1]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        node_x = []
        node_y = []
        node_alist_text = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            text = str(self.alist(node))
            text = text.replace(': {',': <br>{')
            node_alist_text.append(text)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                # colorscale options
                #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                colorscale='YlGnBu',
                reversescale=True,
                color=[],
                size=10,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2))

        node_adjacencies = []
        node_text = []
        for node, adjacencies in enumerate(G.adjacency()):
            node_adjacencies.append(len(adjacencies[1]))
            # node_text.append('# of connections: '+str(len(adjacencies[1])))
            node_text.append(node_alist_text[node] + "<br># connections:" +str(len(adjacencies[1])))

        node_trace.marker.color = node_adjacencies
        node_trace.text = node_text

        fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='FRANK Inference Graph',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        annotations=[ dict(
                            text="",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002 ) ],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                        )
        fig.show()

        
        
    

    
        
        
        
        
    
    