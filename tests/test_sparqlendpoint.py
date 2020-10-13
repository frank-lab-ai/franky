import unittest
from frank.kb import rdf


class TestSparqlEndpoint(unittest.TestCase):
    @unittest.skip
    def test_findSubLocations(self):
        result = rdf.find_sub_location("Africa")
        self.assertTrue(len(result) > 0 and 'Ghana' in result,
                        "must return more than one item")


if __name__ == '__main__':
    unittest.main()
