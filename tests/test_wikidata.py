import unittest
from frank.kb import wikidata
from frank.alist import Alist
from frank.alist import Attributes as tt
from frank.alist import Contexts as ctx
import frank.context


class TestWikidata(unittest.TestCase):

    def test_wikidata_query_object(self):
        a = Alist(**{tt.ID: '1', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                     tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        result = wikidata.find_property_object(a)
        self.assertEqual(len(result), 1, "should be 24262901")
    
    def test_wikidata_query_object_with_context(self):
        a = Alist(**{tt.ID: '1', tt.SUBJECT: 'London', tt.PROPERTY: 'P1082',
                     tt.OBJECT: '',tt.OPVAR: '?x', tt.COST: 1})
        ctx1 = [{ctx.nationality: 'United Kingdom'}, 
                {ctx.place: 'England',
                 ctx.device: 'phone', 
                 ctx.datetime: '2018-04-30 12:00:00', 
                 tt.SUBJECT: 'http://www.wikidata.org/entity/Q84'},
                 {}]
        a.set(tt.CONTEXT, ctx1)
        frank.context.inject_retrieval_context(a)
        result = wikidata.find_property_object(a)
        self.assertTrue(len(result) > 0, "should have at least one item")

    def test_wikidata_query_object_with_context2(self):
        a = Alist(**{tt.ID: '1', tt.SUBJECT: 'London', tt.PROPERTY: 'P1082',
                     tt.OBJECT: '',tt.OPVAR: '?x', tt.COST: 1})
        ctx1 = [{ctx.nationality: 'United Kingdom'}, 
                {ctx.place: 'England',
                 ctx.device: 'phone', 
                 ctx.datetime: '2020-04-30 12:00:00', 
                 tt.SUBJECT: 'http://www.wikidata.org/entity/Q84'
                 },
                 {}]
        a.set(tt.CONTEXT, ctx1)
        frank.context.inject_retrieval_context(a)
        result = wikidata.find_property_object(a)
        self.assertTrue(len(result) > 0, "should have at least one item")

    def test_wikidata_query_object_with_context3(self):
        a = Alist(**{tt.ID: '1', tt.SUBJECT: 'London', tt.PROPERTY: 'P1082',
                     tt.OBJECT: '',tt.OPVAR: '?x', tt.COST: 1, tt.TIME: '2020'})
        ctx1 = [{ctx.nationality: 'United Kingdom'}, 
                {ctx.place: 'England',
                 ctx.device: 'phone', 
                 ctx.datetime: '2020-04-30 12:00:00', 
                 tt.SUBJECT: 'http://www.wikidata.org/entity/Q84'
                 },
                 {}]
        a.set(tt.CONTEXT, ctx1)
        frank.context.inject_retrieval_context(a)
        result = wikidata.find_property_object(a)
        self.assertTrue(len(result) ==0, "should have no item")

    def test_wikidata_query_object_with_context4(self):
        a = Alist(**{tt.ID: '1', tt.SUBJECT: 'London', tt.PROPERTY: 'P6',
                     tt.OBJECT: '',tt.OPVAR: '?x', tt.COST: 1})
        ctx1 = [{ctx.nationality: 'United Kingdom'}, 
                {ctx.place: 'England',
                 ctx.device: 'phone', 
                 ctx.datetime: '2020-04-30 12:00:00', 
                 tt.SUBJECT: 'http://www.wikidata.org/entity/Q84'
                 },
                 {}]
        a.set(tt.CONTEXT, ctx1)
        frank.context.inject_retrieval_context(a)
        result = wikidata.find_property_object(a)
        self.assertTrue(len(result) > 0, "should have at least one item")
        
    def test_wikidata_query_object_with_context_missing_subj(self):
        a = Alist(**{tt.ID: '1', tt.SUBJECT: '', tt.PROPERTY: 'P6',
                     tt.OBJECT: '',tt.OPVAR: '?x', tt.COST: 1})
        ctx1 = [{ctx.nationality: 'Ghana'}, 
                {ctx.place: 'London',
                 ctx.device: 'phone', 
                 ctx.datetime: '2020-04-30 12:00:00', 
                 tt.SUBJECT: 'http://www.wikidata.org/entity/Q84'
                 },
                 {}]
        a.set(tt.CONTEXT, ctx1)
        frank.context.inject_query_context(a)
        frank.context.inject_retrieval_context(a)
        result = wikidata.find_property_object(a)
        self.assertTrue(len(result) > 0, "should have at least one item")
        

    def test_findPropertyWithId(self):
        result = wikidata.find_entity_property_with_id('Ghana', 'P1082')
        self.assertTrue(len(result) > 0, "should have at least one item")

    def test_findSubElements(self):
        result = wikidata.find_sub_elements("Africa", "continent", "country")
        self.assertTrue(len(result) > 0, "should have at least one item")

    def test_findGeoPoliticalSubElements(self):
        result = wikidata.find_geopolitical_subelements("Africa", "country")
        self.assertTrue(len(result) > 0, "should not be an empty list")

    def test_findGeoPoliticalSubElementsCity(self):
        result = wikidata.find_geopolitical_subelements("Ghana", "city")
        self.assertTrue(len(result) > 0, "should not be an empty list")

    def test_wikidata_partOfRelationSubject(self):
        a = Alist(**{tt.ID: '1', tt.SUBJECT: '', tt.PROPERTY: 'P1082',
                     tt.OBJECT: 'Europe', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        result = wikidata.part_of_relation_subject(a)
        self.assertTrue(len(result) > 0, "should contain at least one item")

    def test_wikidata_partOfRelationObject(self):
        a = Alist(**{tt.ID: '1', tt.SUBJECT: 'Accra', tt.PROPERTY: 'P1082',
                     tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        result = wikidata.part_of_relation_object(a)
        self.assertTrue(len(result) > 0, "should contain at least one item")

    def test_wikidata_partOfGeoPoliticalSubject(self):
        a = Alist(**{tt.ID: '1', tt.SUBJECT: '', tt.PROPERTY: '__geopolitical:city',
                     tt.OBJECT: 'Ghana', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        result = wikidata.part_of_geopolitical_subject(a)
        self.assertTrue(len(result) > 0, "should contain at least one item")

    def test_search_properties(self):
        prop = wikidata.search_properties("president")
        self.assertTrue(len(prop) > 0)

    def test_find_entity_location(self):
        locations = wikidata.find_location_of_entity("London")
        self.assertTrue(len(locations) > 0)

    def test_search_properties_from_rootword(self):
        prop = wikidata.search_properties("singing")
        self.assertTrue(len(prop) > 0)

if __name__ == '__main__':
    unittest.main()
