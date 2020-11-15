'''
File: inference.py
Description: Core functions to the FRANK algorithm


'''

import datetime
import random
import threading
import time

import frank.cache.logger as clogger
import frank.map.map_wrapper
import frank.processLog as plog
from frank.processLog import pcolors as pcol
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
from frank.alist import Contexts as ctx
from frank.graph import InferenceGraph


class Infer:
    """ 
    Resolve alists by infer projection variables in alist

    Attributes
    ----------
    G: InferenceGraph

    session_id : str

    last_heartbeat : time
        The last time an inference activity happened to 
        determine when to time-out.

    property_refs : dict
        Reference to properties in knowledge bases that match predicate in query.

    reverse_property_ref s: dict
        Inverse references to properties in knowledge bases that match predicate in query.

    max_depth: int
        The current maximum depth in the inference graph from the root node.

    propagated_alists : list
        List of root node alists resolved after successful propagation 
        of variables from leaf nodes.

    root : Alist
        Alist in the root node of inference graph.

    explainer: Explanation
        An object to generate explanations.     

    """

    def __init__(self, G: InferenceGraph):
        """
        Parameters
        ----------
        G : InferenceGraph
        """
        self.G = G
        self.session_id = '0'
        self.last_heartbeat = time.time()
        self.property_refs = {}
        self.reverse_property_refs = {}
        self.max_depth = 0
        self.propagated_alists = []
        self.root = None
        self.explainer = Explanation()

    def enqueue_root(self, alist):
        """ Add alist as the root node of the inference graph"""
        self.root = alist
        self.G.add_alist(alist)

    def run_frank(self, alist: Alist):
        """ Run the FRANK algorithm for an alist

        Args
        ----
        alist : Alist

        Return
        ------
        Return True if the instantiation of the project variable of an alist 
        is propagated to the root node.

        Notes
        -----
        For the given alist, attempt to instantiate projection 
        variable. If instantiation is successful, attempt to reduce
        Else decompose and add new children to queue
        """
        self.last_heartbeat = time.time()
        curr_propagated_alists = []
        self.max_depth = alist.depth
        if alist.state is states.PRUNED:
            self.write_trace(
                f"{pcol.RED}ignore pruned {alist.id}{pcol.RESET}-{alist}{pcol.RESETALL}")
            return propagated_alists

        bool_result = False
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
            self.G.add_alist(alist)
        # if OPVAR not instantiated, search KB
        elif not bool_result:
            bool_result = self.search_kb(alist)
        # search kb for the variable instantiation

        if bool_result:
            is_propagated = False
            if alist.state != states.REDUCIBLE:  # if in reducible state, don't change
                alist.state = states.EXPLORED
                self.G.add_alist(alist)
            if agg_instantiated and proj_instantiated:
                alist.state = states.REDUCIBLE
                self.G.add_alist(alist)
            if self.G.child_ids(alist.id):
                is_propagated = self.propagate(self.G.child_ids(alist.id)[0])
            else:
                is_propagated = self.propagate(
                    self.G.child_ids(self.G.parent_ids(alist.id)[0])[0])

            if is_propagated:
                prop_alist = self.G.alist(self.root.id)
                self.write_trace(f"{pcol.CYAN}intermediate ans: "
                                 f"{pcol.RESET}-{prop_alist}{pcol.RESETALL}",
                                 loglevel=processLog.LogLevel.ANSWER)
                curr_propagated_alists.append(prop_alist.copy())
                self.propagated_alists.append(prop_alist.copy())
        else:
            alist.state = states.EXPLORED
            self.G.add_alist(alist)
            for mapOp in self.get_map_strategy(alist):
                self.decompose(alist, mapOp)
        return curr_propagated_alists

    def search_kb(self, alist: Alist):
        """ Search knowledge bases to instantiate variables in alist.

        Args
        ----
        alist: Alist

        Return
        ------
        Returns `True` if variable instantiation is successful from a KB search.

        """
        self.last_heartbeat = time.time()
        self.write_trace(
            f"{pcol.MAGENTA}search {alist.id}{pcol.RESET} {alist}{pcol.RESETALL}")
        if alist.state == states.EXPLORED:
            new_alist = alist.copy()
            new_alist.state = states.EXPLORED
            new_alist.set(tt.OPVAR, alist.get(tt.OPVAR))
            return True

        prop_string = alist.get(tt.PROPERTY)
        prop_refs = []
        found_facts = []
        sources = {
            'wikidata': {'fn': wikidata, 'trust': 'low'},
            'worldbank': {'fn': worldbank, 'trust': 'high'}
        }
        context = alist.get(tt.CONTEXT)
        context_store = {}
        # context_store = {**context[0], **context[1], **context[2]}
        for source_name, source in sources.items():
            # check context for trust
            if ctx.trust in context_store:
                if context_store[ctx.trust] == 'high' and source['trust'] != 'high':
                    continue
            # for source_name, source in {'worldbank':worldbank}.items():
            search_alist = alist.copy()
            # inject context into IR
            search_alist = frank.context.inject_retrieval_context(
                search_alist, source_name)

            # if the property_refs does not contain an entry for the property in this alist
            # search KB for a ref for the property
            prop_sources = []
            if prop_string in self.property_refs:
                prop_sources = [x[1] for x in self.property_refs[prop_string]]

            if (prop_string not in self.property_refs and not prop_string.startswith('__')) \
                    or (prop_string in self.property_refs and source_name not in prop_sources):

                props = source['fn'].search_properties(prop_string)

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
                (cache_found_flag, results) = (False, [])
                # (cache_found_flag, results) = frank.cache.neo4j.search_cache(alist_to_instantiate=search_alist,
                #                                                         attribute_to_instantiate=search_attr,
                #                                                         search_attributes=searchable_attr)
                if cache_found_flag == True:
                    found_facts.append(results[0])
                # search with source-specific property IDs

                for (propid, _source_name) in self.property_refs[prop_string]:
                    self.last_heartbeat = time.time()
                    search_alist.set(tt.PROPERTY, propid[0])
                    (cache_found_flag, results) = (False, [])
                    #  = frank.cache.neo4j.search_cache(alist_to_instantiate=search_alist,
                    #                                                         attribute_to_instantiate=search_attr,
                    #                                                         search_attributes=searchable_attr)
                    if cache_found_flag == True:
                        found_facts.append(results[0])
                        self.write_trace(
                            f'{pcol.MAGENTA}found: cache{pcol.RESETALL}')
                # if not found_facts:
                #     self.write_trace('found:>>> cache')
            if not cache_found_flag and prop_string in self.property_refs:
                # search for data for each property reference source
                for propid_label, _source_name in self.property_refs[prop_string]:
                    self.last_heartbeat = time.time()

                    try:
                        if _source_name == source_name:
                            search_alist.set(tt.PROPERTY, propid_label[0])
                            found_facts.extend(source['fn'].find_property_values(
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
                        self.write_trace(
                            f"{pcol.RED}Search Error{pcol.RESETALL}", processLog.LogLevel.ERROR)
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
                sourceCov = sourcePrior().get_prior(
                    source=list(ff.data_sources)[0]).cov
                ff.set(tt.COV, sourceCov)
                ff.state = states.REDUCIBLE
                ff.set(tt.EXPLAIN, '')
                ff.node_type = nt.FACT
                if ff.get(tt.PROPERTY) in self.reverse_property_refs:
                    ff.set(tt.PROPERTY,
                           self.reverse_property_refs[ff.get(tt.PROPERTY)])

                alist.parent_decomposition = "Lookup"
                self.G.add_alist(alist)
                self.G.link(alist, ff, alist.parent_decomposition)

                # fact is considered reduced
                self.write_trace(
                    f'  {pcol.MAGENTA}found:{pcol.RESET} {str(ff)}{pcol.RESETALL}')
        return len(found_facts) > 0

    def get_map_strategy(self, alist: Alist):
        """ Get decomposition rules to apply to an alist

        Args
        ----
        alist : Alist

        Return
        ------
        ops : A list of reduce functions for aggregating alists

        """
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

    def decompose(self, alist: Alist, map_op):
        """ Apply a decomposition rule to create successors of an alist

        Args
        ----
        alist : Alist to decompose

        map_op : str
            Name of the map operation to apply to the alist

        Return
        ------
        alist: Alist
            Successor h-node alist that has z-node child alists

        Notes
        -----
        z-nodes are alists that represent facts and contain variables that 
        are to be instantiated with data from knowledge bases.
        h-nodes are alists that have operations to aggregate their child z-nodes.
        Decompositions create z-node and specify the `h` operations for aggregating 
        the decomposed child nodes.

                    (alist)
                       |
                       |
                    (h-node)
                    / ... \\
                   /  ...  \\   
            (z-node1) ... (z-nodeN)

        """
        self.last_heartbeat = time.time()
        if alist.depth + 1 > config.config['max_depth']:
            print('max depth reached!\n')
            alist.state = states.IGNORE
            return alist

        self.write_trace('{blue}{bold}T{thread}{reset} > {op}:{id}-{alist}{resetall}'.format(
            blue=pcol.BLUE, reset=pcol.RESET, bold=pcol.RESET, resetall=pcol.RESETALL,
            thread=threading.get_ident(),
            op=map_op[1], alist=alist, id=alist.id))
        alist.branchType = br.OR
        child = map_op[0](alist, self.G)
        # check for query context
        context = alist.get(tt.CONTEXT)
        self.last_heartbeat = time.time()
        if child is not None:
            self.write_trace(
                f'{pcol.BLUE}>> {child.id}{pcol.RESET}-{str(child)}{pcol.RESETALL}')
            succ = self.G.successors(child.id)
            for node_id1 in succ:
                grandchild = self.G.alist(node_id1)
                self.write_trace(
                    f'  {pcol.BLUE}>>> {grandchild.id}{pcol.RESET}-{str(grandchild)}{pcol.RESETALL}')
                reducibleCtr = 0
                succ2 = self.G.successors(grandchild.id)
                for node_id2 in succ2:
                    ggchild = self.G.alist(node_id2)
                    self.write_trace(
                        f'  {pcol.BLUE}>>> {ggchild.id}{pcol.RESET}-{str(ggchild)}{pcol.RESETALL}')
                    if ggchild.state == states.REDUCIBLE:
                        self.G.add_alist(ggchild)
                        reducibleCtr += 1
            # generate the WHY explanation
            self.explainer.why(self.G, alist, map_op[1])
            return child
        else:
            return None

    def aggregate(self, alist_id):
        """ Aggregate the child nodes of an alist by applying the operation 
            specified by the *`h`* attribute of the node's alist.

        Args
        ----
        alist_id : str
            Id of alist whose child nodes should be aggregated

        Return
        --------
        Returns True if aggregation was successful.  

        Notes
        -----
        Only child alists that are in the `reduced` or `reducible` states are aggregated.
        The result of the aggregation is stored in the alist and the inference graph is updated.
        Text explaining the aggregation is also added to the `xp` attribute of the alist.
        """
        alist = self.G.alist(alist_id)
        self.last_heartbeat = time.time()
        self.write_trace(
            f'{pcol.YELLOW}reducing {alist.id}{pcol.RESET}-{alist}{pcol.RESETALL}')

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
            self.write_trace(
                f'  {pcol.YELLOW}<<< {x.id}{pcol.RESET}-{x}{pcol.RESETALL}')

        unexplored = [
            x for x in children if x.state == states.UNEXPLORED]
        if not reducibles or len(unexplored) == len(children):
            return False  # there's nothing to reduce

        reducedAlist = reduce_op.reduce(alist, reducibles, self.G)

        last_heartbeat = time.time()

        if reducedAlist is not None:
            for c in children:
                alist.data_sources = list(
                    set(alist.data_sources + c.data_sources))
            for r in reducibles:
                r.state = states.REDUCED
                self.G.add_alist(r)
            alist.state = states.REDUCIBLE  # check later
            self.G.add_alist(alist)
            self.explainer.what(self.G, alist, True)
            self.write_trace(
                f"{pcol.GREEN}reduced {alist.id}{pcol.RESET}-{alist}{pcol.RESETALL}")
            return True
        else:
            self.explainer.what(self.G, alist, False)
            self.write_trace(
                f"{pcol.YELLOW}reduce {alist.id} failed {pcol.RESET}-{alist}{pcol.RESETALL}")
            return False

    def propagate(self, alist_id):
        self.last_heartbeat = time.time()
        curr_alist = self.G.alist(alist_id)
        self.write_trace(
            f'{pcol.GREEN}propagate {curr_alist.id}{pcol.RESET}-{curr_alist}{pcol.RESETALL}')
        # try:
        while self.G.parent_ids(curr_alist.id):
            # get parent alist and apply its reduce operation to its successors
            if self.aggregate(self.G.parent_ids(curr_alist.id)[0]):
                # set the parent to the current alist and recurse
                curr_alist = self.G.parent_alists(curr_alist.id)[0]
            else:
                return False
        # except Exception as e:
        #     self.write_trace("Error during propagation: " +
        #                      str(e), processLog.LogLevel.ERROR)
        #     return False
        return True

    def write_trace(self, content, loglevel=processLog.LogLevel.INFO):
        processLog.println(content, processLog.LogLevel.INFO)
