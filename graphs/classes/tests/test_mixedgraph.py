import networkx as nx
import pytest
from networkx.classes.tests.test_graph import BaseAttrGraphTester, BaseGraphTester
from networkx.classes.tests.test_graph import TestEdgeSubgraph as _TestGraphEdgeSubgraph
from networkx.classes.tests.test_graph import TestGraph
from networkx.utils import edges_equal, graphs_equal, nodes_equal

from graphs import MixedEdgeGraph


class TestMixedEdgeGraph:
    def setup_method(self):
        self.Graph = MixedEdgeGraph
        self._graph_func = nx.Graph

        # build dict-of-dict-of-dict K3
        ed1, ed2, ed3 = ({}, {}, {})
        self.k3adj = {0: {1: ed1, 2: ed2}, 1: {0: ed1, 2: ed3}, 2: {0: ed2, 1: ed3}}
        self.k3edges = [(0, 1), (0, 2), (1, 2)]
        self.k3nodes = [0, 1, 2]
        self.K3_edge_type = "undirected"
        self.K3 = self.Graph()
        self.K3.add_edge_type(nx.Graph(), self.K3_edge_type)
        self.K3.add_edges_from(self.k3edges, edge_type=self.K3_edge_type)
        # self.K3._adj = self.k3adj
        # self.K3._node = {}
        # self.K3._node[0] = {}
        # self.K3._node[1] = {}
        # self.K3._node[2] = {}

    def test_add_edge(self):
        edge_type = "bidirected"
        G = self.Graph()
        G.add_edge_type(self._graph_func(), edge_type=edge_type)
        G.add_edge(0, 1, edge_type=edge_type)
        assert G.adj() == {edge_type: {0: {1: {}}, 1: {0: {}}}}
        G = self.Graph()
        G.add_edge_type(self._graph_func(), edge_type=edge_type)
        G.add_edge(*(0, 1), edge_type=edge_type)
        assert G.adj() == {edge_type: {0: {1: {}}, 1: {0: {}}}}

    def test_add_edges_from(self):
        edge_type = "undirected"
        G = self.Graph()
        G.add_edge_type(self._graph_func(), edge_type=edge_type)
        G.add_edges_from([(0, 1), (0, 2, {"weight": 3})], edge_type=edge_type)
        assert G.adj()[edge_type] == {
            0: {1: {}, 2: {"weight": 3}},
            1: {0: {}},
            2: {0: {"weight": 3}},
        }
        G = self.Graph()
        G.add_edge_type(self._graph_func(), edge_type=edge_type)
        G.add_edges_from(
            [(0, 1), (0, 2, {"weight": 3}), (1, 2, {"data": 4})], data=2, edge_type=edge_type
        )
        assert G.adj()[edge_type] == {
            0: {1: {"data": 2}, 2: {"weight": 3, "data": 2}},
            1: {0: {"data": 2}, 2: {"data": 4}},
            2: {0: {"weight": 3, "data": 2}, 1: {"data": 4}},
        }

        with pytest.raises(nx.NetworkXError):
            G.add_edges_from([(0,)], edge_type=edge_type)  # too few in tuple
        with pytest.raises(nx.NetworkXError):
            G.add_edges_from([(0, 1, 2, 3)], edge_type=edge_type)  # too many in tuple
        with pytest.raises(TypeError):
            G.add_edges_from([0], edge_type=edge_type)  # not a tuple
        with pytest.raises(TypeError):
            G.add_edges_from([0])  # no edge type

    def test_remove_edge(self):
        G = self.K3.copy()
        G.remove_edge(0, 1, self.K3_edge_type)
        assert G.adj() == {self.K3_edge_type: {0: {2: {}}, 1: {2: {}}, 2: {0: {}, 1: {}}}}
        with pytest.raises(nx.NetworkXError):
            G.remove_edge(-1, 0, self.K3_edge_type)

    def test_remove_edges_from(self):
        G = self.K3.copy()
        G.remove_edges_from([(0, 1)], self.K3_edge_type)
        assert G.adj() == {self.K3_edge_type: {0: {2: {}}, 1: {2: {}}, 2: {0: {}, 1: {}}}}
        G.remove_edges_from([(0, 0)], self.K3_edge_type)  # silent fail

    @pytest.mark.skip(reason="need to implement")
    def test_edges_data(self):
        G = self.K3
        all_edges = [(0, 1, {}), (0, 2, {}), (1, 2, {})]
        assert edges_equal(G.edges(data=True), all_edges)
        assert edges_equal(G.edges(0, data=True), [(0, 1, {}), (0, 2, {})])
        assert edges_equal(G.edges([0, 1], data=True), all_edges)
        with pytest.raises(nx.NetworkXError):
            G.edges(-1, True)

    @pytest.mark.skip(reason="need to implement")
    def test_get_edge_data(self):
        G = self.K3.copy()
        assert G.get_edge_data(0, 1) == {}
        assert G[0][1] == {}
        assert G.get_edge_data(10, 20) is None
        assert G.get_edge_data(-1, 0) is None
        assert G.get_edge_data(-1, 0, default=1) == 1

    def test_update(self):
        # specify both edges and nodes
        G = self.K3.copy()
        G.update(
            nodes=[3, (4, {"size": 2})],
            edges=[(4, 5), (6, 7, {"weight": 2})],
            edge_type=self.K3_edge_type,
        )
        nlist = [
            (0, {}),
            (1, {}),
            (2, {}),
            (3, {}),
            (4, {"size": 2}),
            (5, {}),
            (6, {}),
            (7, {}),
        ]
        assert sorted(G.nodes.data()) == nlist
        if G.is_directed():
            elist = [
                (0, 1, {}),
                (0, 2, {}),
                (1, 0, {}),
                (1, 2, {}),
                (2, 0, {}),
                (2, 1, {}),
                (4, 5, {}),
                (6, 7, {"weight": 2}),
            ]
        else:
            elist = [
                (0, 1, {}),
                (0, 2, {}),
                (1, 2, {}),
                (4, 5, {}),
                (6, 7, {"weight": 2}),
            ]
        assert sorted(G.edges()[self.K3_edge_type].data()) == elist
        assert G.graph == {}

        # no keywords -- order is edges, nodes
        G = self.K3.copy()
        G.update([(4, 5), (6, 7, {"weight": 2})], [3, (4, {"size": 2})], self.K3_edge_type)
        assert sorted(G.nodes.data()) == nlist
        assert sorted(G.edges()[self.K3_edge_type].data()) == elist
        assert G.graph == {}

        # update using only a graph
        edge_type = "bidirected"
        G = self.Graph()
        G.add_edge_type(self._graph_func(), edge_type=edge_type)
        G.graph["foo"] = "bar"
        G.add_node(2, data=4)
        G.add_edge(0, 1, edge_type=edge_type, weight=0.5)
        GG = G.copy()
        # H = self.Graph()
        # H.add_edge_type(self._graph_func(), edge_type=edge_type)
        # GG.update(H)
        # print(G.adj)
        # print(GG.adj)
        # assert graphs_equal(G, GG)
        # H.update(G)
        # assert graphs_equal(H, G)

        # update nodes only
        H = self.Graph()
        with pytest.raises(RuntimeError, match="No edge type"):
            H.update(nodes=[3, 4])
        H.add_edge_type(self._graph_func(), edge_type=edge_type)
        H.update(nodes=[3, 4])
        assert H.nodes ^ {3, 4} == set()
        # assert H.size() == 0

        # update edges only
        H = self.Graph()
        with pytest.raises(RuntimeError, match="Edge type is undefined"):
            H.update(edges=[(3, 4)])
        H.add_edge_type(self._graph_func(), edge_type=edge_type)
        H.update(edges=[(3, 4)], edge_type=edge_type)
        assert sorted(H.edges()[edge_type].data()) == [(3, 4, {})]
        # assert H.size() == 1

        # No inputs -> exception
        with pytest.raises(nx.NetworkXError):
            nx.Graph().update()
