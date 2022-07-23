from collections.abc import Mapping


class UnionAdjacency(Mapping):
    """A read-only union of dict Adjacencies as a Map of Maps of Maps.

    The two input dict-of-dict-of-dicts represent the union of
    `G.succ` and `G.pred`. Return values are UnionAtlas
    The inner level of dict is read-write. But the
    middle and outer levels are read-only.

    succ : a dict-of-dict-of-dict {node: nbrdict}
    pred : a dict-of-dict-of-dict {node: nbrdict}
    The keys for the two dicts should be the same

    See Also
    ========
    UnionAtlas: View into dict-of-dict
    UnionMultiAdjacency: View into dict-of-dict-of-dict-of-dict
    """

    __slots__ = ("_succ", "_pred")

    def __getstate__(self):
        return {"_succ": self._succ, "_pred": self._pred}

    def __setstate__(self, state):
        self._succ = state["_succ"]
        self._pred = state["_pred"]

    def __init__(self, succ, pred):
        # keys must be the same for two input dicts
        assert len(set(succ.keys()) ^ set(pred.keys())) == 0
        self._succ = succ
        self._pred = pred

    def __len__(self):
        return len(self._succ)  # length of each dict should be the same

    def __iter__(self):
        return iter(self._succ)

    def __getitem__(self, nbr):
        return UnionAtlas(self._succ[nbr], self._pred[nbr])

    def copy(self):
        return {n: self[n].copy() for n in self._succ}

    def __str__(self):
        return str({nbr: self[nbr] for nbr in self})

    def __repr__(self):
        return f"{self.__class__.__name__}({self._succ!r}, {self._pred!r})"


class UnionMixedAdjacency(Mapping):
    """A read-only union of dict Adjacencies as a Map of Maps of Maps.

    The two input dict-of-dict-of-dicts represent the union of
    `G.succ` and `G.pred`. Return values are UnionAtlas
    The inner level of dict is read-write. But the
    middle and outer levels are read-only.

    succ : a dict-of-dict-of-dict {node: nbrdict}
    pred : a dict-of-dict-of-dict {node: nbrdict}
    The keys for the two dicts should be the same

    See Also
    ========
    UnionAtlas: View into dict-of-dict
    UnionMultiAdjacency: View into dict-of-dict-of-dict-of-dict
    """
    def __getstate__(self):
        return {"_succ": self._succ, "_pred": self._pred}

    def __setstate__(self, state):
        self._succ = state["_succ"]
        self._pred = state["_pred"]

    def __init__(self, graphs):
        for graph in graphs:
            if 
        # keys must be the same for two input dicts
        assert len(set(succ.keys()) ^ set(pred.keys())) == 0
        self._succ = succ
        self._pred = pred
    
    def __len__(self):
        return len(self._succ)  # length of each dict should be the same

    def __iter__(self):
        return iter(self._succ)

    def __getitem__(self, nbr):
        return UnionAtlas(self._succ[nbr], self._pred[nbr])

    def copy(self):
        return {n: self[n].copy() for n in self._succ}

    def __str__(self):
        return str({nbr: self[nbr] for nbr in self})

    def __repr__(self):
        return f"{self.__class__.__name__}({self._succ!r}, {self._pred!r})"


