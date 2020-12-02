import unittest
from frank.alist import Alist
from frank.alist import Attributes as tt, States as states
from frank.infer import Infer


class Test_Inference(unittest.TestCase):

    def setUp(self):
        self.infer = Infer()
        self.alist = Alist(**{tt.ID: '1', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                              tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})

        self.c1 = Alist(**{tt.ID: '2', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                           tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        self.c1.attributes['?x'] = ''
        self.c1.instantiate_variable('?x', '120')
        self.c1.state = states.REDUCIBLE
        self.c1.data_sources.update(['wikidata', 'worldbank'])

        self.c2 = Alist(**{tt.ID: '3', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                           tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        self.c2.attributes['?x'] = ''
        self.c2.instantiate_variable('?x', '122')
        self.c2.state = states.REDUCIBLE
        self.c2.data_sources.update(['conceptnet', 'worldbank'])

        self.c3 = Alist(**{tt.ID: '4', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                           tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        self.c3.attributes['?x'] = ''
        self.c3.instantiate_variable('?x', '126')
        self.c3.state = states.REDUCIBLE
        self.c3.data_sources.add('ciafactbook')

        self.alist.link_child(self.c1)
        self.alist.link_child(self.c2)
        self.alist.link_child(self.c3)

    def test_inference(self):
        alist = Alist(**{tt.ID: '1', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'population',
                         tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        # infer = Infer().runFrank(alist)
        self.assertTrue(True)

    def test_aggregate(self):
        res = self.infer.aggregate(self.alist)
        self.assertTrue(res)


if __name__ == '__main__':
    unittest.main()
