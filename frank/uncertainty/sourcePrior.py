'''
File: sourcePrior.py
Description: Manage prior uncertainty for knowledge sources.


'''

from datetime import datetime
import numpy as np
import pandas as pd
import math
from frank.config import config
import frank.uncertainty.sourcePrior as sourcePrior
from frank.kb import mongo
import frank.dataloader

# client = MongoClient(host=config["mongo_host"], port=config["mongo_port"])
client = mongo.getClient()
db = client[config["mongo_db"]]
collectionName = "sourcepriors"
defaultParamA = 1.0
defaultParamB = 1.0
defaultCov = 0.9  # high default cov


class SourcePrior():
    def __init__(self, source="", mean=0.0, variance=0.0, cov=0.0, lastModified=datetime.now()):
        self.source = source
        self.paramA = mean
        self.paramB = variance
        self.cov = cov
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
            df = frank.dataloader.load_source_priors()
            columns = ['source','paramA','paramB','cov','lastModified']
            data = [self.source, self.paramA, self.paramB, self.cov, self.lastModified.utcnow()]
            res = df.loc[df.source == self.source]
            if len(res) > 0:
                result = df.loc[df.source == self.source, columns] = data
            else:
                df2 = pd.DataFrame([data], columns=columns)
                df = df.append(df2, ignore_index=True)
            frank.dataloader.save_source_priors(df)
            return True

    def save_to_db(self):
        """
        Save or update the prior object
        """
        if config["update_priors"] == False or self.source == "":
            return
        # do upsert
        result = db[collectionName].update_one(
            {"source": self.source},
            {"$set": {"source": self.source, "paramA": self.paramA, "paramB": self.paramB, "cov": self.cov,
                      "lastModified": self.lastModified.utcnow()}},
            upsert=True
        )
        return result

    def get_prior(self, source: str):
        """
        Retrieve a prior object for the requested knowledge source.
        """
        if config["use_db"]:
            return self.getPrior_from_db()
        else:   
            prior = SourcePrior(source, mean=defaultParamA,
                                variance=defaultParamB, cov=defaultCov)
            df = frank.dataloader.load_source_priors()
            results = df.loc[df.source == source, 
                            ['source', 'paramA', 'paramB', 'cov']]
            if len(results) > 0:
                record = results.head().to_numpy()
                prior.source = record[0][0]
                prior.paramA = record[0][1]
                prior.paramB = record[0][2]
                prior.cov = record[0][3]
            else:
                # if no stored prior, save the default prior
                self.save()
            return prior

    def get_prior_from_db(self, source: str):
        """
        Retrieve a prior object for the requested knowledge source.
        """
        prior = SourcePrior(source, mean=defaultParamA,
                            variance=defaultParamB, cov=defaultCov)
        results = db[collectionName].find({"source": source})
        for record in results:
            prior.source = record["source"]
            prior.paramA = record["paramA"]
            prior.paramB = record["paramB"]
            prior.cov = record["cov"]

        # if no prior retrieved for the source, save the prior object
        #  containing the default values
        if results.retrieved <= 0:
            self.save()

        return prior

    def posterior(self, dataPoints, knownMean, knownVariance):
        """
        Get posterior parameters give the observed data
        """
        posteriorA = 0.0
        posteriorB = 0.0
        n = len(dataPoints)
        posteriorA = self.paramA + (n/2)

        # calculate the mean squared error
        dataY = np.array([y for (_, y) in dataPoints])
        knownMeans = np.ones(len(dataY)) * knownMean
        mse = np.square(dataY-knownMeans).mean()

        posteriorB = self.paramB + ((n/2) * mse)
        precision = posteriorA/posteriorB
        posteriorVariance = 1/precision
        # update the priors
        self.paramA = posteriorA
        self.paramB = posteriorB
        # cov = stdev/mean
        self.cov = math.sqrt(knownVariance)/knownMean
        self.save()
        return (posteriorA, posteriorB)
