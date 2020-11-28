'''
File: propertyPrior.py
Description: Manage prior uncertainty for properties (or relations)


'''

from datetime import datetime
import numpy as np
import pandas as pd
import math
import statistics
from frank.config import config
import frank.uncertainty.sourcePrior as sourcePrior
from frank.kb import mongo
import frank.dataloader

# client = MongoClient(host=config["mongo_host"], port=config["mongo_port"])
client = mongo.getClient()
db = client[config["mongo_db"]]
collectionName = "predicatepriors"
defaultMean = 1e7
defaultVariance = math.pow(1e7, 2)


class PropertyPrior():
    def __init__(self, source="", property="", mean=0.0, variance=0.0,
                 lastModified=datetime.now()):
        self.source = source
        self.property = property
        self.mean = mean
        self.variance = variance
        self.lastModified = lastModified

    def save(self):
        """
        Save or update the prior object
        """
        if config["update_priors"] == False or self.source == "":
            return
        if config["use_db"]:
            return self.save_to_db()
        else:
            df = frank.dataloader.load_predicate_priors()
            columns = ['source', 'predicate',
                       'mean', 'variance', 'lastModified']
            data = [self.source, self.property, self.mean,
                    self.variance, self.lastModified.utcnow()]
            res = df.loc[(df.source == self.source) &
                         (df.predicate == self.property)]
            if len(res) > 0:
                result = df.loc[(df.source == self.source) & (df.predicate == self.property),
                                columns] = data
            else:
                df2 = pd.DataFrame([data], columns=columns)
                df = df.append(df2, ignore_index=True)
            frank.dataloader.save_predicate_priors(df)
            return True

    def save_to_db(self):
        """
        Save or update the prior object
        """
        if config["update_priors"] == False or self.source == "":
            return
        # do upsert
        result = db[collectionName].update_one(
            {"source": self.source, "predicate": self.property},
            {"$set": {"source": self.source, "predicate": self.property,
                      "mean": self.mean, "variance": self.variance,
                      "lastModified": self.lastModified.utcnow()}},
            upsert=True
        )
        return result

    def get_prior(self, source: str, property: str):
        """
        Retrieve a prior object for the requested knowledge source.
        """
        if config["use_db"]:
            return self.getPrior_from_db()
        else:
            prior = PropertyPrior(
                source, property, mean=defaultMean, variance=defaultVariance)
            df = frank.dataloader.load_predicate_priors()
            results = df.loc[(df.source == source) & (df.predicate == property),
                             ['source', 'mean', 'variance']]
            if len(results) > 0:
                record = results.head().to_numpy()
                prior.source = record[0][0]
                prior.mean = record[0][1]
                prior.variance = record[0][2]
            else:
                # if no stored prior, save the default prior
                self.save()
            return prior

    def get_prior_from_db(self, source: str, property: str):
        """
        Retrieve a prior object for the requested knowledge source.
        """
        prior = PropertyPrior(
            source, property, mean=defaultMean, variance=defaultVariance)
        results = db[collectionName].find(
            {"source": source, "predicate": property})
        for record in results:
            prior.source = record["source"]
            prior.mean = record["mean"]
            prior.variance = record["variance"]

        # if no prior retrieved for the source, save the prior object
        #  containing the default values
        if results.retrieved <= 0:
            self.save()

        return prior

    def posterior(self, dataPoints, knownVariance):
        """
        Get posterior parameters given the observed data
        """
        priorVariance = self.variance
        posteriorMean = 0.0
        posteriorVariance = 0.0
        n = len(dataPoints)
        dataY = [y for (_, y) in dataPoints]
        mlMean = statistics.mean(dataY)
        posteriorMean = mlMean

        dataVariance = 0.0
        if len(dataY) >= 2:
            dataVariance = statistics.variance(dataY)

        posteriorVariance = 1.0 / \
            ((1.0/priorVariance) + (n/(knownVariance + dataVariance)))

        # update the priors
        self.mean = posteriorMean
        self.variance = posteriorVariance
        self.save()
        return (self.mean, self.variance)

    def getObservedValueEstimate(self, dataPoints, source, property):
        # get the source predicate prior
        self = PropertyPrior().get_prior(source, property)
        kbPrior = sourcePrior.SourcePrior().get_prior(source)
        estimatedMeanVariance = None
        n = len(dataPoints)
        dataY = [y for (_, y) in dataPoints]
        mlMean = statistics.mean(dataY)

        assumedKnownVariance = math.pow(kbPrior.cov * mlMean, 2)

        # if this is the first time predicate is being observed in the source,
        # then use the source prior as the prior variance for the source-predicate variance,
        # and then use the mean of the observed values as the mean of the prior mean.
        # update the source-predicate prior
        # else if the predicate already has a source-property prior entry,
        # then use the Gaussian params to estimate posterior mean and variance

        # if spp != None:
        estimatedMeanVariance = self.posterior(
            dataPoints, assumedKnownVariance)

        # update the source priors
        kbPrior.posterior(
            dataPoints, knownMean=estimatedMeanVariance[0], knownVariance=estimatedMeanVariance[1])
        return estimatedMeanVariance
