from frank.alist import Alist
from frank.alist import Attributes as tt
from frank.alist import VarPrefix as vx
from frank.alist import Branching as br
from frank.alist import States as states
import unittest


class Test_Alist(unittest.TestCase):
    def test_a(self):
        self.assertTrue(True)

    def test_link_child(self):
        parent = Alist(**{tt.ID: '1', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                          tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        child = Alist(**{tt.ID: '1', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        parent.link_child(child)
        self.assertTrue(len(parent.children) > 0 and len(
            child.parent) > 0, 'parent and child count should be > 0 after linking')

    def test_getVariables(self):
        alist = Alist(**{tt.ID: '1', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        alist.set('#d', 34)
        variables = alist.variables()
        self.assertTrue(len(variables) == 3, "should have 3 items in dict")

    def test_isInstantiated2(self):
        alist = Alist(**{tt.ID: '1', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        alist.set('#d', 34)
        results = [alist.is_instantiated(tt.SUBJECT),
                   alist.is_instantiated(tt.OBJECT),
                   alist.is_instantiated('#d')]
        self.assertEqual(results, [True, False, True],
                         "should result in list [True, False, True].")

    def test_getInstantiatedAttributes(self):
        alist = Alist(**{tt.ID: '1', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        alist.set('#d', 34)
        alist.set('?x', 100)
        instantiatedVars = alist.instantiated_attributes()
        self.assertTrue(len(instantiatedVars) >0,
                        "there should be 2 instantiated variables.")

    def test_getVariableRefs(self):
        alist = Alist(**{tt.ID: '1', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        varRefs = alist.variable_references('?x')
        self.assertEqual(sorted(list(varRefs.keys())), sorted(
            [tt.OBJECT, tt.OPVAR]), "should be OBJECT and OPVAR.")

    def test_prune(self):
        parent = Alist(**{tt.ID: '1', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                          tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        child = Alist(**{tt.ID: '1', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        childB = Alist(**{tt.ID: '1', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                          tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        grandchild = Alist(**{tt.ID: '1', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
                              tt.OBJECT: '', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        parent.link_child(child)
        parent.link_child(childB)
        child.link_child(grandchild)
        child.prune()
        self.assertEqual((len(parent.children), len(child.parent), len(child.children), len(grandchild.parent)),
                         (1, 0, 0, 0), "parent should only have one child, child and grandchild should have no parents.")

    def test_instantiateVariables(self):
        alist = Alist(**{tt.ID: '1', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        alist.set('#d', '')
        alist.set('?x', '#d')
        alist.instantiate_variable('#d', 99)
        self.assertEqual(alist.get('?x'), 99, "OBJECT should be 99.")

    def test_getInstantiationValue(self):
        alist = Alist(**{tt.ID: '1', tt.SUBJECT: 'Africa', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        alist.set('#d', '')
        alist.set('?x', '#d')
        alist.set('$y', '')
        alist.instantiate_variable('#d', 99)
        results = (alist.instantiation_value('#d'), alist.instantiation_value('?x'),
                   alist.instantiation_value(
                       tt.OBJECT), alist.instantiation_value(tt.TIME),
                   alist.instantiation_value('$y'))
        self.assertEqual(results, (99, 99, 99, '2010', ''))

    def test_getNestingVars(self):
        alist = Alist(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1})
        alist.set('$y', {"$filter": [{"p": "type", "o": "country"}]})
        self.assertTrue(alist.nesting_variables())

    def test_isInstantiated(self):
        alist = Alist(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1, '$y': 'Ghana'})
        result = alist.is_instantiated(tt.SUBJECT)
        self.assertTrue(result)

    def test_getNonInstantiated(self):
        alist = Alist(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1, '$y': 'Ghana'})
        result = alist.uninstantiated_attributes()
        self.assertTrue('s' not in result)

    def test_getAlistJsonWithMetadata(self):
        alist = Alist(**{tt.ID: '1', tt.SUBJECT: '$y', tt.PROPERTY: 'P1082',
                         tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1, '$y': 'Ghana'})
        result = alist.get_alist_json_with_metadata()
        self.assertTrue('id' in result)


if __name__ == '__main__':
    unittest.main()
