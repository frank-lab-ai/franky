'''
File: scheduler.py
Description: 
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)

'''
import time
import timeit
import uuid
import json
import threading
from frank.infer import Infer

from frank.alist import Alist
from frank.alist import Attributes as tt
from frank.alist import States as states
from frank.alist import Branching as branching
from frank import config
from frank.util import utils
from frank.graph import InferenceGraph
import frank.context

class Launcher():

    def __init__(self, **kwargs):
        self.frank_infer: Infer = None
        self.timeout = 60  # self.timeout in seconds
        self.start_time = time.time()
        self.inference_graphs = {}

    def start(self, alist: Alist, session_id, inference_graphs):
        ''' Create new inference graph and infer'''
        G = InferenceGraph()
        self.frank_infer = Infer(G)
        self.frank_infer.session_id = session_id
        self.inference_graphs = inference_graphs
        self.start_time = time.time()
        self.frank_infer.last_heartbeat = time.time()
        print(f"session-id: {self.frank_infer.session_id}")
        alist = frank.context.inject_query_context(alist)
        self.frank_infer.enqueue_root(alist)
        self.schedule(-1)

    def start_for_api(self, alist_obj, session_id, inference_graphs):

        a = Alist(**alist_obj)
        t = threading.Thread(target=self.start, args=(a, session_id, inference_graphs))
        t.start()
        return session_id

    def schedule(self, last_root_prop_depth):
        if time.time() - self.frank_infer.last_heartbeat > self.timeout:
            # stop and print any answer found
            self.cache_and_print_answer(True)
        
        max_prop_depth_diff = 1
        stop_flag = False
        while True:
            if self.frank_infer.session_id in self.inference_graphs:
                self.inference_graphs[self.frank_infer.session_id]['graph'] = self.frank_infer.G
            else:
                self.inference_graphs[self.frank_infer.session_id] = {
                    'graph': self.frank_infer.G, 
                    'intermediate_answer': None,
                    'answer': None,
                }
            flag = False
            # first check if there are any leaf nodes that can be reduced
            reducible = self.frank_infer.G.frontier(state=states.REDUCIBLE, update_state=False)
            if reducible:
                propagatedToRoot = self.frank_infer.run_frank(reducible[0])
                if propagatedToRoot:
                    self.cache_and_print_answer(False)                    
                    flag = True
                
            if not flag:
                # check if there are any unexplored leaf nodes
                unexplored = self.frank_infer.G.frontier(state=states.UNEXPLORED)
                if unexplored and last_root_prop_depth > 0 and (unexplored[0].depth > last_root_prop_depth + max_prop_depth_diff):
                    stop_flag = True
                    break
                if unexplored:
                    propagatedToRoot = self.frank_infer.run_frank(unexplored[0])
                    if propagatedToRoot:
                        last_root_prop_depth = unexplored[0].depth
                        self.cache_and_print_answer(False)
                        flag = True            
            if not flag:
                break  

        if stop_flag:
            self.cache_and_print_answer(True)   
        else:
            # if no answer has been propagated to root and        
            if time.time() - self.frank_infer.last_heartbeat <= self.timeout:
                time.sleep(3)
            
            if self.frank_infer.G.frontier(update_state=False):
                self.schedule(last_root_prop_depth)
            else:
                # stop and print any answer found
                self.cache_and_print_answer(True)


    def cache_and_print_answer(self, isFinal=False):
        elapsed_time = time.time() - self.start_time
        answer = 'No answer found'
        

        if self.frank_infer.propagated_alists:
            latest_root = self.frank_infer.propagated_alists[-1]

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
                       "alist": self.frank_infer.propagated_alists[-1].attributes
                       }
            
            self.inference_graphs[self.frank_infer.session_id] = {
                'graph': self.frank_infer.G, 
                'intermediate_answer': ans_obj,
                'answer': ans_obj if isFinal else None,
            }

            # if isFinal:
            #     RedisClientPool().get_client().lpush(
            #         self.frank_infer.session_id + ':answer',  json.dumps(ans_obj))
            # else:
            #     RedisClientPool().get_client().set(self.frank_infer.session_id +
            #                                        ':partialAnswer',  json.dumps(ans_obj))
            # RedisClientPool().get_client().expire(
            #     self.frank_infer.session_id + ':answer', config.config['redis_expire_seconds'])
            if isFinal:
                print(json.dumps(ans_obj, indent=2))


if __name__ == '__main__':
    # prediction
    launcher = Launcher()
    session_id = uuid.uuid4().hex
    launcher.start(b, session_id)
