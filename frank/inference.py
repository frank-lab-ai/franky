'''
File: inference.py
Description: Core functions to the FRANK algorithm
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)

'''

import datetime
import random
import threading
import time
from heapq import heappop, heappush

import frank.cache.logger as clogger
import frank.cache.neo4j
import frank.map.map_wrapper
import frank.processLog
import frank.reduce.comp
import frank.reduce.eq
import frank.reduce.gpregress
import frank.reduce.gt
import frank.reduce.gte
import frank.reduce.lt
import frank.reduce.lte
import frank.reduce.max
import frank.reduce.mean
import frank.reduce.min
import frank.reduce.mode
import frank.reduce.nnpredict
import frank.reduce.product
import frank.reduce.regress
import frank.reduce.sum
import frank.reduce.value
import frank.reduce.values
from frank.util import utils
from frank.alist import Alist
from frank.alist import Attributes as tt
from frank.alist import Branching as br
from frank.alist import NodeTypes as nt
from frank.alist import States as states
from frank import config
from frank.kb import rdf, wikidata, worldbank
from .explain import Explanation
from frank import processLog
from frank.uncertainty.sourcePrior import SourcePrior as sourcePrior
import frank.context
from frank.graph import InferenceGraph


class Execute:

    def __init__(self, G:InferenceGraph):
        self.G = G
        self.trace = ''
        self.session_id = '0'
        self.last_heartbeat = time.time()
        # self.nodes_queue = []
        # self.wait_queue = []
        self.property_refs = {}
        self.reverse_property_refs = {}
        self.graph_nodes = []
        self.graph_edges = []
        self.has_temp_answer = False
        self.max_depth_process_so_far = 0
        self.answer_propagated_to_root = []
        self.root = None
        self.explainer = Explanation()

    def enqueue_root(self, alist):
        self.root = alist
        self.enqueue_node(alist, None, True, '')
        self.G.add_alist(alist)

    def enqueue_node(self, alist: Alist, parent: Alist, to_be_processed: bool, decomp_rule: str):
        try:
            # if to_be_processed:
            #     heappush(self.nodes_queue, (alist.cost, alist,
            #                                 parent, to_be_processed, decomp_rule))
            self.graph_nodes.append(alist)
            if parent is not None:
                self.graph_edges.append((parent.id, alist.id))
            # # update the trace store
            # clogger.Logging().log(
            #     (clogger.REDIS, 'lpush', True, self.session_id + ':graphNodes', str(alist)))
            # if parent:
            #     clogger.Logging().log(('redis', 'lpush', True,
            #                            self.session_id +
            #                            ':graphEdges', str(alist),
            #                            '{{"source":"{}", "target":"{}" }}'.format(parent.id, alist.id)))
            # self.write_graph(alist, parent=parent, edge=decomp_rule)
            # self.G.link(parent, alist, decomp_rule)
        except Exception:
            print("Exception occurred when adding node to queue")

    def run_frank(self, alist: Alist):
        '''
        For the given alist, attempt to instantiate projection variable
        If instantiation is successful, attempt to reduce
        Else decompose and add new children to queue
        '''
        self.last_heartbeat = time.time()
        propagated_to_root = False
        self.max_depth_process_so_far = alist.depth
        if alist.state is states.PRUNED:
            self.write_trace("ignore pruned:>> {}-{}".format(alist.id, alist))
            return propagated_to_root

        bool_result = False
        # check if OPVAR is instantiated
        # if OPVAR is instantiated, set bool_result to TRUE
        # if alist.is_instantiated(alist.get(tt.OPVAR)):
        #     bool_result = True
        # if the the projection vars are already instantiated
        #   then make the alist reducible and return True
        proj_vars = alist.projection_variables()
        proj_instantiated = True
        if proj_vars:
            for p, _ in proj_vars.items():
                proj_instantiated = proj_instantiated and alist.is_instantiated(
                    p)

        agg_vars = alist.get(tt.OPVAR).split(' ')
        agg_instantiated = True
        if agg_vars:
            for v in agg_vars:
                agg_instantiated = agg_instantiated and alist.is_instantiated(
                    v)
            if agg_instantiated:
                bool_result = True

        if bool_result:
            alist.state = states.REDUCIBLE
            self.write_trace_reduced(alist)  # to change state in cache
        # if OPVAR not instantiated, search KB
        elif not bool_result:
            bool_result = self.search_kb(alist)
        # search kb for the variable instantiation

        if bool_result:
            if alist.state != states.REDUCIBLE:  # if in reducible state, don't change
                alist.state = states.EXPLORED
                self.G.add_alist(alist)
            if agg_instantiated and proj_instantiated:
                alist.state = states.REDUCIBLE
                self.G.add_alist(alist)
            if self.G.child_ids(alist.id):
                propagated_to_root = self.propagate(self.G.child_ids(alist.id)[0])
            else:
                propagated_to_root = self.propagate(
                    self.G.child_ids(self.G.parent_ids(alist.id)[0])[0])

            if propagated_to_root:
                prop_alist = self.G.alist(self.root.id)
                self.write_trace("intermediate ans:>> {}-{}".format(
                    prop_alist.id, prop_alist), loglevel=processLog.LogLevel.ANSWER)
                self.answer_propagated_to_root.append(prop_alist.copy())
        else:
            alist.state = states.EXPLORED
            self.G.add_alist(alist)
            for mapOp in self.get_map_strategy(alist):
                self.decompose(alist, mapOp)
        return propagated_to_root

    def search_kb(self, alist: Alist):
        self.last_heartbeat = time.time()
        self.write_trace("search:>>{} {}".format(alist.id, alist))
        if alist.state == states.EXPLORED:
            new_alist = alist.copy()
            new_alist.state = states.EXPLORED
            new_alist.set(tt.OPVAR, alist.get(tt.OPVAR))
            return True
        
        prop_string = alist.get(tt.PROPERTY)
        prop_refs = []
        found_facts = []
        for source_name, source in {'wikidata':wikidata, 'worldbank':worldbank}.items():
        # for source_name, source in {'worldbank':worldbank}.items():
            search_alist = alist.copy()
            # inject context into IR
            search_alist = frank.context.inject_retrieval_context(search_alist, source_name)
            
            # if the property_refs does not contain an entry for the property in this alist
            # search KB for a ref for the property
            prop_sources = []
            if prop_string in self.property_refs:
                prop_sources = [x[1] for x in self.property_refs[prop_string]]

            if (prop_string not in self.property_refs and not prop_string.startswith('__') ) \
                or (prop_string in self.property_refs and source_name not in prop_sources):

                props = source.search_properties(prop_string)
                
                if len(props) > 0:             
                    maxScore = 0
                    for p in props:
                        if p[2] >= maxScore:
                            prop_refs.append((p, source_name))
                            self.reverse_property_refs[p[0]] = prop_string
                            maxScore = p[2]
                        else:
                            break
                self.property_refs[prop_string] = prop_refs

            
            search_attr = tt.SUBJECT
            uninstantiated_variables = search_alist.uninstantiated_attributes()
            if tt.SUBJECT in uninstantiated_variables:
                search_attr = tt.SUBJECT
            elif tt.OBJECT in uninstantiated_variables:
                search_attr = tt.OBJECT

            cache_found_flag = False
            if config.config['use_cache']:
                searchable_attr = list(filter(lambda x: x != search_attr,
                                            [tt.SUBJECT, tt.PROPERTY, tt.OBJECT, tt.TIME]))
                # search with original property name
                (cache_found_flag, results) = frank.cache.neo4j.search_cache(alist_to_instantiate=search_alist,
                                                                        attribute_to_instantiate=search_attr,
                                                                        search_attributes=searchable_attr)
                if cache_found_flag == True:
                    found_facts.append(results[0])
                # search with source-specific property IDs

                for (propid, _source_name) in self.property_refs[prop_string]:
                    self.last_heartbeat = time.time()
                    search_alist.set(tt.PROPERTY, propid[0])
                    (cache_found_flag, results) = frank.cache.neo4j.search_cache(alist_to_instantiate=search_alist,
                                                                            attribute_to_instantiate=search_attr,
                                                                            search_attributes=searchable_attr)
                    if cache_found_flag == True:
                        found_facts.append(results[0])
                        self.write_trace('found:>>> cache')
                # if not found_facts:
                #     self.write_trace('found:>>> cache')
            if not cache_found_flag and prop_string in self.property_refs:
                # search for data for each property reference source
                for propid_label, _source_name in self.property_refs[prop_string]:
                    self.last_heartbeat = time.time()
                    
                    try:
                        if _source_name == source_name:
                            search_alist.set(tt.PROPERTY, propid_label[0])
                            found_facts.extend(source.find_property_values(
                                    search_alist, search_attr))
                            # TODO: handle location search in less adhoc manner
                            if alist.get(tt.PROPERTY).lower() == "location":
                                if search_attr == tt.SUBJECT:
                                    found_facts.extend(
                                        wikidata.part_of_relation_subject(search_alist))
                                elif search_attr == tt.OBJECT:
                                    found_facts.extend(
                                        wikidata.part_of_relation_object(search_alist))
                            break
                    except Exception as ex:
                        self.write_trace("Search Error", processLog.LogLevel.ERROR)
                        print(str(ex))
            if not found_facts and alist.get(tt.PROPERTY).startswith('__geopolitical:'):
                if search_attr == tt.SUBJECT:
                    found_facts.extend(
                        wikidata.part_of_geopolitical_subject(search_alist))
            # TODO: save facts found to cache if caching is enabled
            # if foundFacts and config.config['use_cache']:
            #     for ff in foundFacts:
            #         cache().save(ff, ff.dataSources[0])

        if found_facts:
            self.last_heartbeat = time.time()
            all_numeric = True
            non_numeric_data_items = []
            numeric_data_items = []

            for ff in found_facts:
                self.last_heartbeat = time.time()
                if utils.is_numeric(ff.get(search_attr)):
                    numeric_data_items.append(
                        utils.get_number(ff.get(search_attr), 0.0))
                else:
                    all_numeric = False
                    non_numeric_data_items.append(ff.get(search_attr))
                ff.set(tt.OPVAR, alist.get(tt.OPVAR))
                ff.set(ff.get(tt.OPVAR), ff.get(search_attr))
                sourceCov = sourcePrior().getPrior(
                    source=list(ff.data_sources)[0]).cov
                ff.set(tt.COV, sourceCov)
                ff.state = states.REDUCIBLE
                ff.set(tt.EXPLAIN, '')
                ff.node_type = nt.FACT
                if ff.get(tt.PROPERTY) in self.reverse_property_refs:
                    ff.set(tt.PROPERTY,
                           self.reverse_property_refs[ff.get(tt.PROPERTY)])
                # alist.link_child(ff)
                self.G.link(alist, ff,alist.parent_decomposition)
                alist.parent_decomposition = "Lookup"
                self.enqueue_node(ff, alist, False, 'Lookup')
                # self.add_reduced_alist_to_redis(ff) # leaf node from retrieved
                # fact is considered reduced
                self.write_trace(' found:>>> {}'.format(str(ff)))
        return len(found_facts) > 0

    def get_map_strategy(self, alist: Alist):
        # TODO: learn to predict best strategy given path of root from
        # node and attributes in alist
        self.last_heartbeat = time.time()
        if alist.get(tt.OP).lower() in ['eq', 'lt', 'gt', 'lte', 'gte']:
            return [(frank.map.map_wrapper.get_mapper_fn("comparison"), "comparison")]
        # if compound frame (i.e nesting point in frame), then normalize
        elif alist.uninstantiated_nesting_variables():
            return [(frank.map.map_wrapper.get_mapper_fn("normalize"), "normalize")]
        else:
            ops = []
            for allowed_op in config.config["base_decompositions"]:
                try:
                    ops.append(
                        (frank.map.map_wrapper.get_mapper_fn(allowed_op), allowed_op))
                except Exception as ex:
                    print("Error in decomposition mapper: " + str(ex))
            random.shuffle(ops)
            return ops

    def decompose(self, alist: Alist, mapOp):
        self.last_heartbeat = time.time()
        if alist.depth + 1 > config.config['max_depth']:
            print('max depth reached!\n')
            alist.state = states.IGNORE
            return alist

        self.write_trace('T{thread} > {op}:{id}-{alist}'.format(
            thread=threading.get_ident(), op=mapOp[1], alist=alist, id=alist.id))
        alist.branchType = br.OR
        child = mapOp[0](alist, self.G)
        # check for query context
        context = alist.get(tt.CONTEXT)
        # if child and context:            
        #     # do no assume child query context is the same as parent
        #     child.set(tt.CONTEXT, [context[0], context[1],{}])
        #     frank.context.inject_query_context(child)
        self.last_heartbeat = time.time()
        if child is not None:
            # child.node_type = nt.HNODE
            self.write_trace('>> {}-{}'.format(child.id, str(child)))
            # self.write_graph(child, parent=alist, edge=mapOp[1])
        #     if child.state != states.EXPLORED:
        #         child.parent_decomposition = mapOp[1]
        #         heappush(self.wait_queue, (child.cost,
        #                                    child, alist, False, mapOp[1]))

        #     for grandchild in child.children:
        #         # grandchild.node_type = nt.ZNODE
        #         grandchild.set(tt.CONTEXT, child.get(tt.CONTEXT))
        #         self.write_graph(grandchild, parent=child, edge=mapOp[1])
        #         self.write_trace(
        #             '>>> {}-{}'.format(grandchild.id, str(grandchild)))
        #         if grandchild.state != states.EXPLORED:
        #             heappush(self.wait_queue, (grandchild.cost,
        #                                        grandchild, child, True, mapOp[1]))
        #         reducibleCtr = 0
        #         for ggc in grandchild.children:
        #             ggc.node_type = nt.ZNODE
        #             ggc.set(tt.CONTEXT, child.get(tt.CONTEXT))
        #             self.write_graph(ggc, parent=grandchild, edge=mapOp[1])
        #             self.write_trace('>>>> {}-{}'.format(ggc.id, str(ggc)))
        #             if ggc.state == states.REDUCIBLE:
        #                 if reducibleCtr == 0:
        #                     heappush(self.nodes_queue, (ggc.cost,
        #                                                 ggc, grandchild, False, mapOp[1]))
        #                 # self.enqueue_node(ggc, grandchild, False, mapOp[1])
        #                 self.write_trace_reduced(ggc)
        #                 reducibleCtr += 1
        #             elif ggc.state != states.EXPLORED:
        #                 heappush(self.wait_queue, (ggc.cost,
        #                                            ggc, grandchild, True, mapOp[1]))
        #     # generate the WHY explanation
            succ  = self.G.successors(child.id)
            for node_id1 in succ:
                grandchild = self.G.alist(node_id1)
                self.write_trace(
                    '>>> {}-{}'.format(grandchild.id, str(grandchild)))
                # if grandchild.state != states.EXPLORED:
                #     heappush(self.wait_queue, (grandchild.cost,
                #                                grandchild, child, True, mapOp[1]))
                
                reducibleCtr = 0
                succ2  = self.G.successors(grandchild.id)
                for node_id2 in succ2:
                    ggchild = self.G.alist(node_id2)
                    self.write_trace(
                        '>>> {}-{}'.format(ggchild.id, str(ggchild)))
                    if ggchild.state == states.REDUCIBLE:
                    #     if reducibleCtr == 0:
                    #         heappush(self.nodes_queue, (ggchild.cost,
                    #                                     ggchild, grandchild, False, mapOp[1]))
                        # self.enqueue_node(ggc, grandchild, False, mapOp[1])
                        self.write_trace_reduced(ggchild)
                        reducibleCtr += 1
                    # elif ggchild.state != states.EXPLORED:
                    #     heappush(self.wait_queue, (ggchild.cost,
                    #                                 ggchild, grandchild, True, mapOp[1]))

            # self.explainer.why(alist, mapOp[1])
            return child
        else:
            return None

    def aggregate(self, alist_id):
        alist = self.G.alist(alist_id)
        self.last_heartbeat = time.time()
        self.write_trace('reducing:>><< {}-{}'.format(alist.id, alist))

        reduce_op = None
        try:
            reduce_op = eval('frank.reduce.' + alist.get(tt.OP).lower())
        except:
            print(f"Cannot process {alist.get(tt.OP).lower()}")

        assert(reduce_op is not None)
        
        children = self.G.child_alists(alist.id)
        reducibles = [x for x in children
                      if (x.state == states.REDUCIBLE or x.state == states.REDUCED) 
                          and x.get(tt.OP).lower() != 'comp']
        for x in reducibles:
            self.write_trace('  <<< {}-{}'.format(x.id, x))

        unexplored = [
            x for x in children if x.state == states.UNEXPLORED]
        if not reducibles or len(unexplored) == len(children):
            return False  # there's nothing to reduce

        reducedAlist = reduce_op.reduce(alist, reducibles, self.G)

        last_heartbeat = time.time()

        if reducedAlist is not None:
            for c in children:
                alist.data_sources = list(set(alist.data_sources + c.data_sources))
            for r in reducibles:
                r.state = states.REDUCED
                self.G.add_alist(r)
            alist.state = states.REDUCIBLE

            # these are there for the COMP operation that creates new nodes
            # after reducing
            for n in alist.nodes_to_enqueue_only:
                self.enqueue_node(n[0], n[1], n[2], n[3])
            # in a reducer generated new node, then they MUST be processed immediately,
            # so place in nodesQueue, not waitQueue
            for n in alist.nodes_to_enqueue_and_process:
                self.enqueue_node(n[0], n[1], n[2], n[3])
            # clear nodes to enqueue to prevent reuse if node is cloned to
            # create child nodes
            alist.nodes_to_enqueue_only.clear()
            alist.nodes_to_enqueue_and_process.clear()
            self.G.add_alist(alist)
            # self.explainer.what(alist, True)
            self.write_trace_reduced(alist)
            self.write_trace("reduced:<< {}-{}".format(alist.id, alist))
            return True
        else:
            # self.explainer.what(alist, False)
            self.write_trace("reduce failed:<< {}-{}".format(alist.id, alist))
            return False

    def propagate(self, alist_id):
        self.last_heartbeat = time.time()
        curr_alist = self.G.alist(alist_id)
        self.write_trace('^^ {}-{}'.format(curr_alist.id, curr_alist))
        try:
            while self.G.parent_ids(curr_alist.id):
                # get the parent alist and apply its reduce operation to its
                # children
                if self.aggregate(self.G.parent_ids(curr_alist.id)[0]):
                    # set the parent to the current alist and recurse up the
                    # tree
                    curr_alist = self.G.parent_alists(curr_alist.id)[0]
                else:
                    return False
        except Exception as e:
            self.write_trace("Error during propagation: " +
                             str(e), processLog.LogLevel.ERROR)
            return False
        return True

    def write_trace_reduced(self, alist: Alist):
        # clogger.Logging().log(('redis', ',mset', True, '{}:alist:{}'.format(
        #     self.session_id, alist.id), str(alist)))
        # self.write_graph(alist)
        self.G.add_alist(alist)

    def write_trace(self, content, loglevel=processLog.LogLevel.INFO):
        processLog.println(content, processLog.LogLevel.INFO)
        # if(loglevel <= processLog.baseLogLevel):
        #     # save log to redis store
        #     clogger.Logging().log(('redis', 'lpush', False,  self.session_id + ':trace', content))

    def write_graph(self, alist: Alist, parent: Alist = None, edge: str = None):
        # clogger.Logging().log(('neo4j', alist, parent, edge, self.session_id))
        # if parent:
        #     self.G.add_alist(parent)
        #     self.G.link(parent, alist, edge)
        # else:
        #     self.G.add_alist(alist)
        pass