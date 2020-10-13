import unittest

import frank
import frank.reduce.value
import frank.reduce.values
import frank.reduce.sum
import frank.reduce.min
import frank.reduce.max
import frank.reduce.mean
import frank.reduce.mode
import frank.reduce.count
import frank.reduce.product
import frank.reduce.regress
import frank.reduce.gpregress
import frank.reduce.comp
import frank.reduce.eq
import frank.reduce.gt
import frank.reduce.gte
import frank.reduce.lt
import frank.reduce.lte
# import frank.reduce.nnpredict
from frank.alist import Alist
from frank.alist import Attributes as tt
from frank.map import normalize


class TestReduce(unittest.TestCase):

    def setUp(self):
        self.alist = Alist(**{tt.ID: '1', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                              tt.OBJECT: '?x', tt.TIME: '2020', tt.OPVAR: '?x', tt.COST: 1})

        self.c1 = Alist(**{tt.ID: '2', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                           tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1, '?x': ''})
        self.c1.instantiate_variable('?x', '120')

        self.c2 = Alist(**{tt.ID: '3', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                           tt.OBJECT: '?x', tt.TIME: '2011', tt.OPVAR: '?x', tt.COST: 1, '?x': ''})
        self.c2.instantiate_variable('?x', '122')

        self.c3 = Alist(**{tt.ID: '4', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                           tt.OBJECT: '?x', tt.TIME: '2012', tt.OPVAR: '?x', tt.COST: 1, '?x': ''})
        self.c3.instantiate_variable('?x', '126')

        self.c4 = Alist(**{tt.ID: '5', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                           tt.OBJECT: '?x', tt.TIME: '2013', tt.OPVAR: '?x', tt.COST: 1, '?x': ''})
        self.c4.instantiate_variable('?x', '125')

        self.c5 = Alist(**{tt.ID: '5', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                           tt.OBJECT: '?x', tt.TIME: '2014', tt.OPVAR: '?x', tt.COST: 1, '?x': ''})
        self.c5.instantiate_variable('?x', '126')

        self.c6 = Alist(**{tt.ID: '6', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                           tt.OBJECT: '?x', tt.TIME: '2015', tt.OPVAR: '?x', tt.COST: 1, '?x': ''})
        self.c6.instantiate_variable('?x', '128')
        self.c7 = Alist(**{tt.ID: '7', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                           tt.OBJECT: '?x', tt.TIME: '2016', tt.OPVAR: '?x', tt.COST: 1, '?x': ''})
        self.c7.instantiate_variable('?x', '129')

        self.alist.link_child(self.c1)
        self.alist.link_child(self.c2)
        self.alist.link_child(self.c3)
        self.alist.link_child(self.c4)
        self.alist.link_child(self.c5)
        self.alist.link_child(self.c6)
        self.alist.link_child(self.c7)

    def test_value(self):
        a = frank.reduce.value.reduce(self.alist, self.alist.children)
        self.assertTrue(a.instantiation_value(tt.OBJECT), '124')

    def test_values(self):
        a = frank.reduce.values.reduce(self.alist, self.alist.children)
        self.assertEqual(a.instantiation_value(tt.OBJECT),
                         '120,122,126,125,126,128,129')

    def test_sum(self):
        a = frank.reduce.sum.reduce(self.alist, self.alist.children)
        self.assertEqual(float(a.instantiation_value(tt.OPVAR)), 876.0)

    def test_max(self):
        a = frank.reduce.max.reduce(self.alist, self.alist.children)
        self.assertEqual(int(a.instantiation_value(tt.OPVAR)), 129)

    def test_min(self):
        a = frank.reduce.min.reduce(self.alist, self.alist.children)
        self.assertEqual(a.instantiation_value(tt.OPVAR), '120')

    def test_count(self):
        a = frank.reduce.count.reduce(self.alist, self.alist.children)
        self.assertEqual(a.instantiation_value(tt.OPVAR), 7)

    def test_product(self):
        a = frank.reduce.product.reduce(self.alist, self.alist.children)
        self.assertEqual(a.instantiation_value(tt.OPVAR), 479724456960000.0)

    def test_regress(self):
        a = frank.reduce.regress.reduce(self.alist, self.alist.children)
        print(a)
        self.assertAlmostEqual(
            a.instantiation_value(tt.OPVAR), 134.89, places=2)
    
    def test_gpregress(self):
        a = frank.reduce.gpregress.reduce(self.alist, self.alist.children)
        print(a)
        self.assertAlmostEqual(
            a.instantiation_value(tt.OPVAR), 134.89, places=2)

    @unittest.skip
    def test_nnpredict(self):
        a = frank.reduce.nnpredict.reduce(self.alist, self.alist.children)
        self.assertAlmostEqual(
            a.instantiation_value(tt.OPVAR), 158.97, places=2)

    def test_comp(self):
        # root = Alist(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
        #                  tt.OBJECT: '?x', tt.TIME: '2016', tt.OPVAR: '?x', tt.COST: 1})
        # node101 = Alist(**{tt.OP:'comp', tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
        #                  tt.OBJECT: '?x', tt.TIME: '2016', tt.OPVAR: '?x', tt.COST: 1})
        a = Alist(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
                     tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1,
                     '$y': {"$is": "Ghana"}})
        normalize.Normalize().decompose(a)
        result = frank.reduce.comp.reduce(
            a.children[0], a.children[0].children)
        self.assertTrue(result != None)

    def test_eq(self):
        a = Alist(**{tt.ID: '1', tt.OPVAR: '$x $y',
                     '$x': '?x1', '$y': '?y1', '?_eq_': ''})
        b = Alist(**{tt.ID: '2', tt.OPVAR: '?x1', '?x1': 20})
        c = Alist(**{tt.ID: '3', tt.OPVAR: '?y1', '?y1': 20})

        a.link_child(b)
        a.link_child(c)
        result = frank.reduce.eq.reduce(a, [b, c])
        self.assertTrue(True if result.instantiation_value(
            '?_eq_') == 'true' else False)

    def test_gt(self):
        a = Alist(**{tt.ID: '1', tt.OPVAR: '$x $y',
                     '$x': '?x1', '$y': '?y1', '?_gt_': ''})
        b = Alist(**{tt.ID: '2', tt.OPVAR: '?x1', '?x1': 36})
        c = Alist(**{tt.ID: '3', tt.OPVAR: '?y1', '?y1': 33})

        a.link_child(b)
        a.link_child(c)
        result = frank.reduce.gt.reduce(a, [b, c])
        self.assertTrue(True if result.instantiation_value(
            '?_gt_') == 'true' else False)

    def test_gte(self):
        a = Alist(**{tt.ID: '1', tt.OPVAR: '$x $y',
                     '$x': '?x1', '$y': '?y1', '?_gte_': ''})
        b = Alist(**{tt.ID: '2', tt.OPVAR: '?x1', '?x1': 33})
        c = Alist(**{tt.ID: '3', tt.OPVAR: '?y1', '?y1': 33})

        a.link_child(b)
        a.link_child(c)
        result = frank.reduce.gte.reduce(a, [b, c])
        self.assertTrue(True if result.instantiation_value(
            '?_gte_') == 'true' else False)

    def test_lt(self):
        a = Alist(**{tt.ID: '1', tt.OPVAR: '$x $y',
                     '$x': '?x1', '$y': '?y1', '?_lt_': ''})
        b = Alist(**{tt.ID: '2', tt.OPVAR: '?x1', '?x1': 20})
        c = Alist(**{tt.ID: '3', tt.OPVAR: '?y1', '?y1': 30})

        a.link_child(b)
        a.link_child(c)
        result = frank.reduce.lt.reduce(a, [b, c])
        self.assertTrue(True if result.instantiation_value(
            '?_lt_') == 'true' else False)

    def test_lte(self):
        a = Alist(**{tt.ID: '1', tt.OPVAR: '$x $y',
                     '$x': '?x1', '$y': '?y1', '?_lte_': ''})
        b = Alist(**{tt.ID: '2', tt.OPVAR: '?x1', '?x1': 30})
        c = Alist(**{tt.ID: '3', tt.OPVAR: '?y1', '?y1': 30})

        a.link_child(b)
        a.link_child(c)
        result = frank.reduce.lte.reduce(a, [b, c])
        self.assertTrue(True if result.instantiation_value(
            '?_lte_') == 'true' else False)

    # def test_mode(self):
    #     c4 = Alist(**{tt.ID: '5', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
    #                      tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
    #     c4.attributes['?x'] = ''
    #     c4.instantiateVariable('?x', '122')
    #     self.alist.link_child(c4)

    #     a = frank.reduce.mode.reduce(self.alist, self.alist.children)
    #     self.assertEqual(a.getInstantiationValue(tt.OPVAR), '122')


if __name__ == '__main__':
    unittest.main()
