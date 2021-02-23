import unittest
import json
import frank.uncertainty.sourcePrior as sourcePrior
import frank.uncertainty.propertyPrior as propertyPrior
import frank.uncertainty.aggregateUncertainty as aggregateUncertainty
from frank.alist import Alist
from frank.alist import Attributes as tt


class TestUncertainty(unittest.TestCase):
    def test_sourceprior_save_default(self):
        prior = sourcePrior.SourcePrior("testSourceA")
        prior.save()

        retrievedPrior = sourcePrior.SourcePrior().get_prior(source="testSourceA")
        self.assertTrue(retrievedPrior.source == prior.source,
                        "values must be the same")

    def test_sourceprior_save(self):
        prior = sourcePrior.SourcePrior(
            "testSourceA", mean=10.0, variance=100.0, cov=0.5)
        prior.save()

        retrievedPrior = sourcePrior.SourcePrior().get_prior(source="testSourceA")
        self.assertTrue(retrievedPrior.cov == prior.cov,
                        "values must be the same")

    def test_get_source_posterior(self):
        prior = sourcePrior.SourcePrior(
            "testSourceA", mean=10.0, variance=100.0, cov=0.5)
        data = [("A", 20.0), ("B", 25), ("C", 20), ("D", 30.0)]
        posterior = prior.posterior(data, 20.0, 100.0)
        self.assertTrue(posterior[0] > 0, "positive posterior required")

    def test_propertyprior_save_default(self):
        prior = propertyPrior.PropertyPrior("testSourceA", "propA")
        prior.save()

        retrievedPrior = propertyPrior.PropertyPrior().get_prior(
            source="testSourceA", property="propA")
        self.assertTrue(retrievedPrior.property ==
                        prior.property, "values must be the same")

    def test_propertyprior_save_dt(self):
        prior = propertyPrior.PropertyPrior(
            "testSourceA", "propA", mean=15, variance=50)
        prior.save()

        retrievedPrior = propertyPrior.PropertyPrior().get_prior(
            source="testSourceA", property="propA")
        self.assertTrue(retrievedPrior.property ==
                        prior.property, "values must be the same")

    def test_get_prop_posterior(self):
        kb_prior = sourcePrior.SourcePrior(
            "testSourceA", mean=10.0, variance=100.0)
        kb_prior.save()
        prior = propertyPrior.PropertyPrior(
            "testSourceA", "propA", mean=5.0, variance=10)
        data = [("A", 20.0), ("B", 25), ("C", 20), ("D", 30.0)]
        posterior = prior.posterior(data, knownVariance=100.0)
        self.assertTrue(posterior[0] > 0, "positive posterior required")

    def test_get_observed_estimate_value(self):
        kb_prior = sourcePrior.SourcePrior(
            "testSourceA", mean=10.0, variance=100.0)
        kb_prior.save()
        prior = propertyPrior.PropertyPrior(
            "testSourceA", "propA", mean=5.0, variance=10)
        data = [("A", 20.0), ("B", 25), ("C", 20), ("D", 30.0)]
        posterior = prior.getObservedValueEstimate(
            data, "testSourceA", "propA")
        self.assertTrue(posterior[0] > 0, "positive posterior required")

    # def test_aggregate_uncertainty(self):
    #     alist = Alist(**{tt.ID: '1', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
    #                      tt.OBJECT: '?x', tt.TIME: '2016', tt.OPVAR: '?x', tt.COST: 1, tt.COV: 0.2})
    #     c1 = Alist(**{tt.ID: '2', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
    #                   tt.OBJECT: '?x', tt.TIME: '2010', tt.OPVAR: '?x', tt.COST: 1, '?x': '', tt.COV: 0.5})
    #     c1.instantiate_variable('?x', '120')
    #     c2 = Alist(**{tt.ID: '3', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
    #                   tt.OBJECT: '?x', tt.TIME: '2011', tt.OPVAR: '?x', tt.COST: 1, '?x': '', tt.COV: 0.4})
    #     c2.instantiate_variable('?x', '122')
    #     c3 = Alist(**{tt.ID: '4', tt.SUBJECT: 'Ghana', tt.PROPERTY: 'P1082',
    #                   tt.OBJECT: '?x', tt.TIME: '2012', tt.OPVAR: '?x', tt.COST: 1, '?x': '', tt.COV: 0.1})
    #     c3.instantiate_variable('?x', '126')
    #     alist.(c1)
    #     alist.link_child(c2)
    #     alist.link_child(c3)

    #     confidence = aggregateUncertainty.estimate_uncertainty(
    #         alist.children, all_numeric=True, operation=alist.get(tt.OP), child_count=len(alist.children))
    #     self.assertTrue(confidence > 0, "confidence value must be positive")


if __name__ == "__main__":
    unittest.main()
