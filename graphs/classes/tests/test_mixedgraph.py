import pytest

import networkx as nx
from networkx.utils import nodes_equal

from networkx.classes.tests.test_graph import BaseAttrGraphTester, BaseGraphTester
from networkx.classes.tests.test_graph import TestEdgeSubgraph as _TestGraphEdgeSubgraph
from networkx.classes.tests.test_graph import TestGraph as _TestGraph


# class BaseMixedEdgeGraphTester(BaseGraphTester):
    # def test_edges(self):
        # pass