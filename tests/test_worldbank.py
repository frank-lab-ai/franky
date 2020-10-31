import unittest
# import kb.wikidata
from frank.kb import worldbank
from frank.kb import rdf
from frank.kb import conceptnet
from frank.alist import Alist
from frank.alist import Attributes as tt


class TestWorldbank(unittest.TestCase):

    def test_findPropertyFromDb(self):
        result = worldbank.getCountryPropertyDb(
            "People's Republic of China", 'id')
        self.assertEqual(result, "CHN", "must be 'CHN'")

    def test_find_entity_location(self):
        locations = worldbank.find_location_of_entity("Ghana")
        self.assertTrue(len(locations) > 0)

    def test_find_entity_location(self):
        locations = worldbank.find_location_of_entity("London")
        self.assertTrue(len(locations) > 0)

    def test_getWorldBankData(self):
        a = Alist(**{tt.ID: '1', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'SP.POP.TOTL', tt.OBJECT: '',
                     tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        result = worldbank.find_property_object(a)
        self.assertEqual(len(result), 1, "should not be empty")


if __name__ == '__main__':
    unittest.main()
