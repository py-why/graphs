

def bidirected_to_unobserved_confounder(G, bidirected_edge_name='bidirected'):
    """Convert all bidirected edges to unobserved confounders.

    Parameters
    ----------
    G : ADMG
        A causal graph with bidirected edges.

    Returns
    -------
    G_copy : ADMG
        A networkx DiGraph that is a fully specified DAG with unobserved
        variables added in place of bidirected edges.
    """
    uc_label = "Unobserved Confounders"
    G_copy = G.copy()

    # for every bidirected edge, add a new node
    for idx, latent_edge in enumerate(G.c_component_graph.edges):
        G_copy.add_node(f"U{idx}", label=uc_label, observed="no")

        # then add edges from the new UC to the nodes
        G_copy.add_edge(f"U{idx}", latent_edge[0])
        G_copy.add_edge(f"U{idx}", latent_edge[1])

        # remove the actual bidirected edge
        G_copy.remove_bidirected_edge(*latent_edge)

    return G_copy