'''
File: scheduler.py
Description: 
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)

'''
import time
import threading
import timeit
import uuid
import json
import threading
from heapq import heappush, heappop
from frank.inference import Execute

from frank.alist import Alist
from frank.alist import Attributes as tt
from frank.alist import States as states
from frank.alist import Branching as branching
from frank import config
from frank.util import utils
from frank.graph import InferenceGraph

from frank.cache.redis import RedisClientPool
import frank.context

class Launcher():

    def __init__(self, **kwargs):
        self.frank_exec: Execute = None
        self.timeout = 60  # self.timeout in seconds
        self.start_time = time.time()

    def start(self, alist: Alist, session_id):
        ''' Create new inference graph and execute'''
        G = InferenceGraph()
        self.frank_exec = Execute(G)
        self.frank_exec.session_id = session_id
        self.start_time = time.time()
        self.frank_exec.last_heartbeat = time.time()
        print(f"session-id: {self.frank_exec.session_id}")
        alist = frank.context.inject_query_context(alist)
        self.frank_exec.enqueue_root(alist)
        self.schedule()

    def start_for_api(self, alist_obj, session_id):

        a = Alist(**alist_obj)
        t = threading.Thread(target=self.start, args=(a, session_id))
        t.start()
        return session_id

    def schedule(self):
        if time.time() - self.frank_exec.last_heartbeat > self.timeout:
            # stop and print any answer found
            self.cache_and_print_answer(True)

        
        while True:
            flag = False
            # first check if there are any leaf nodes that can be reduced
            reducible = self.frank_exec.G.frontier(state=states.REDUCIBLE, update_state=False)
            if reducible:
                propagatedToRoot = self.frank_exec.run_frank(reducible[0])
                if propagatedToRoot:
                    self.cache_and_print_answer(False)
                    flag = True
                
            if not flag:
                # check if there are any unexplored leaf nodes
                unexplored =self.frank_exec.G.frontier(state=states.UNEXPLORED)
                if unexplored:
                    propagatedToRoot = self.frank_exec.run_frank(unexplored[0])
                    if propagatedToRoot:
                        self.cache_and_print_answer(False)
                        flag = True;
            
            if not flag:
                break
            

        # if no answer has been propagated to root and        
        if time.time() - self.frank_exec.last_heartbeat <= self.timeout:
            time.sleep(3)
        
        if self.frank_exec.G.frontier(update_state=False):
            self.schedule()
        else:
            # stop and print any answer found
            self.cache_and_print_answer(True)

        # while self.frank_exec.nodes_queue:
        #     # TODO: setup concurrency
        #     propagatedToRoot = self.frank_exec.run_frank(
        #         heappop(self.frank_exec.nodes_queue)[1])
        #     if propagatedToRoot:
        #         self.cache_and_print_answer(False)

        # else if no answer has been propagated to root and
        # if not self.frank_exec.answer_propagated_to_root and self.frank_exec.wait_queue:
        #     # if self.frank_exec.wait_queue:
        #     while self.frank_exec.wait_queue:
        #         n = heappop(self.frank_exec.wait_queue)
        #         self.frank_exec.enqueue_node(n[1], n[2], n[3], n[4])
        #         # heappush(self.frank_exec.nodes_queue, heappop(self.frank_exec.wait_queue))
        # elif time.time() - self.frank_exec.last_heartbeat <= self.timeout:
        #     time.sleep(3)

        # if items to be processed in nodes_queue
        # if self.frank_exec.nodes_queue:
        #     self.schedule()
        # else:
        #     # stop and print any answer found
        #     self.cache_and_print_answer(True)

    def cache_and_print_answer(self, isFinal=False):
        elapsed_time = time.time() - self.start_time
        answer = 'No answer found'
        if self.frank_exec.answer_propagated_to_root:
            latest_root = self.frank_exec.answer_propagated_to_root[-1]

            # get projection variables from the alist
            # only one projection variable can be used as an alist
            projVars = latest_root.projection_variables()
            if projVars:
                for pvkey, pv in projVars.items():
                    answer = latest_root.instantiation_value(pvkey)

            # if no projection variables exist, then use aggregation variable as answer
            else:
                answer = latest_root.instantiation_value(
                    latest_root.get(tt.OPVAR))

            try:
                if utils.is_numeric(answer):
                    answer = utils.to_precision(
                        answer,  int(config.config["answer_sigdig"]))
            except Exception:
                pass

            # format error bar
            errorbar = 0.0
            try:
                errorbar = utils.get_number(latest_root.get(
                    tt.COV), 0) * utils.get_number(answer, 0)
                errorbar_sigdig = utils.to_precision(
                    errorbar, int(config.config["errorbar_sigdig"]))
            except Exception:
                pass
            ans_obj = {"answer": f"{answer}",
                       "error_bar": f"{errorbar_sigdig}",
                       "sources": f"{','.join(list(latest_root.data_sources))}",
                       "elapsed_time": f"{round(elapsed_time)}s",
                       "alist": self.frank_exec.answer_propagated_to_root[-1].attributes
                       }

            if isFinal:
                RedisClientPool().get_client().lpush(
                    self.frank_exec.session_id + ':answer',  json.dumps(ans_obj))
            else:
                RedisClientPool().get_client().set(self.frank_exec.session_id +
                                                   ':partialAnswer',  json.dumps(ans_obj))
            RedisClientPool().get_client().expire(
                self.frank_exec.session_id + ':answer', config.config['redis_expire_seconds'])
            if isFinal:
                print(json.dumps(ans_obj, indent=2))


if __name__ == '__main__':
    # prediction
    launcher = Launcher()
    session_id = uuid.uuid4().hex
    launcher.start(b, session_id)
