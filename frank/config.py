#server config
server = {
    "frank_port": 9876,
    "mongo_host": "mongo",
    "mongo_port": 27017,
    "mongo_user": "",
    "mongo_pwd": "",
    "mongo_db": "frank",
    "redis_host": "redis",
    "redis_port": 6379,
    "redis_expire_seconds": 3600,
    "neo4j_host": "neo4j",
    "neo4j_port": 7687,
    "neo4j_username": "neo4j",
    "neo4j_password":"@neo4j123",
    "max_depth": 20,
    "update_priors": True,
    "update_priors2": True,
    "use_cache" : False,

    "visualize" : False,
    "polynomial_degree" : 1,
    "sparql_endpoint": "http://172.20.0.1:8890/sparql",
    "thread_pool" : 1,
    "log_level" : 10,
    "answer_sigdig" : 4,
    "errorbar_sigdig" : 2,
    "launch_as" : "server",
    "temporal_branching_factor": 10,
    # decompositions allowed. 'normalize' is enabled by default. Options: [temporal, geospatial, isa]
    "base_decompositions": ["temporal","geospatial"],
    "derived_decompositions": {
        "geospatial" : ["join", ["isa", "partition"]],
        "product": ["join", ["isa", "feature"] ]
    }
}

# local config
local = {
    "frank_port": 9876,
    "mongo_host": "localhost",
    "mongo_port": 27017,
    "mongo_user": "",
    "mongo_pwd": "",
    "mongo_db": "frank",
    "redis_host": "localhost",
    "redis_port": 6379,
    "redis_expire_seconds": 3600,
    "neo4j_host": "localhost",
    "neo4j_port": 7687,
    "neo4j_username": "neo4j",
    "neo4j_password":"@neo4j123",
    "max_depth": 20,
    "update_priors": True,
    "update_priors2": True,
    "use_cache" : False,

    "visualize" : False,
    "polynomial_degree" : 1,
    "sparql_endpoint": "http://frank-qa.nuamah.com:8890/sparql",
    "thread_pool" : 1,
    "log_level" : 10,
    "answer_sigdig" : 4,
    "errorbar_sigdig" : 2,
    "launch_as" : "server",
    "temporal_branching_factor": 10,
    # decompositions allowed. 'normalize' is enabled by default. Options: [temporal, geospatial, isa]
    "base_decompositions": ["temporal"],
    "derived_decompositions": {
        "geospatial" : ["join", ["isa", "partition"]],
        "product": ["join", ["isa", "feature"] ]
    }
}

# set to local or server
config = local 