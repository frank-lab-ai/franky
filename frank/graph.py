'''
File: graph.py
Description: InferenceGraph for FRANK
'''

from typing import Callable

import networkx as nx
import plotly.graph_objects as go

from frank.alist import Alist
from frank.alist import NodeTypes as nt
from frank.alist import States as st


class InferenceGraph(nx.DiGraph):
    """Class definition for Frank's inference graph, inherits from networkx.DiGraph. Encodes
    alists, edges between alists, and methods for manipulating the graph."""

    def __init__(
            self,
        ):
        """Initializes the graph."""
        nx.DiGraph.__init__(self)

    def add_alist(
            self,
            alist: Alist,
        ) -> None:
        """Adds an alist to the graph.
        
        Parameters
        ----------
        alist: Alist
            Alist to add to the graph.
        """
        self.add_node(alist.id, **alist.attributes)

    def add_alists_from(
            self,
            alists: list[Alist],
        ) -> None:
        """Add a collection of alists to the graph.
        
        Parameters
        ----------
        alists: list[Alist]
            A collection of alists to add to the graph.
        """
        self.add_nodes_from([(a.id, a.attributes) for a in alists])

    def display(
            self,
        ) -> None:
        """CURRENTLY NOT USED.
        
        Displays the graph.
        """
        pos = nx.spring_layout(self)
        nx.draw(self, pos = pos, with_labels = True, node_size = 500, node_color = 'red', width = 1, font_size = 8)
        #formatted_edge_labels = {(elem[0], elem[1]): edge_labels[elem] for elem in edge_labels}
        nx.draw_networkx_edge_labels(self, pos = pos, edge_labels = edge_labels)
        # plt.show(block = False)

    def parent_alists(
            self,
            alist_id: str,
        ) -> list[Alist]:
        """Returns the parent alists of the specified alist.
        
        Parameters
        ----------
        alist_id: str
            ID of the alist whose parent alists are to be returned.
        
        Returns
        -------
        pred_arr: list[Alist]
            List of parent alists of the specified alist.
        """
        pred = self.predecessors(alist_id)
        pred_arr = [Alist(**self.nodes[x]) for x in pred]

        return pred_arr

    def child_alists(
            self,
            alist_id: str,
        ) -> list[Alist]:
        """Returns the child alists of the specified alist.
        
        Parameters
        ----------
        alist_id: str
            ID of the alist whose child alists are to be returned.
        
        Returns
        -------
        succ_arr: list[Alist]
            List of child alists of the specified alist.
        """
        succ = self.successors(alist_id)
        succ_arr = [Alist(**self.nodes[x]) for x in succ]

        return succ_arr

    def parent_ids(
            self,
            alist_id: str,
        ) -> list[str]:
        """Returns the parent alist IDs of the specified alist.
        
        Parameters
        ----------
        alist_id: str
            ID of the alist whose parent alists are to be returned.
        
        Returns
        -------
        pred_arr: list[Alist]
            List of parent alists of the specified alist.
        """
        pred = self.predecessors(alist_id)
        pred_arr = list(pred)

        return pred_arr

    def child_ids(
            self,
            alist_id: str,
        ) -> list[str]:
        """Returns the child alist IDs of the specified alist.
                
        Parameters
        ----------
        alist_id: str
            ID of the alist whose child alists are to be returned.
        
        Returns
        -------
        succ_arr: list[Alist]
            List of child alists of the specified alist.
        """
        succ = self.successors(alist_id)
        succ_arr = list(succ)

        return succ_arr

    def alist(
            self,
            alist_id: str,
        ) -> Alist:
        """Returns the alist with the specified ID.
        
        Parameters
        ----------
        alist_id: str
            ID of the alist to be returned.
        
        Returns
        -------
        alist: Alist
            Alist with the specified ID."""
        try:
            alist = Alist(**self.nodes[alist_id])
            return alist
        except KeyError as e:
            raise KeyError(f"Alist with id {alist_id} not found in graph") from e

    def alists(
            self,
        ) -> list[Alist]:
        """Returns a list of all alists in the graph.
        
        Returns
        -------
        alists: list[Alist]
            List of all alists in the graph.
        """
        alists = [Alist(**self.nodes[x]) for x in self.nodes()]

        return alists

    def alists_and_edges(
            self,
        ) -> list[Alist]:
        """Returns a list of all alists in the graph with their parent, child, and label.
        
        Returns
        -------
        alists: list[Alist]
            List of all alists in the graph with their parent, child, and label.
        """
        edges = [{'source': x[0], 'target': x[1], 'label':self[x[0]][x[1]]['label']}
                 for x in self.edges()]

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

    def link(
            self,
            parent: Alist,
            child: Alist,
            edge_label: str = '',
            create_new_id: bool = True,
        ) -> None:
        """Link two alists together in the graph.
        
        Parameters
        ----------
        parent: Alist
            Parent alist.
        child: Alist
            Child alist.
        edge_label: str
            Label for the edge between the two alists.
        create_new_id: bool
            Whether to create a new ID for the child alist.
        """
        if parent:
            succ = self.successors(parent.id)
            succ_nodes = [self.nodes[x] for x in succ]
            if create_new_id:
                child.depth = parent.depth + 1
                child.id = f"{parent.depth + 1}{parent.id}{len(succ_nodes) + 1}"
            self.add_alist(child)
            self.add_edge(parent.id, child.id, **{'label': edge_label})
        else:
            self.add_alist(child)

    def leaf_nodes(
            self,
            sort: bool = False,
            sort_key: Callable | None = None,
        ) -> list:
        """Returns a list of leaf nodes in the graph.
        
        Returns
        -------
        nodes: list
            List of leaf nodes in the graph.
        """
        nodes = [x for x in self.nodes() if self.out_degree(x) == 0]
        return nodes

    def leaf_alists(
            self,
            sort: bool = False,
            sort_key: Callable | None = None,
        ) -> list[Alist]:
        """Returns a list of leaf alists in the graph.
        
        Parameters
        ----------
        sort: bool
            Whether to sort the alists.
        sort_key: Callable | None
            Key to sort the alists by. If None, defaults to sorting by cost.
        
        Returns
        -------
        nodes: list
            List of leaf alists in the graph.
        """
        nodes = [Alist(**self.nodes[x])
                 for x in self.nodes() if self.out_degree(x) == 0]

        if sort and sort_key:
            nodes.sort(key = sort_key)
        elif sort and not sort_key:
            nodes.sort(key = lambda x: x.attributes['meta']['cost'])

        return nodes

    def prune(
            self,
            alist_id: str,
        ) -> None:
        """Prunes the graph by removing the specified alist and its children.
        
        Parameters
        ----------
        alist_id: str
            ID of the alist to be pruned.
        """
        succ = nx.bfs_successors(self, alist_id)
        for s in succ:
            self.remove_nodes_from(s[1])
        self.remove_node(alist_id)

    def frontier(
            self,
            size: int = 1,
            update_state: bool = True,
            state: int = st.UNEXPLORED,
        ) -> list[Alist]:
        """ Get a leaf node that are not in a reducible state.
        
        Parameters
        ----------
        size: int
            Number of leaf nodes to return.
        update_state: bool
            Whether to update the state of the returned leaf nodes.
        state: int
            State of the leaf nodes to return.
        
        Returns
        -------
        top: list[Alist]
            List of leaf nodes.
        """
        sorted_leaves = self.leaf_alists(sort = True)
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

    def blanket_subgraph(
            self,
            alist_id: str,
            ancestor_length: int = 1,
            descendant_length: int = 1,
        ) -> nx.DiGraph:
        """Returns a subgraph of the graph that contains the specified alist and its ancestors and
        descendants.
        
        Parameters
        ----------
        alist_id: str
            ID of the alist to be used as the center of the subgraph.
        ancestor_length: int
            Length of the ancestor path to include in the subgraph.
        descendant_length: int
            Length of the descendant path to include in the subgraph.
        
        Returns
        -------
        blanket: nx.DiGraph
            Subgraph of the graph that contains the specified alist and its ancestors and
            descendants.
        """
        ancestors = nx.single_target_shortest_path(
            self, alist_id, cutoff = ancestor_length)
        descendants = nx.single_source_shortest_path(
            self, alist_id, cutoff = descendant_length)
        nodes = set(list(ancestors.keys()) + list(descendants.keys()))
        blanket = self.subgraph(nodes)
        return blanket

    def simple_plot(
            self,
        ) -> None:
        """Plots a very simple tree showing inference graph structure."""
        G = nx.DiGraph(self.edges())
        pos = nx.drawing.nx_pydot.pydot_layout(G, prog='dot')
        nx.draw(G, pos, with_labels=True, arrows=True)

        return None

    def plot_plotly(
            self,
            subtitle: str= '',
        ) -> None:
        """Plots the graph using plotly.
        
        Parameters
        ----------
        subtitle: str
            Subtitle for the plot.
        """
        G = self
        pos = nx.drawing.nx_pydot.pydot_layout(G, prog='dot')
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
            x = edge_x,
            y = edge_y,
            line = {
                'width': 0.5,
                'color': '#888'
                },
            hoverinfo = 'none',
            mode = 'lines'
            )

        node_x = []
        node_y = []
        node_alist = []
        node_alist_text = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            alist = self.alist(node)
            node_alist.append(alist)
            text = str(alist)
            text = text.replace(': {', ': <br>{')
            node_alist_text.append(text)

        node_adjacencies = []
        node_text = []
        colors = []
        sizes = []
        marker_symbols = []
        pallette = {
            'grey': '#A5A5A5',
            'orange': '#F28C02',
            'cyan': '#0BE1DD',
            'black': '#000000',
            }
        for node, adjacencies in enumerate(G.adjacency()):
            node_adjacencies.append(len(adjacencies[1]))
            # node_text.append('# of connections: '+str(len(adjacencies[1])))
            # + "<br># connections:" +str(len(adjacencies[1])))
            node_text.append(node_alist_text[node])
            alist = node_alist[node]
            max_out_degree = min([len(adjacencies[1]), 8]
                                 )  # can have a max of 8

            if alist.id == '0':
                colors.append(pallette['cyan'])
            elif alist.node_type == nt.FACT:
                colors.append(pallette['black'])
            elif alist.state == st.REDUCED:
                colors.append(pallette['orange'])
            else:
                colors.append(pallette['grey'])

            if alist.node_type == nt.FACT:
                sizes.append(10 + max_out_degree)
                marker_symbols.append('circle-dot')
            elif alist.node_type == nt.ZNODE:
                sizes.append(12 + max_out_degree)
                marker_symbols.append('circle')
            elif alist.node_type == nt.HNODE:
                sizes.append(12 + max_out_degree)
                marker_symbols.append('square')

        node_trace = go.Scatter(
            x = node_x, y = node_y,
            mode = 'markers',
            hoverinfo = 'text',
            text = node_text,
            marker = dict(
                symbol = marker_symbols,
                # showscale = True,
                colorscale = 'YlGnBu',
                reversescale = True,
                color = colors,
                size = sizes,
                opacity = 0.9,
                line = dict(
                    color = '#6B6B6B',
                    width = 2
                )
            )
        )

        fig = go.Figure(data = [edge_trace, node_trace],
                        layout = go.Layout(
                        title = f'FRANK Inference Graph <br><span style="font-size:12px; margin-top:-5px">Q: {subtitle}</span>',
                        titlefont_size = 16,
                        showlegend = False,
                        hovermode = 'closest',
                        margin = dict(b=20, l=5, r=5, t=40),
                        annotations=[dict(
                            text="",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002)],
                        xaxis=dict(showgrid=False, zeroline=False,
                                   showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                        )
        fig.show()
