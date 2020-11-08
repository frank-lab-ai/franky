'''
File: wikidata.py
Description: Interface to Wikidata


'''

from pymongo import MongoClient
from frank import config


def getClient():
    if config.config['mongo_user']:
        # login with auth
        client = MongoClient(
            host=config.config['mongo_host'],
            port=config.config['mongo_port'],
            username=config.config['mongo_user'],
            password=config.config['mongo_pwd'],
            authSource="admin",
            authMechanism='SCRAM-SHA-1')
    else:
        # login without auth
        client = MongoClient(
            host=config.config['mongo_host'],
            port=config.config['mongo_port'])

    return client
