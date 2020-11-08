'''
File: logger.py
Description: 


'''

import queue
import random
import threading
import time

from frank import config
from frank.alist import Alist
# from frank.cache import neo4j, redis
# from frank.cache.redis import RedisClientPool

REDIS = 'redis'
NEO4J = 'neo4j'
class Logging:
    running = False
    write_queue = queue.Queue(maxsize=0)

    def __init__(self):
        pass

    def writelog(self):
        # 0: cache_location 1:alist, 2:parent, 4:edge, 4:sessionid
        # Logging.running = True
        # while True:
        #     if Logging.write_queue.empty():
        #         Logging.running = False
        #         break
        #     else:
        #         item = Logging.write_queue.get()
        #         if item[0] == NEO4J:
        #             try:
        #                 neo4j.create_node(item[1], item[2], item[3], item[4])
        #             except Exception as ex:
        #                 print(f"Exception ocurred when caching to neo4j: {str(ex)}")
        #         elif item[0] == REDIS:
        #             try: 
        #                 if item[1] == 'lpush':
        #                     RedisClientPool().get_client().lpush(item[3], item[4])
        #                 elif item[1] == 'mset':
        #                     RedisClientPool().get_client().mset({item[3]: item[4]})
        #                 # expiry
        #                 if item[2] == True:
        #                         RedisClientPool().get_client().expire(item[3], config.config['redis_expire_seconds'])
                        
        #             except Exception as e:
        #                     print("Exception occurred when caching to redis. " + str(e))

        return
        

    def log(self, log_item):
        # """
        # Args: Tuple (cache_location, alist, parent, edge, sessionId)
        # """
        # Logging.write_queue.put(log_item)
        # if Logging.running == False:
        #     ps = threading.Thread(target=self.writelog, args=())
        #     ps.start()
        pass

    def flush(self):
        # if Logging.running == False:
        #     ps = threading.Thread(target=self.writelog, args=())
        #     ps.start()
        pass
