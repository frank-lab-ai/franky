import unittest

import numpy as np
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
from frank.graph import InferenceGraph


class TestReduce(unittest.TestCase):

    def setUp(self):
        self.G = InferenceGraph()
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

        self.G.add_alist(self.alist) 
        self.G.link(self.alist, self.c1)
        self.G.link(self.alist, self.c2)
        self.G.link(self.alist, self.c3)
        self.G.link(self.alist, self.c4)
        self.G.link(self.alist, self.c5)
        self.G.link(self.alist, self.c6)
        self.G.link(self.alist, self.c7)

        self.G2 = InferenceGraph()
        self.alist2 = Alist(**{tt.ID: '1', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                              tt.OBJECT: '?x', tt.TIME: '2020', tt.OPVAR: '?x', tt.COST: 1})       

        self.c21 = Alist(**{tt.ID: '2', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                           tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1, '?x': ''})
        self.c21.instantiate_variable('?x', 'a')

        self.c22 = Alist(**{tt.ID: '3', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                           tt.OBJECT: '?x', tt.TIME: '2011', tt.OPVAR: '?x', tt.COST: 1, '?x': ''})
        self.c22.instantiate_variable('?x', 'b')

        self.c23 = Alist(**{tt.ID: '4', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                           tt.OBJECT: '?x', tt.TIME: '2012', tt.OPVAR: '?x', tt.COST: 1, '?x': ''})
        self.c23.instantiate_variable('?x', 'c')

        self.c24 = Alist(**{tt.ID: '5', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                           tt.OBJECT: '?x', tt.TIME: '2013', tt.OPVAR: '?x', tt.COST: 1, '?x': ''})
        self.c24.instantiate_variable('?x', 'd')

        self.c25 = Alist(**{tt.ID: '5', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                           tt.OBJECT: '?x', tt.TIME: '2014', tt.OPVAR: '?x', tt.COST: 1, '?x': ''})
        self.c25.instantiate_variable('?x', 'a')

        self.G2.add_alist(self.alist2) 
        self.G2.link(self.alist2, self.c21)
        self.G2.link(self.alist2, self.c22)
        self.G2.link(self.alist2, self.c23)
        self.G2.link(self.alist2, self.c24)
        self.G2.link(self.alist2, self.c25)

    def test_value(self):
        a = frank.reduce.value.reduce(self.alist, self.G.child_alists(self.alist.id), self.G)
        self.assertTrue(a.instantiation_value(tt.OBJECT), '124')
    
    def test_value2(self):
        a = frank.reduce.value.reduce(self.alist2, self.G2.child_alists(self.alist2.id), self.G2)
        self.assertTrue(a.instantiation_value(tt.OBJECT), 'a')

    def test_values(self):
        a = frank.reduce.values.reduce(self.alist, self.G.child_alists(self.alist.id), self.G)
        self.assertEqual(a.instantiation_value(tt.OBJECT),
                         '120,122,126,125,126,128,129')

    def test_sum(self):
        a = frank.reduce.sum.reduce(self.alist, self.G.child_alists(self.alist.id), self.G)
        self.assertEqual(float(a.instantiation_value(tt.OPVAR)), 876.0)

    def test_max(self):
        a = frank.reduce.max.reduce(self.alist, self.G.child_alists(self.alist.id), self.G)
        self.assertEqual(int(a.instantiation_value(tt.OPVAR)), 129)

    def test_min(self):
        a = frank.reduce.min.reduce(self.alist, self.G.child_alists(self.alist.id), self.G)
        self.assertEqual(a.instantiation_value(tt.OPVAR), '120')

    def test_count(self):
        a = frank.reduce.count.reduce(self.alist, self.G.child_alists(self.alist.id), self.G)
        self.assertEqual(a.instantiation_value(tt.OPVAR), 7)

    def test_product(self):
        a = frank.reduce.product.reduce(self.alist, self.G.child_alists(self.alist.id), self.G)
        self.assertEqual(a.instantiation_value(tt.OPVAR), 479724456960000.0)

    def test_regress(self):
        a = frank.reduce.regress.reduce(self.alist, self.G.child_alists(self.alist.id), self.G)
        print(a)
        self.assertAlmostEqual(
            a.instantiation_value(tt.OPVAR), 134.89, places=2)
    
    def test_gpregress(self):
        a = frank.reduce.gpregress.reduce(self.alist, self.G.child_alists(self.alist.id), self.G)
        print(a)
        self.assertAlmostEqual(
            a.instantiation_value(tt.OPVAR), 134, places=0 )

    def test_gpregress_2(self):
        alist = Alist(**{tt.ID: '101', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                              tt.OBJECT: '?x', tt.TIME: '2020', tt.OPVAR: '?x', tt.COST: 1})

        c1 = Alist(**{tt.ID: '21011', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                           tt.OBJECT: '?x', tt.TIME: '2019.0', tt.OPVAR: '?x', tt.COST: 1, '?x': 1839758040765.62})
        c2 = Alist(**{tt.ID: '21012', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                           tt.OBJECT: '?x', tt.TIME: '2018.0', tt.OPVAR: '?x', tt.COST: 1, '?x': 1885482534238.33})
        G = InferenceGraph()
        G.add_alist(alist)
        G.link(alist, c1)
        G.link(alist, c2)

        a = frank.reduce.gpregress.reduce(alist, G.child_alists(alist.id), G)
        print(a)
        self.assertAlmostEqual(
            a.instantiation_value(tt.OPVAR), 1792866444829.7, places=1)

    def test_do_gpregress(self):
        data = [
                [2019.0, 1839758040765.62],
                [2018.0, 1885482534238.33],
                [2017.0, 2055505502224.73], 
                [2016.0, 1793989048409.29], 
                [2015.0, 1802214373741.32], 
                [2014.0, 2455993625159.37], 
                [2013.0, 2472806919901.67], 
                [2012.0, 2465188674415.03], 
                [2011.0, 2616201578192.25], 
                [2010.0, 2208871646202.82], 
                [2009.0, 1667019780934.28], 
                [2008.0, 1695824571927.15], 
                [2007.0, 1397084345950.39], 
                [2006.0, 1107640297889.95]
                ]
        X, y = [], []
        for d in data:
            X.append([d[0]]) 
            y.append(d[1])
        X = np.array(X)
        y = np.array(y)
        predict = frank.reduce.gpregress.do_gpregress(X,y, np.array([2022.]), (np.max(y)-np.min(y))**2, 1)
        y_predict = predict[0]['y']
        self.assertAlmostEqual(y_predict, 1324535292167, places=0)

    @unittest.skip
    def test_nnpredict(self):
        a = frank.reduce.nnpredict.reduce(self.alist, self.G.child_alists(self.alist.id), self.G)
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
        G = InferenceGraph()
        G.add_alist(a)
        normalize.Normalize().decompose(a, G)
        child1 = G.child_alists(a.id)[0]
        result = frank.reduce.comp.reduce(
          child1 , G.child_alists(child1.id), G)
        self.assertTrue(result != None)

    def test_eq(self):
        a = Alist(**{tt.ID: '1', tt.OPVAR: '$x $y',
                     '$x': '?x1', '$y': '?y1', '?_eq_': ''})
        b = Alist(**{tt.ID: '2', tt.OPVAR: '?x1', '?x1': 20})
        c = Alist(**{tt.ID: '3', tt.OPVAR: '?y1', '?y1': 20})
        G = InferenceGraph()
        G.add_alist(a)
        G.link(a, b)
        G.link(a, c)
        result = frank.reduce.eq.reduce(a, [b, c], G)
        self.assertTrue(True if result.instantiation_value(
            '?_eq_') == 'true' else False)

    def test_gt(self):
        a = Alist(**{tt.ID: '1', tt.OPVAR: '$x $y',
                     '$x': '?x1', '$y': '?y1', '?_gt_': ''})
        b = Alist(**{tt.ID: '2', tt.OPVAR: '?x1', '?x1': 36})
        c = Alist(**{tt.ID: '3', tt.OPVAR: '?y1', '?y1': 33})

        G = InferenceGraph()
        G.add_alist(a)
        G.link(a, b)
        G.link(a, c)
        result = frank.reduce.gt.reduce(a, [b, c], G)
        self.assertTrue(True if result.instantiation_value(
            '?_gt_') == 'true' else False)

    def test_gte(self):
        a = Alist(**{tt.ID: '1', tt.OPVAR: '$x $y',
                     '$x': '?x1', '$y': '?y1', '?_gte_': ''})
        b = Alist(**{tt.ID: '2', tt.OPVAR: '?x1', '?x1': 33})
        c = Alist(**{tt.ID: '3', tt.OPVAR: '?y1', '?y1': 33})

        G = InferenceGraph()
        G.add_alist(a)
        G.link(a, b)
        G.link(a, c)
        result = frank.reduce.gte.reduce(a, [b, c], G)
        self.assertTrue(True if result.instantiation_value(
            '?_gte_') == 'true' else False)

    def test_lt(self):
        a = Alist(**{tt.ID: '1', tt.OPVAR: '$x $y',
                     '$x': '?x1', '$y': '?y1', '?_lt_': ''})
        b = Alist(**{tt.ID: '2', tt.OPVAR: '?x1', '?x1': 20})
        c = Alist(**{tt.ID: '3', tt.OPVAR: '?y1', '?y1': 30})

        G = InferenceGraph()
        G.add_alist(a)
        G.link(a, b)
        G.link(a, c)
        result = frank.reduce.lt.reduce(a, [b, c], G)
        self.assertTrue(True if result.instantiation_value(
            '?_lt_') == 'true' else False)

    def test_lte(self):
        a = Alist(**{tt.ID: '1', tt.OPVAR: '$x $y',
                     '$x': '?x1', '$y': '?y1', '?_lte_': ''})
        b = Alist(**{tt.ID: '2', tt.OPVAR: '?x1', '?x1': 30})
        c = Alist(**{tt.ID: '3', tt.OPVAR: '?y1', '?y1': 30})

        G = InferenceGraph()
        G.add_alist(a)
        G.link(a, b)
        G.link(a, c)
        result = frank.reduce.lte.reduce(a, [b, c], G)
        self.assertTrue(True if result.instantiation_value(
            '?_lte_') == 'true' else False)

    # def test_mode(self):
    #     c4 = Alist(**{tt.ID: '5', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
    #                      tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
    #     c4.attributes['?x'] = ''
    #     c4.instantiateVariable('?x', '122')
    #     self.alist.link_child(c4)

    #     a = frank.reduce.mode.reduce(self.alist, self.G.child_alists(self.alist.id), self.G)
    #     self.assertEqual(a.getInstantiationValue(tt.OPVAR), '122')


if __name__ == '__main__':
    unittest.main()
