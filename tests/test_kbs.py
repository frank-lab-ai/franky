import unittest
# import kb.wikidata
from frank.kb import worldbank
from frank.kb import rdf
from frank.kb import conceptnet
from frank.kb import musicbrainz
from frank.alist import Alist
from frank.alist import Attributes as tt


class TestKbs(unittest.TestCase):

    def test_findPropertyFromDb(self):
        result = worldbank.getCountryPropertyDb(
            "People's Republic of China", 'id')
        self.assertEqual(result, "CHN", "must be 'CHN'")

    def test_find_entity_location(self):
        locations = worldbank.find_location_of_entity("Ghana")
        self.assertTrue(len(locations) > 0)

    @unittest.skip
    def test_findPropertyFromRdf(self):
        result = rdf.getCountryProperty('Ghana', 'id')
        self.assertEqual(len(result), 1, "should have at least one item")

    def test_getWorldBankData(self):
        a = Alist(**{tt.ID: '1', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'SP.POP.TOTL', tt.OBJECT: '',
                     tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        result = worldbank.find_property_object(a)
        self.assertEqual(len(result), 1, "should not be empty")


    def test_conceptnetGetClassInstances(self):
        result = conceptnet.find_instance_elements("continent")
        self.assertTrue(len(result) > 0 , "should not be empty")


    def test_conceptnetPartOf(self):
        result = conceptnet.find_relation_object("P9", "PartOf")
        self.assertTrue(len(result) > 0 , "should not be empty")

    def test_getMusicRecording(self):
        result = musicbrainz.find_recording(title="Torn", artist="Natalie")
        self.assertTrue(len(result) > 0, "list should not be empty")

    def test_getMusicDataArtist(self):
        a = Alist(**{tt.ID: '1', tt.SUBJECT: '?x', tt.PROPERTY: 'sang', tt.OBJECT: 'Giants',
                     tt.TIME: '2020', tt.OPVAR: '?x', tt.COST: 1})
        result = musicbrainz.find_property_values(a, search_element=tt.SUBJECT)
        self.assertTrue(result == None, "result should not be None")
    
    def test_getMusicDataTime(self):
        # when did Dermot sing Giants?
        a = Alist(**{tt.ID: '1', tt.SUBJECT: 'Dermot', tt.PROPERTY: 'sang', tt.OBJECT: 'Giants',
                     tt.TIME: '?x', tt.OPVAR: '?x', tt.COST: 1})
        result = musicbrainz.find_property_values(a, search_element=tt.TIME)
        self.assertTrue(result == None, "result should not be None")

if __name__ == '__main__':
    unittest.main()
