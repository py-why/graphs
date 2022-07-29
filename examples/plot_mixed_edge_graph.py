"""
====================================================
MixedEdgeGraph - Graph with different types of edges
====================================================

A `MixedEdgeGraph` is a graph comprised of a tuple, :math:`G = (V, E)`.
The difference compared to the other networkx graphs are the edges, E.
``E`` is comprised of a set of mixed edges defined by the user. This
allows arbitrary representation of graphs with different types of edges.
The `MixedEdgeGraph` class represents each type of edge using an internal
graph that is one of `nx.Graph` or `nx.DiGraph` classes. Each internal graph
represents one type of edge. 

Semantically a `MixedEdgeGraph` with just one type of edge, is just a normal
`nx.Graph` or `nx.DiGraph`.

For example, causal graphs typically have two types of edges:

- ``->`` directed edges representing causal relations
- ``<->`` bidirected edges representing the presence of an unobserved
confounder.
"""

import matplotlib.pyplot as plt
import networkx as nx
from networkx import DiGraph, Graph

from graphs import MixedEdgeGraph

# %%
# Construct a MixedEdgeGraph
# --------------------------
# Using the ``MixedEdgeGraph``, we can represent a causal graph
# with two different kinds of edges. To create the graph, we
# use networkx `DiGraph` class to represent directed edges,
# and `Graph` class to represent edges without directions (i.e.
# bidirected edges). The edge types are then specified, so the mixed edge
# graph object knows which graphs are associated with which types of edges.

directed_G = DiGraph(
    [
        ("X", "Y"),
        ("Z", "X"),
    ]
)
bidirected_G = Graph(
    [
        ("X", "Y"),
    ]
)
G = MixedEdgeGraph(
    graphs=[directed_G, bidirected_G], edge_types=["directed", "bidirected"], name="IV Graph"
)

# Compute the multipartite_layout using the "layer" node attribute
pos = nx.multipartite_layout(G, subset_key="layer")

# we can then visualize the mixed-edge graph
fig, ax = plt.subplots()
nx.draw_networkx(G, pos=pos, ax=ax)
ax.set_title("Instrumental Variable Mixed Edge Causal Graph")
fig.tight_layout()
plt.show()

# %%
# Mixed Edge Graph Properties
# ---------------------------

print(G.name)

# G is directed since there are directed edges
print(f"{G} is directed: {G.is_directed()} because there are directed edges.")

# MixedEdgeGraphs are not multigraphs
print(G.is_multigraph())

# the different edge types present in the graph
print(G.edge_types)

# the internal networkx graphs representing each edge type
print(G.get_graphs())

# we can specifically get the networkx graph representation
# of any edge, e.g. the bidirected edges
bidirected_edges = G.get_graphs("bidirected")

# %%
# Mixed Edge Graph Operations on Nodes
# ------------------------------------

# Nodes: Similar to `nx.Graph` and `nx.DiGraph`, the nodes of the graph
# can be queried via the same API. By default nodes are stored
# inside every internal graph.
nodes = G.nodes
assert G.order() == len(G)
assert len(G) == G.number_of_nodes()
print(f"{G} has {G.order()} nodes: {nodes}")

# If we add a node, then we can query if the new node is there
print(f"Graph has node A: {G.has_node('A')}")
G.add_node("A")
print(f"Now graph has node A: {G.has_node('A')}")

# Now, we can remove the node
G.remove_node("A")
print(f"Graph has node A: {G.has_node('A')}")

# %%
# Mixed Edge Graph Operations on Edges
# ------------------------------------

# Edges: We can query specific edges by type
print(f"The graph has directed edges: {G.edges['directed']}")

# When querying, adding, or removing an edge, you must specify
# the edge type.
assert G.has_edge('X', 'Y', edge_type='directed')
G.add_edge('Z', 'Y', edge_type='bidirected')
G.remove_edge('Z', 'Y', edge_type='bidirected')

# Similar to the networkx API, the ``adj`` provides a way to iterate
# through the nodes and edges, but now over different edge types.
for edge_type, adj in G.adj:
    print(edge_type)
    print(adj)

# In contrast with the networkx API, a mixed edge graph provides
# a class method for iterating over all the possible adjacencies
# of a node (similar to ``neighbors`` function for Graph).
assert 'Z' in G.adjacencies('X')
