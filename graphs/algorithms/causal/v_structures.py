from itertools import combinations


def _get_spouse(G, node):
    pass


def compute_v_structures(G):
    """Iterate through the G to compute all v-structures.

    Parameters
    ----------
    G : DiGraph | MixedEdgeGraph
        A causal G.

    Returns
    -------
    vstructs : Set[Tuple]
        The v structures within the graph. Each set has a 3-tuple with the
        parent, collider, and other parent.
    """
    vstructs: Set[Tuple] = set()
    for node in G.nodes:
        # get a list of the parents and spouses
        parents = set(G.parents(node))
        spouses = _get_spouse(G, node)
        triple_candidates = parents.union(spouses)
        for p1, p2 in combinations(triple_candidates, 2):
            if (
                not G.has_adjacency(p1, p2)  # should be unshielded triple
                and G.has_edge(p1, node)  # must be connected to the node
                and G.has_edge(p2, node)  # must be connected to the node
            ):
                p1_, p2_ = sorted((p1, p2))
                vstructs.add((p1_, node, p2_))
    return vstructs
