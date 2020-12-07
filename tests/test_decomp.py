import unittest
from frank.map.temporal import Temporal
from frank.map.geospatial import Geospatial
from frank.map.normalize import Normalize
# from frank.map.isa import IsA
from frank.alist import Alist
from frank.alist import Attributes as tt
from frank.graph import InferenceGraph


class TestDecompositions(unittest.TestCase):
    def test_temporal(self):
        self.assertTrue(True)

    def test_temporal(self):
        alist = Alist(**{tt.ID: '0', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        G = InferenceGraph()
        G.add_alist(alist)
        temporal = Temporal()
        results = temporal.decompose(alist, G)
        self.assertTrue(len(G.child_alists(alist.id)) > 0,
                        "should have more than one element")

    @unittest.skip
    def test_geospatial(self):
        alist = Alist(**{tt.ID: '1', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        G = InferenceGraph()
        G.add_alist(alist)
        geospatial = Geospatial()
        results = geospatial.decompose(alist, G)
        self.assertTrue(len(G.child_alists(alist.id)) > 0,
                        "geospatial decomp should return more than one child")

    def test_normalize_filter(self):
        alist = Alist(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1,
                         '$y': {"$filter": [{"p": "type", "o": "country"}]}})
        G = InferenceGraph()
        G.add_alist(alist)
        normalize = Normalize()
        results = normalize.decompose(alist, G)
        self.assertTrue(len(G.child_alists(alist.id)) > 0)

    def test_normalize_filter_with_location(self):
        alist = Alist(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1,
                         '$y': {"$filter": [{"p": "type", "o": "country"}, {"p": "location", "o": "Africa"}]}})
        G = InferenceGraph()
        G.add_alist(alist)
        normalize = Normalize()
        results = normalize.decompose(alist, G)
        self.assertTrue(len(G.child_alists(alist.id)) > 0)

    def test_normalize_in(self):
        alist = Alist(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1,
                         '$y': {"$in": ["Ghana", "UK", "France"]}})
        
        G = InferenceGraph()
        G.add_alist(alist)
        normalize = Normalize()
        results = normalize.decompose(alist, G)
        self.assertTrue(len(G.child_alists(alist.id)) > 0)

    def test_normalize_is(self):
        alist = Alist(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1,
                         '$y': {"$is": "Ghana"}})
        G = InferenceGraph()
        G.add_alist(alist)
        normalize = Normalize()
        results = normalize.decompose(alist, G)
        self.assertTrue(len(G.child_alists(alist.id)) > 0)


if __name__ == "__main__":
    unittest.main()
