from networkx.algorithms import d_separated
from networkx import DiGraph

from graphs import MixedEdgeGraph
from .convert import bidirected_to_unobserved_confounder

def m_separated(G, x, y, z, bidirected_edge_name='bidirected', directed_edge_name='directed'):
    """Check m-separation among 'x' and 'y' given 'z' in mixed-edge causal graph G.

    This algorithm wraps ``networkx.algorithms.d_separated``, but
    allows one to pass in a ``ADMG`` instance instead.

    It first converts all bidirected edges into explicit unobserved
    confounding nodes in an explicit ``networkx.DiGraph``, which then
    calls ``networkx.algorithms.d_separated`` to determine d-separation.
    This inherently increases the runtime cost if there are many
    bidirected edges, because many nodes must be added.

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
    if not isinstance(G, MixedEdgeGraph):
        raise RuntimeError('m-separation should only be run on a MixedEdgeGraph. If '
                           'you have a directed graph, use "d_separated" function instead.')

    # get the full graph by converting bidirected edges into latent confounders
    # and keeping the directed edges
    explicit_G = G.compute_full_graph(to_networkx=True)

    bidirected_to_unobserved_confounder(G, )

    # get all unobserved confounders

    # make sure there are always conditioned on the conditioning set
    z = z.union(G._cond_set)
    return d_separated(explicit_G, x, y, z)

