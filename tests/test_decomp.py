import unittest
from frank.map.temporal import Temporal
from frank.map.geospatial import Geospatial
from frank.map.normalize import Normalize
# from frank.map.isa import IsA
from frank.alist import Alist
from frank.alist import Attributes as tt


class TestDecompositions(unittest.TestCase):
    def test_temporal(self):
        self.assertTrue(True)

    def test_temporal(self):
        alist = Alist(**{tt.ID: '0', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        temporal = Temporal()
        results = temporal.decompose(alist)
        self.assertTrue(len(results.children) > 0,
                        "should have more than one element")

    @unittest.skip
    def test_geospatial(self):
        alist = Alist(**{tt.ID: '1', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        geospatial = Geospatial()
        results = geospatial.decompose(alist)
        self.assertTrue(len(results.children) > 0,
                        "geospatial decomp should return more than one child")

    def test_normalize_filter(self):
        alist = Alist(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1,
                         '$y': {"$filter": [{"p": "type", "o": "country"}]}})
        normalize = Normalize()
        results = normalize.decompose(alist)
        self.assertTrue(len(results.children) > 0)

    def test_normalize_filter_with_location(self):
        alist = Alist(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1,
                         '$y': {"$filter": [{"p": "type", "o": "country"}, {"p": "location", "o": "Africa"}]}})
        normalize = Normalize()
        results = normalize.decompose(alist)
        print(results.children[0])
        self.assertTrue(len(results.children) > 0)

    def test_normalize_in(self):
        alist = Alist(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1,
                         '$y': {"$in": ["Ghana", "UK", "France"]}})
        normalize = Normalize()
        results = normalize.decompose(alist)
        self.assertTrue(len(results.children) > 0)

    def test_normalize_is(self):
        alist = Alist(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1,
                         '$y': {"$is": "Ghana"}})
        normalize = Normalize()
        results = normalize.decompose(alist)
        self.assertTrue(len(results.children) > 0)


if __name__ == "__main__":
    unittest.main()
