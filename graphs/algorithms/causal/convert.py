def bidirected_to_unobserved_confounder(
    G, bidirected_edge_name="bidirected", uc_label="Unobserved Confounders"
):
    """Convert all bidirected edges to unobserved confounders.

    Parameters
    ----------
    G : MixedEdgeGraph
        A causal graph with bidirected edges.
    bidirected_edge_name : str
        The name of the graph representing bidirected edges in ``G``.
    uc_label : str
        The ``label`` of the unobserved variables that are added in.

    Returns
    -------
    G_copy : MixedEdgeGraph
        A networkx DiGraph that is a fully specified DAG with unobserved
        variables added in place of bidirected edges.

    Notes
    -----
    This converts bidirected to unobserved confounding variables, that are unobserved
    nodes that have a directed edge pointing to the two variables that were connected
    with a bidirected edge.
    """
    uc_label = "Unobserved Confounders"
    G_copy = G.copy()

    # for every bidirected edge, add a new node
    bidirected_sub_graph = G.get_graphs(edge_type=bidirected_edge_name)
    for idx, latent_edge in enumerate(bidirected_sub_graph.edges):
        G_copy.add_node(f"U{idx}", label=uc_label, observed="no")

        # then add edges from the new UC to the nodes
        G_copy.add_edge(f"U{idx}", latent_edge[0])
        G_copy.add_edge(f"U{idx}", latent_edge[1])

        # remove the actual bidirected edge
        G_copy.remove_edge(*latent_edge, edge_type=bidirected_edge_name)

    return G_copy
