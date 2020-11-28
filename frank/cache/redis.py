# '''
# File: redis.py
# Description:
#

# '''

# import redis
# from frank import config

# class RedisClientPool:
#     class __RedisClientPool:
#         def __init__(self):
#           self.con_pool = redis.ConnectionPool(config.config['redis_host'], config.config['redis_port'], db=0)
#         def get_client(self):
#           # return redis.Redis(connection_pool=self.con_pool)
#           return redis.Redis(host=config.config['redis_host'], port=config.config['redis_port'])
#     instance = None
#     def __init__(self):
#         if not RedisClientPool.instance:
#           print("\n\ncreate new pool instance")
#           RedisClientPool.instance = RedisClientPool.__RedisClientPool()
#     def get_client(self):
#         return self.instance.get_client()


# # print("\n\ncreate redis conn")
# # redis_pool = redis.ConnectionPool(config.config['redis_host'], config.config['redis_port'], db=0)
# # redis_conn = redis.Redis(connection_pool=redis_pool)

# # # def init():
# # #   global redis_pool
# # #   redis_pool = redis.ConnectionPool(config.config['redis_host'], config.config['redis_port'], db=0)

# # def get_client():
# #   return redis_conn
# #   # if redis_pool == None:
# #   #   init()
# #   #   return redis.Redis(connection_pool=redis_pool)
# #   # else:
# #   #   return redis.Redis(connection_pool=redis_pool)
