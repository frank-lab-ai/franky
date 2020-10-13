from frank.alist import Alist
from frank.alist import Attributes as tt
from frank.alist import Contexts as ctx
from frank.kb import wikidata
from frank.map.temporal import Temporal
from frank.util import utils
import frank.context
import unittest
import json


class Test_Contexts(unittest.TestCase):

    def test_add_context(self):
        a = Alist(**{tt.ID: '1', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                     tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        ctx1 = [{ctx.nationality: 'United Kingdom'}, {ctx.place: 'United Kingdom',
                                          ctx.device: 'phone', ctx.datetime: '2020-04-30 12:00:00'},
                 {}]
        a.set(tt.CONTEXT, ctx1)
        ctx2 = a.get(tt.CONTEXT)
        alistJson = json.loads(json.dumps(a.attributes))
        self.assertEqual(ctx1, ctx2, "Context values do not match")

    def test_inject_context_IR(self):
        a = Alist(**{tt.ID: '1', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                     tt.OBJECT: '',tt.OPVAR: '?x', tt.COST: 1})
        ctx1 = [{ctx.nationality: 'United Kingdom'}, {ctx.place: 'England',
                                          ctx.device: 'phone', ctx.datetime: '2020-04-30 12:00:00'},
                 {'s':{'wikidata':'url://wikidata', 'worldbank':'wbankID'}, 't':'2020'}]
        a.set(tt.CONTEXT, ctx1)
        alist = frank.context.inject_retrieval_context(a, 'worldbank')
        self.assertEqual(alist.get(tt.TIME), '2020')

    def test_inject_query_context_loc(self):
        a = Alist(**{tt.ID: '1', tt.SUBJECT: 'London', tt.PROPERTY: 'P1082',
                     tt.OBJECT: '',tt.OPVAR: '?x', tt.COST: 1})
        ctx1 = [{ctx.nationality: 'United Kingdom'}, {ctx.place: 'England',
                                          ctx.device: 'phone', ctx.datetime: '2020-04-30 12:00:00'},
                 {}]
        a.set(tt.CONTEXT, ctx1)
        alist = frank.context.inject_query_context(a)
        self.assertEqual(alist.get(tt.CONTEXT)[2][tt.SUBJECT]['wikidata'], 'http://www.wikidata.org/entity/Q84')

    def test_inject_context_query(self):
        # query context
        a = Alist(**{tt.ID: '1', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                     tt.OBJECT: '', tt.OPVAR: '?x', tt.COST: 1})
        ctx1 = [{ctx.nationality: 'United Kingdom'}, {ctx.place: 'United Kingdom',
                                          ctx.device: 'phone', ctx.datetime: '2010-04-30 12:00:00'},
                 {}]
        a.set(tt.CONTEXT, ctx1)
        alist = frank.context.inject_query_context(a)
        ctx2 = a.get(tt.CONTEXT)
        self.assertEqual(ctx2[0][ctx.accuracy], 'low')

    def test_inject_context_query_2(self):
        # query context
        a = Alist(**{tt.ID: '1', tt.SUBJECT: '', tt.PROPERTY: 'P1082',
                     tt.OBJECT: '', tt.OPVAR: '?x', tt.COST: 1})
        ctx1 = [{ctx.nationality: 'United States'}, {ctx.place: 'Paris',
                                          ctx.device: 'phone', ctx.datetime: '2010-04-30 12:00:00'},
                 {}]
        a.set(tt.CONTEXT, ctx1)
        alist = frank.context.inject_query_context(a)
        ctx2 = a.get(tt.CONTEXT)
        self.assertEqual(ctx2[0][ctx.accuracy], 'low')

    def test_inject_context_inference(self):
        a = Alist(**{tt.ID: '1', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082', tt.TIME: '2023',
                     tt.OBJECT: '', tt.OPVAR: '?x', tt.COST: 1})
        ctx1 =  [{
                    ctx.nationality: 'United Kingdom',
                    ctx.accuracy: 'low',
                    ctx.speed:'low'}, 
                {
                    ctx.place: 'United Kingdom',
                    ctx.device: 'phone', 
                    ctx.datetime: '2020-07-27 11:00:00'},
                 {}
                ]
        a.set(tt.CONTEXT, ctx1)
        op_alist = Temporal().decompose(a)
        self.assertEqual(op_alist.get(tt.OP), 'regress')

    def test_context_composition(self):
        a = Alist(**{tt.ID: '1', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082', tt.TIME: '2023',
                     tt.OBJECT: '', tt.OPVAR: '?x', tt.COST: 1})
        ctx1 =  [{
                    ctx.nationality: 'United Kingdom' }, 
                {
                    ctx.place: 'United Kingdom',
                    ctx.device: 'computer', 
                    ctx.datetime: '2010-07-27 11:00:00'},
                 {}
                ]
        a.set(tt.CONTEXT, ctx1)
        query_ctx = frank.context.inject_query_context
        # query context should infer the ctx.accuracy from ctx.device
        op_alist = Temporal().decompose(query_ctx(a))
        self.assertEqual((op_alist.get(tt.OP), len(op_alist.children)), ('gpregress', 49))
    

    def test_search_with_context(self):
        a = Alist(**{tt.ID: '1', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                     tt.OBJECT: '', tt.OPVAR: '?x', tt.COST: 1})
        ctx1 = [{ctx.nationality: 'United Kingdom'}, {ctx.place: 'United Kingdom',
                                          ctx.device: 'phone', ctx.datetime: '2010-04-30 12:00:00'},
                 {}]
        a.set(tt.CONTEXT, ctx1)
        a = frank.context.inject_retrieval_context(a)
        result = wikidata.find_property_object(a)
        v = '0'
        if result:
            v = result[0].get(tt.OBJECT)
        self.assertAlmostEqual(utils.get_number(v, 0), 24200000, 1)
