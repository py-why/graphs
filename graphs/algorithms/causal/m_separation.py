from copy import deepcopy
from collections import deque

import networkx as nx
from networkx.utils import UnionFind

import graphs

from .convert import bidirected_to_unobserved_confounder

__all__ = ["m_separated"]


def markov_blanket(G, x, bidirected_edge_name="bidirected", directed_edge_name="directed"):
    pass


def m_separated(G, x, y, z, bidirected_edge_name="bidirected", directed_edge_name="directed"):
    """Check m-separation among 'x' and 'y' given 'z' in mixed-edge causal graph G.

    This algorithm adapts the linear time algorithm presented in [1] currently implemeted in networkx.algorithms.d_separation to work for mixed-edge causal graphs.

    This algorithm first obtains the ancestral subgraph of x | y | z which only requires knowledge of the directed edges. Then, all outgoing directed edges from nodes in z are deleted. After that, an undirected graph composed from the directed and bidirected edges amongst the remaining nodes is created. Then, x is independent of y given z if x is disconnected from y in this new graph.

    [1] Darwiche, A.  (2009).  Modeling and reasoning with Bayesian networks. 
       Cambridge: Cambridge University Press.

    Parameters
    ----------
    G : mixed-edge-graph
        Mixed edge causal graph.
    x : set
        First set of nodes in ``G``.
    y : set
        Second set of nodes in ``G``.
    z : set
        Set of conditioning nodes in ``G``. Can be empty set.

    Returns
    -------
    b : bool
        A boolean that is true if ``x`` is m-separated from ``y`` given ``z`` in ``G``.

    See Also
    --------
    networkx.algorithms.d_separation.d_separated

    Notes
    -----
    This wraps the networkx implementation, which only allows DAGs. Since
    ``ADMG`` is not represented.
    """
    if not isinstance(G, graphs.MixedEdgeGraph):
        raise RuntimeError(
            "m-separation should only be run on a MixedEdgeGraph. If "
            'you have a directed graph, use "d_separated" function instead.'
        )
    if any(
        edge_type not in G.edge_types for edge_type in [bidirected_edge_name, directed_edge_name]
    ):
        raise RuntimeError(
            f"m-separation only works on graphs with directed and bidirected edges. "
            f"Your graph passed in has the following edge types: {G.edge_types}, whereas "
            f"the function is expecting directed edges named {directed_edge_name} and "
            f"bidirected edges named {bidirected_edge_name}."
        )
    union_xyz = x.union(y).union(z)
    # get directed edges
    G_copy = nx.DiGraph()
    G_copy.add_nodes_from((n, deepcopy(d)) for n, d in G.nodes.items())
    G_copy.graph = deepcopy(G.graph)

    G_copy.add_edges_from(G.get_graphs(edge_type=directed_edge_name).edges)

    # get bidirected edges subgraph
    G_bidirected = nx.Graph()
    G_bidirected.add_nodes_from((n, deepcopy(d)) for n, d in G.nodes.items())
    G_bidirected.add_edges_from(G.get_graphs(edge_type=bidirected_edge_name).edges)

    # get ancestral subgraph of x | y | z by removing leaves in directed graph that are not in x | y | z

    # until no more leaves can be removed.
    leaves = deque([n for n in G_copy.nodes if G_copy.out_degree[n] == 0])
    while len(leaves) > 0:
        leaf = leaves.popleft()
        if leaf not in union_xyz:
            for p in G_copy.predecessors(leaf):
                if G_copy.out_degree[p] == 1:
                    leaves.append(p)
            G_copy.remove_node(leaf)
            G_bidirected.remove_node(leaf)

    # remove outgoing directed edges in z
    edges_to_remove = list(G_copy.out_edges(z))
    G_copy.remove_edges_from(edges_to_remove)

    # make new undirected graph from remaining directed and bidirected edges
    G_final = nx.Graph()
    G_final.add_nodes_from((n, deepcopy(d)) for n, d in G_final.nodes.items())
    G_final.add_edges_from(G_copy.edges)
    G_final.add_edges_from(G_bidirected.edges)

    print(G_final.edges)

    disjoint_set = UnionFind(G_final.nodes())
    for component in nx.connected_components(G_final):
        disjoint_set.union(*component)
    disjoint_set.union(*x)
    disjoint_set.union(*y)

    if x and y and disjoint_set[next(iter(x))] == disjoint_set[next(iter(y))]:
        return False
    else:
        return True
