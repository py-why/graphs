from functools import cached_property
from typing import List
from copy import deepcopy

import networkx as nx
from networkx import DiGraph, Graph
import networkx.convert as convert
from networkx.classes.coreviews import AdjacencyView, UnionAdjacency, MultiAdjacencyView
from networkx.classes.reportviews import DegreeView, EdgeView, NodeView
from networkx.exception import NetworkXError


class MixedEdgeGraph:
    _graphs = list
    _edge_types = list
    graph_attr_dict_factory = dict

    def __init__(self, graphs: List, edge_types: List, **attr):
        """Base class for mixed-edge graphs.

        A mixed-edge graph stores nodes and different kinds of edges.
        The edges can represent non-directed (i.e. `Graph`), or 
        directed (i.e. `DiGraph`) edge connections among nodes.

        Nodes can be any nodes that can be represented in `Graph`,
        and `DiGraph`.

        Edges are represented as links between nodes with optional
        key/value attributes.

        Parameters
        ----------
        graphs : List of Graph | DiGraph
            A list of networkx single-edge graphs.
        edge_types : List of str
            A list of names for each edge type.
        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to graph as key=value pairs.

        See Also
        --------
        Graph
        DiGraph
        MultiGraph
        MultiDiGraph
        """
        if len(graphs) != len(edge_types):
            raise RuntimeError(f'The number of graph objects passed in, {len(graphs)}, '
            f'must match the number of edge types, {len(edge_types)}.')
        if any(not isinstance(graph, (Graph, DiGraph)) for graph in graphs):
            raise RuntimeError('All graph object inputs must be one of Networkx Graph or DiGraph.')

        self._graphs = graphs
        self._edge_types = edge_types

        self.graph_attr_dict_factory = self.graph_attr_dict_factory
        self.graph = self.graph_attr_dict_factory()  # dictionary for graph attributes
        # load graph attributes (must be after convert)
        self.graph.update(attr)

    @property
    def name(self):
        """String identifier of the graph.

        This graph attribute appears in the attribute dict G.graph
        keyed by the string `"name"`. as well as an attribute (technically
        a property) `G.name`. This is entirely user controlled.
        """
        return self.graph.get("name", "")

    @name.setter
    def name(self, s):
        self.graph["name"] = s

    @property
    def edge_types(self):
        return self._edge_types

    def get_graphs(self, edge_type='all'):
        """Get graphs representing the mixed-edges.

        Parameters
        ----------
        edge_type : str, optional
            The graph of the edge type to return, by default 'all', which
            will then return a list of all edge graphs.

        Returns
        -------
        graph : Graph | List of Graphs
            The graph representing a specific type of edge, or all edges.

        Raises
        ------
        ValueError
            _description_
        """
        if edge_type not in self._edge_types and edge_type != 'all':
            raise ValueError(f'Querying the edge_type of a MixedEdgeGraph must be '
                f'"all", or one of {self._edge_types}, not {edge_type}.')
        if edge_type == 'all':
            return self._graphs
        else:
            graph_idx = self._edge_types.index(edge_type)
            return self._graphs[graph_idx]

    @cached_property
    def nodes(self):
        # simply return the NodeView of the first graph
        return NodeView(self._graphs[0])

    def add_node(self, node_for_adding, **attr):
        for graph in self._graphs:
            graph.add_node(node_for_adding, **attr)

    def add_nodes_from(self, nodes_for_adding, **attr):
        for graph in self._graphs:
            graph.add_node(nodes_for_adding, **attr)

    def remove_node(self, n):
        for graph in self._graphs:
            graph.remove_node(n)

    def remove_nodes_from(self, nodes):
        for graph in self._graphs:
            graph.remove_nodes_from(nodes)

    def has_node(self, n):
        """Returns True if the graph contains the node n.

        Identical to `n in G`

        Parameters
        ----------
        n : node

        Examples
        --------
        >>> G = nx.path_graph(3)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.has_node(0)
        True

        It is more readable and simpler to use

        >>> 0 in G
        True

        """
        return self._graphs[0].has_node(n)

    def number_of_nodes(self):
        """Returns the number of nodes in the graph.

        Returns
        -------
        nnodes : int
            The number of nodes in the graph.

        See Also
        --------
        order: identical method
        __len__: identical method

        Examples
        --------
        >>> G = nx.path_graph(3)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.number_of_nodes()
        3
        """
        return len(self.nodes)

    def order(self):
        """Returns the number of nodes in the graph.

        Returns
        -------
        nnodes : int
            The number of nodes in the graph.

        See Also
        --------
        number_of_nodes: identical method
        __len__: identical method

        Examples
        --------
        >>> G = nx.path_graph(3)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.order()
        3
        """
        return len(self.nodes)

    def clear(self):
        for graph in self._graphs:
            graph.clear()

    def clear_edges(self):
        for graph in self._graphs:
            graph.clear_edges()

    def __iter__(self):
        """Iterate over the nodes. Use: 'for n in G'.

        Returns
        -------
        niter : iterator
            An iterator over all nodes in the graph.

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> [n for n in G]
        [0, 1, 2, 3]
        >>> list(G)
        [0, 1, 2, 3]
        """
        return iter(self.nodes)

    def __contains__(self, n):
        """Returns True if n is a node, False otherwise. Use: 'n in G'.

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> 1 in G
        True
        """
        try:
            return n in self.nodes
        except TypeError:
            return False

    def __len__(self):
        """Returns the number of nodes in the graph. Use: 'len(G)'.

        Returns
        -------
        nnodes : int
            The number of nodes in the graph.

        See Also
        --------
        number_of_nodes: identical method
        order: identical method

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> len(G)
        4

        """
        return len(self.nodes)

    def __getitem__(self, n):
        """Returns a dict of neighbors of node n.  Use: 'G[n]'.

        Parameters
        ----------
        n : node
           A node in the graph.

        Returns
        -------
        adj_dict : dictionary
           The adjacency dictionary for nodes connected to n.

        Notes
        -----
        G[n] is the same as G.adj[n] and similar to G.neighbors(n)
        (which is an iterator over G.adj[n])

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G[0]
        AtlasView({1: {}})
        """
        return self.adj[n]

    def update(self, edges=None, nodes=None, edge_type=None):
        """Update the graph using nodes/edges/graphs as input.

        Like dict.update, this method takes a graph as input, adding the
        graph's nodes and edges to this graph. It can also take two inputs:
        edges and nodes. Finally it can take either edges or nodes.
        To specify only nodes the keyword `nodes` must be used.

        The collections of edges and nodes are treated similarly to
        the add_edges_from/add_nodes_from methods. When iterated, they
        should yield 2-tuples (u, v) or 3-tuples (u, v, datadict).

        Parameters
        ----------
        edges : Graph object, collection of edges, or None
            The first parameter can be a graph or some edges. If it has
            attributes `nodes` and `edges`, then it is taken to be a
            Graph-like object and those attributes are used as collections
            of nodes and edges to be added to the graph.
            If the first parameter does not have those attributes, it is
            treated as a collection of edges and added to the graph.
            If the first argument is None, no edges are added.
        nodes : collection of nodes, or None
            The second parameter is treated as a collection of nodes
            to be added to the graph unless it is None.
            If `edges is None` and `nodes is None` an exception is raised.
            If the first parameter is a Graph, then `nodes` is ignored.

        Examples
        --------
        >>> G = nx.path_graph(5)
        >>> G.update(nx.complete_graph(range(4, 10)))
        >>> from itertools import combinations
        >>> edges = (
        ...     (u, v, {"power": u * v})
        ...     for u, v in combinations(range(10, 20), 2)
        ...     if u * v < 225
        ... )
        >>> nodes = [1000]  # for singleton, use a container
        >>> G.update(edges, nodes)

        Notes
        -----
        It you want to update the graph using an adjacency structure
        it is straightforward to obtain the edges/nodes from adjacency.
        The following examples provide common cases, your adjacency may
        be slightly different and require tweaks of these examples::

        >>> # dict-of-set/list/tuple
        >>> adj = {1: {2, 3}, 2: {1, 3}, 3: {1, 2}}
        >>> e = [(u, v) for u, nbrs in adj.items() for v in nbrs]
        >>> G.update(edges=e, nodes=adj)

        >>> DG = nx.DiGraph()
        >>> # dict-of-dict-of-attribute
        >>> adj = {1: {2: 1.3, 3: 0.7}, 2: {1: 1.4}, 3: {1: 0.7}}
        >>> e = [
        ...     (u, v, {"weight": d})
        ...     for u, nbrs in adj.items()
        ...     for v, d in nbrs.items()
        ... ]
        >>> DG.update(edges=e, nodes=adj)

        >>> # dict-of-dict-of-dict
        >>> adj = {1: {2: {"weight": 1.3}, 3: {"color": 0.7, "weight": 1.2}}}
        >>> e = [
        ...     (u, v, {"weight": d})
        ...     for u, nbrs in adj.items()
        ...     for v, d in nbrs.items()
        ... ]
        >>> DG.update(edges=e, nodes=adj)

        >>> # predecessor adjacency (dict-of-set)
        >>> pred = {1: {2, 3}, 2: {3}, 3: {3}}
        >>> e = [(v, u) for u, nbrs in pred.items() for v in nbrs]

        >>> # MultiGraph dict-of-dict-of-dict-of-attribute
        >>> MDG = nx.MultiDiGraph()
        >>> adj = {
        ...     1: {2: {0: {"weight": 1.3}, 1: {"weight": 1.2}}},
        ...     3: {2: {0: {"weight": 0.7}}},
        ... }
        >>> e = [
        ...     (u, v, ekey, d)
        ...     for u, nbrs in adj.items()
        ...     for v, keydict in nbrs.items()
        ...     for ekey, d in keydict.items()
        ... ]
        >>> MDG.update(edges=e)

        See Also
        --------
        add_edges_from: add multiple edges to a graph
        add_nodes_from: add multiple nodes to a graph
        """
        if edges is not None:
            if nodes is not None:
                self.add_nodes_from(nodes)
                self.add_edges_from(edges)
            else:
                # check if edges is a Graph object
                try:
                    graph_nodes = edges.nodes
                    graph_edges = edges.edges
                except AttributeError:
                    # edge not Graph-like
                    self.add_edges_from(edges)
                else:  # edges is Graph-like
                    self.add_nodes_from(graph_nodes.data())
                    self.add_edges_from(graph_edges.data())
                    self.graph.update(edges.graph)
        elif nodes is not None:
            self.add_nodes_from(nodes)
        else:
            raise NetworkXError("update needs nodes or edges input")

    @cached_property
    def adj(self):
        """Graph adjacency object holding the neighbors of each node.

        This object is a read-only dict-like structure with node keys
        and neighbor-dict values.  The neighbor-dict is keyed by neighbor
        to the edgekey-dict.  So `G.adj[3][2][0]['color'] = 'blue'` sets
        the color of the edge `(3, 2, 0)` to `"blue"`.

        Iterating over G.adj behaves like a dict. Useful idioms include
        `for nbr, datadict in G.adj[n].items():`.

        The neighbor information is also provided by subscripting the graph.
        So `for nbr, foovalue in G[node].data('foo', default=1):` works.

        For mixed-edge graphs, `G.adj` holds all adjacencies (any edge).
        """
        return {edge_type: graph.adj for edge_type, graph in zip(self.edge_types, self.get_graphs())}

    def _get_sub_graph(self, edge_type):
        if edge_type not in self.edge_types:
            raise ValueError(f'Edge type {edge_type} not part of the '
                f'existing edge types in graph.')
        edge_idx = self.edge_types.index(edge_type)
        return self._graphs[edge_idx]

    def has_edge(self, u, v, edge_type):
        """Returns True if the edge (u, v) is in the graph.

        This is the same as `v in G[u]` without KeyError exceptions.

        Parameters
        ----------
        u, v : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.

        Returns
        -------
        edge_ind : bool
            True if edge is in the graph, False otherwise.

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.has_edge(0, 1)  # using two nodes
        True
        >>> e = (0, 1)
        >>> G.has_edge(*e)  #  e is a 2-tuple (u, v)
        True
        >>> e = (0, 1, {"weight": 7})
        >>> G.has_edge(*e[:2])  # e is a 3-tuple (u, v, data_dictionary)
        True

        The following syntax are equivalent:

        >>> G.has_edge(0, 1)
        True
        >>> 1 in G[0]  # though this gives KeyError if 0 not in G
        True

        """
        return self._get_sub_graph(edge_type=edge_type).has_edge(u, v)

    def add_edge(self, u_for_edge, v_for_edge, edge_type, key=None, **attr):
        """Add an edge between u and v.

        The nodes u and v will be automatically added if they are
        not already in the graph.

        Edge attributes can be specified with keywords or by directly
        accessing the edge's attribute dictionary. See examples below.

        Parameters
        ----------
        u_for_edge, v_for_edge : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        edge_type : str
            The edge type.
        key : hashable identifier, optional (default=lowest unused integer)
            Used to distinguish multiedges between a pair of nodes.
        attr : keyword arguments, optional
            Edge data (or labels or objects) can be assigned using
            keyword arguments.

        Returns
        -------
        The edge key assigned to the edge.

        See Also
        --------
        add_edges_from : add a collection of edges

        Notes
        -----
        """
        key = self._get_sub_graph(edge_type).add_edge(u_for_edge, v_for_edge, key=key, **attr)
        return key

    def add_edges_from(self, ebunch_to_add, edge_type, **attr):
        """Add all the edges in ebunch_to_add.

        Parameters
        ----------
        ebunch_to_add : container of edges
            Each edge given in the container will be added to the
            graph. The edges must be given as 2-tuples (u, v) or
            3-tuples (u, v, d) where d is a dictionary containing edge data.
        attr : keyword arguments, optional
            Edge data (or labels or objects) can be assigned using
            keyword arguments.

        See Also
        --------
        add_edge : add a single edge
        add_weighted_edges_from : convenient way to add weighted edges

        Notes
        -----
        Adding the same edge twice has no effect but any edge data
        will be updated when each duplicate edge is added.

        Edge attributes specified in an ebunch take precedence over
        attributes specified via keyword arguments.

        Examples
        --------
        >>> G = nx.Graph()  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_edges_from([(0, 1), (1, 2)])  # using a list of edge tuples
        >>> e = zip(range(0, 3), range(1, 4))
        >>> G.add_edges_from(e)  # Add the path graph 0-1-2-3

        Associate data to edges

        >>> G.add_edges_from([(1, 2), (2, 3)], weight=3)
        >>> G.add_edges_from([(3, 4), (1, 4)], label="WN2898")
        """
        self._get_sub_graph(edge_type).add_edges_from(ebunch_to_add, **attr)

    def remove_edge(self, u, v, edge_type):
        """Remove an edge between u and v.

        Parameters
        ----------
        u, v : nodes
            Remove an edge between nodes u and v.
        edge_type : str
            The edge type.

        Raises
        ------
        NetworkXError
            If there is not an edge between u and v, or
            if there is no edge with the specified key.

        See Also
        --------
        remove_edges_from : remove a collection of edges
        """
        self._get_sub_graph(edge_type).remove_edge(u, v)

    @cached_property
    def edges(self):
        """An OutMultiEdgeView of the Graph as G.edges or G.edges().

        edges(self, nbunch=None, data=False, keys=False, default=None)

        The OutMultiEdgeView provides set-like operations on the edge-tuples
        as well as edge attribute lookup. When called, it also provides
        an EdgeDataView object which allows control of access to edge
        attributes (but does not provide set-like operations).
        Hence, ``G.edges[u, v, k]['color']`` provides the value of the color
        attribute for the edge from ``u`` to ``v`` with key ``k`` while
        ``for (u, v, k, c) in G.edges(data='color', default='red', keys=True):``
        iterates through all the edges yielding the color attribute with
        default `'red'` if no color attribute exists.

        Edges are returned as tuples with optional data and keys
        in the order (node, neighbor, key, data). If ``keys=True`` is not
        provided, the tuples will just be (node, neighbor, data), but
        multiple tuples with the same node and neighbor will be
        generated when multiple edges between two nodes exist.

        Parameters
        ----------
        nbunch : single node, container, or all nodes (default= all nodes)
            The view will only report edges from these nodes.
        data : string or bool, optional (default=False)
            The edge attribute returned in 3-tuple (u, v, ddict[data]).
            If True, return edge attribute dict in 3-tuple (u, v, ddict).
            If False, return 2-tuple (u, v).
        keys : bool, optional (default=False)
            If True, return edge keys with each edge, creating (u, v, k,
            d) tuples when data is also requested (the default) and (u,
            v, k) tuples when data is not requested.
        default : value, optional (default=None)
            Value used for edges that don't have the requested attribute.
            Only relevant if data is not True or False.

        Returns
        -------
        edges : OutMultiEdgeView
            A view of edge attributes, usually it iterates over (u, v)
            (u, v, k) or (u, v, k, d) tuples of edges, but can also be
            used for attribute lookup as ``edges[u, v, k]['foo']``.

        Notes
        -----
        Nodes in nbunch that are not in the graph will be (quietly) ignored.
        For directed graphs this returns the out-edges.

        Examples
        --------
        >>> G = nx.MultiDiGraph()
        >>> nx.add_path(G, [0, 1, 2])
        >>> key = G.add_edge(2, 3, weight=5)
        >>> key2 = G.add_edge(1, 2) # second edge between these nodes
        >>> [e for e in G.edges()]
        [(0, 1), (1, 2), (1, 2), (2, 3)]
        >>> list(G.edges(data=True))  # default data is {} (empty dict)
        [(0, 1, {}), (1, 2, {}), (1, 2, {}), (2, 3, {'weight': 5})]
        >>> list(G.edges(data="weight", default=1))
        [(0, 1, 1), (1, 2, 1), (1, 2, 1), (2, 3, 5)]
        >>> list(G.edges(keys=True))  # default keys are integers
        [(0, 1, 0), (1, 2, 0), (1, 2, 1), (2, 3, 0)]
        >>> list(G.edges(data=True, keys=True))
        [(0, 1, 0, {}), (1, 2, 0, {}), (1, 2, 1, {}), (2, 3, 0, {'weight': 5})]
        >>> list(G.edges(data="weight", default=1, keys=True))
        [(0, 1, 0, 1), (1, 2, 0, 1), (1, 2, 1, 1), (2, 3, 0, 5)]
        >>> list(G.edges([0, 2]))
        [(0, 1), (2, 3)]
        >>> list(G.edges(0))
        [(0, 1)]
        >>> list(G.edges(1))
        [(1, 2), (1, 2)]

        See Also
        --------
        in_edges, out_edges
        """
        return OutMultiEdgeView(self)

    def is_multigraph(self):
        """Returns True if graph is a multigraph, False otherwise."""
        return False

    def is_directed(self):
        """Returns True if graph is directed, False otherwise."""
        # TODO: need to double check that any directed graph algos. work as exp.
        return any([isinstance(graph, DiGraph) for graph in self.get_graphs()])

    def to_undirected(self):
        """Returns an undirected representation of the digraph.

        Returns
        -------
        G : Graph
            An undirected graph with the same name and nodes and
            with edge (u, v, data) if either (u, v, data) or (v, u, data)
            is in the digraph.  If both edges exist in a sub digraph and
            their edge data is different, only one edge is created
            with an arbitrary choice of which edge data to use.
            You must check and correct for this manually if desired.

        See Also
        --------
        MultiGraph, copy, add_edge, add_edges_from

        Notes
        -----
        This returns a "deepcopy" of the edge, node, and
        graph attributes which attempts to completely copy
        all of the data and references.

        This is in contrast to the similar D=MultiDiGraph(G) which
        returns a shallow copy of the data.

        See the Python copy module for more information on shallow
        and deep copies, https://docs.python.org/3/library/copy.html.

        Warning: If you have subclassed MultiDiGraph to use dict-like
        objects in the data structure, those changes do not transfer
        to the MultiGraph created by this method.

        Examples
        --------
        >>> G = nx.path_graph(2)  # or MultiGraph, etc
        >>> H = G.to_directed()
        >>> list(H.edges)
        [(0, 1), (1, 0)]
        >>> G2 = H.to_undirected()
        >>> list(G2.edges)
        [(0, 1)]
        """
        graph_class = Graph

        # deepcopy when not a view
        G = graph_class()
        G.graph.update(deepcopy(self._graphs[0].graph))
        G.add_nodes_from((n, deepcopy(d)) for n, d in self.nodes.items())
        G.add_edges_from(
            (u, v, key, deepcopy(data))
            for _, edge_adj in self.adj
            for u, nbrs in edge_adj.items()
            for v, keydict in nbrs.items()
            for key, data in keydict.items()
        )
        return G
