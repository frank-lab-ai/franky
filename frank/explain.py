'''
File: explain.py
Description: Generate explanations for alists and operations.


'''

from frank.alist import Alist
from frank.alist import Attributes as tt
from frank.alist import States as states
from frank.alist import Branching as branching
from frank.alist import NodeTypes as nt
from frank import config
from frank.graph import InferenceGraph


class Explanation():

    def __init__(self):
        self.ops_text = {'value': 'value', 'max': 'maximum value', 'min': 'minimum value', 'avg': 'average',
                         'mean': 'average', 'mode': 'modal value', 'regress': 'predicted value',
                         'linregress': 'predicted value',
                         'nnregress': 'predicted value',
                         'gpregress': 'predicted value',
                         'nnpredict': 'predicted value', 'comp': 'value',
                         'values': 'values', 'eq': 'equal to', 'gt': 'greater than', 'gte': 'greater than or equal to',
                         'lt': 'less than', 'lte': 'less than or equal to'}
  
    def generateExplanation(self, G:InferenceGraph, node_id, descendant_blanket_length=1, ancestor_blanket_length=1):
        ''' Generate explanation of a node given its blanket'''

        '''
        Saliency ordering: Some decompositions and aggregation operations are not important given their distance
        from the node being explained.
        VALUE nodes based on a LOOKUP decomposition do not need to be explained. State the fact that the value was retrieved.
        Multiple VALUE nodes from LOOKUPs of a node can be simplified as "values looked up from DISTINCT(sources).
        Any VALUE child node that was not retrieved and hence decomposed for further lookup should be highlighted; but no need to
        specify the details of that operation if it falls outside the explanation blanket.
        Any VALUE node for which instantiation failed should be highlighted in the explanation.
        Synonyms for "enclosures" or "scope" to replace "blanket".

        Repetition rule: Should not repeat the same explanation for child nodes with the same operation.
        Instead summarise as one explanation and only highlight differences: e.g. failed instantiations, high uncertainties.

        General procedure for generating the explanation for a node.
        FRANK generates an explanation of length 1 for each node as part of inference.
        To generate an explanation with length > 1, 
            1. ancestors of n*: recursively propagate explanations from parents to their children by appending.
            This explanation should provide a "causal explanation" or justification of the decomposition operation at n*.
            2. descendants of n* : recursively propagate and append explantions from child nodes 
        to their parents. This provides a justification of the aggregation operation at n*.
            3. at n*: a detailed explanation of any aggregation operation performed at n* and the decomposition performed

        Structure of the explanation template:
        <at n*> by <descendants of n*> in the context of <ancestors of n*>
        E.g:  The predicted population of Ghana in 2017 using regression function based on values from past years is 
            26,500,000 with an error margin of +/-35,000.
            Retrieved the population values between 1990 and 2010 from the World Bank and Wikidata.
            Had to predict the population of Ghana in 2017 since I needed to calculate the total population of Africa in 2017
            but could not find any value for the population of Africa in 2017. After decomposing Africa into its parts, I also
            could not find the population of Ghana in 2017.

        Return an object containing a fully composed explanation as well as the partial explanations for WHAT, WHY and HOW.


        '''
        explanation = {"all": "", "what": "", "how": "", "why": ""}

        # get n_star node
        n_star: Alist = G.alist(node_id)
        if not n_star:
            return ''
        ancestors = self.ancestor_explanation(G,
            n_star, "", int(ancestor_blanket_length), 1).strip()
        descendants = self.descendant_explanation(G,
            n_star, "", int(descendant_blanket_length), 1).strip()
        self_exp = f"{n_star.get('what') if 'what' in n_star.attributes else ''} {n_star.get('how') if 'how' in n_star.attributes else ''} "
        sources = self.sources(n_star)
        explanation = {
            # "all":f"{n_star_exp} {n_dsc} {n_asc}",
            "what": self_exp,
            "how": descendants,
            "why": ancestors,
            "sources": sources
        }
        return explanation

    # def summarizeChildren(self, alist: Alist, summary, max_distance, distance):
        if max_distance < distance:
            return ''

        if not alist.children:
            return ''

        feat = ''
        if alist.parent_decomposition.lower() == 'temporal':
            feat = tt.TIME
        elif alist.parent_decomposition.lower() == 'geospatial':
            feat = tt.SUBJECT
        elif alist.parent_decomposition.lower() == 'lookup':
            feat = tt.OBJECT
        elif alist.parent_decomposition.lower() in ['normalize', 'comp']:
            feat = alist.get(tt.OPVAR)
        elif alist.parent_decomposition.lower() == 'comparison':
            feat = f"?{alist.get(tt.OP)}"
        elif not alist.parent:
            feat = alist.get(tt.OPVAR)

        decomps = []
        ops = []
        properties = []
        for child in alist.children:
            # if alist.parent_decomposition.lower() == 'temporal':
            feats = feat.split(' ')
            for ft in feats:
                if ft in child.attributes:
                    decomps.append(child.get(ft))
            # elif alist.parent_decomposition.lower() in  ['normalize','comp']:
            #   decomps.append(child.get(feat))
            ops.append(child.get(tt.OP))
            properties.append(child.get(tt.PROPERTY))

        sources = ''
        if len(alist.data_sources) == 1:
            sources = f" from {list(alist.data_sources)[0]}"
        elif len(alist.data_sources) > 1:
            sources = f" from {', '.join(list(alist.data_sources)[0:len(alist.data_sources)-1])} and {list(alist.data_sources)[-1]}"

        if alist.parent_decomposition.lower() == 'temporal':
            data_range = f" between {min(decomps)} and {max(decomps)}"
            if min(decomps) == max(decomps):
                data_range = f" in {min(decomps)}"
            if alist.instantiation_value(alist.get(tt.OPVAR)):
                # summarize as successful instantiation
                summary += f" Found {properties[0]} values{data_range}{sources} to predict the {properties[0]} of " + \
                    f"{alist.instantiation_value(tt.SUBJECT)} in {alist.get(tt.TIME)}. "
            else:
                # summarize as unsuccessful instantiation
                summary += f" Failed to find the {properties[0]} values{data_range}. "
        elif alist.parent_decomposition.lower() in ['normalize', 'comp']:
            # todo: be specific about sub-query
            time = f" in {alist.get(tt.TIME)}" if alist.get(tt.TIME) else ""
            if alist.get(tt.OP) in ['min', 'max', 'avg', 'mode', 'mean']:
                summary += f" Solved the sub-query and calculated the {self.ops_text[alist.get(tt.OP)]} of the {alist.get(tt.PROPERTY)}{time}."
            elif alist.get(tt.OP) in ['comp'] and decomps:
                listed_str = ''
                for dc in decomps:
                    listed = dc.split(',')
                    if len(listed) > 8:
                        listed_str += f"{', '.join(listed[0:8])}, etc. "
                    else:
                        listed_str += ', '.join(listed)
                summary += f" Found these as solutions to the sub-query: {listed_str}."
            else:
                if alist.get(tt.PROPERTY):
                    summary += f" Solved the sub-query and calculated the {self.ops_text[alist.get(tt.OP)]} of the {alist.get(tt.PROPERTY)} of " + \
                        f"{alist.instantiation_value(tt.SUBJECT)}{time}."
                else:
                    summary += ' ' + alist.get(tt.EXPLAIN)
        elif not alist.parent:
            for child in alist.children:
                summary += self.summarizeNode(child, False)

        for child in alist.children:
            csumm = self.summarizeChildren(
                child, summary, max_distance, distance+1)
            summary = csumm if csumm else summary

        return summary

    # def summarizeParents(self, alist: Alist, summary, max_distance, distance):

    #     if distance <= max_distance:

    #         for parent in alist.parent:
    #             time = f" in {parent.get(tt.TIME)}" if parent.get(
    #                 tt.TIME) else ""

    #             if alist.parent_decomposition.lower() == 'temporal':
    #                 if alist.get(tt.OP).lower() == 'regress':
    #                     summary = f" Had to predict the {parent.get(tt.PROPERTY)} of {parent.instantiation_value(tt.SUBJECT)}{time} " + \
    #                         f"since the required {parent.get(tt.PROPERTY)} value was not found " + \
    #                         f"in the knowledge bases searched.{summary}"
    #                 else:
    #                     summary += f" Tried to find the {parent.get(tt.PROPERTY)} of {parent.instantiation_value(tt.SUBJECT)} " + \
    #                         f"in other times from which to extrapolate."
    #             elif alist.parent_decomposition.lower() == 'geospatial':
    #                 summary += f" The {parent.get(tt.PROPERTY)} of {parent.instantiation_value(tt.SUBJECT)}{time} was not found " + \
    #                     f"so we had find the {parent.get(tt.PROPERTY)} for its constituents.{summary}"
    #             elif alist.parent_decomposition.lower() == 'comparison':
    #                 summary += f" Had to solve for the values of the items to be compared."
    #             else:
    #                 if parent.get(tt.OP).lower() in ['eq', 'lt', 'gt']:
    #                     summary += f" Had to decompose the query in order to determine if the first sub-query " + \
    #                         f"is {self.ops_text[parent.get(tt.OP)]} the second.{summary}"
    #                 elif parent.get(tt.OP).lower() in ['min', 'max', 'avg', 'mode', 'mean']:
    #                     summary += f" The required {self.ops_text[parent.get(tt.OP)]} of the {parent.get(tt.PROPERTY)}{time} " + \
    #                         f"was not found in the knowledge bases searched.{summary}"
    #                 else:
    #                     summary += f" The {self.ops_text[parent.get(tt.OP)]} of the {parent.get(tt.PROPERTY)} of {parent.instantiation_value(tt.SUBJECT)}{time} " + \
    #                         f"was not found in the knowledge bases searched.{summary}"
    #             summary = self.summarizeParents(
    #                 parent, summary, max_distance, distance+1)
    #     return summary

    # def summarizeNode(self, alist: Alist, in_place=True):
        ''' generate explanation for node, assign to alist attribute in place and return the explanation'''
        summary = ''
        try:
            if len(alist.data_sources) == 1:
                sources = f"{list(alist.data_sources)[0]}".strip()
            elif len(alist.data_sources) > 1:
                sources = f"{', '.join(list(alist.data_sources)[0:len(alist.data_sources)-1])} and {list(alist.data_sources)[-1]}".strip(
                )

            comp_in_child = False
            if alist.parent_decomposition.lower() == 'temporal' and alist.instantiation_value(alist.get(tt.OPVAR)):
                summary = f"The predicted {alist.get(tt.PROPERTY)} of {alist.instantiation_value(tt.SUBJECT)} " + \
                    f"in {alist.get(tt.TIME)} using a regression function based on {alist.get(tt.PROPERTY)} " + \
                    f"data from past times is {alist.instantiation_value(alist.get(tt.OPVAR))}."
                # f"data from past times is {list(alist.projection_variables().values())[0]}."
            elif alist.parent_decomposition.lower() == 'geospatial' and alist.instantiation_value(tt.SUBJECT):
                summary = f"Found the constituents of {alist.instantiation_value(tt.SUBJECT)}."
            elif alist.parent_decomposition.lower() == 'lookup' and sources:
                # if len(alist.data_sources) ==1:
                #   sources = f" from {list(alist.data_sources)[0]}"
                # elif len(alist.data_sources) > 1:
                #   sources = f" from {', '.join(list(alist.data_sources)[0:len(alist.data_sources)-1])} and {list(alist.data_sources)[-1]}"
                summary = f"Facts were retrieved from the {sources} knowledge base(s)."

            elif alist.parent_decomposition.lower() in ['normalize', 'comp']:
                # sources = ' '.join(alist.data_sources)
                filter_exp = ""
                counter = 0
                for child in alist.children:
                    if child.get(tt.PROPERTY).startswith("__geopolitical"):
                        if len(filter_exp) > 0:
                            filter_exp = filter_exp + " and "
                        ctype = child.get(tt.PROPERTY).split(":")[1]
                        filter_exp = filter_exp + f"to find entities that have type {ctype}" + \
                            f" and are located in {child.instantiation_value(tt.OBJECT)}"
                    elif child.get(tt.OP).lower() == "values":
                        if len(filter_exp) > 0:
                            filter_exp = filter_exp + " and "
                        filter_exp = filter_exp + f"to find entities that have a {child.get(tt.PROPERTY)} of " + \
                            f"'{child.get(tt.PROPERTY)}'"
                    else:
                        if child.instantiation_value(tt.OBJECT):
                            if counter == 0:
                                if len(filter_exp) > 0:
                                    filter_exp = filter_exp + " and "
                                filter_exp = filter_exp + f"to find the {child.get(tt.PROPERTY)} of " + \
                                    f"{child.instantiation_value(tt.SUBJECT)} ({child.instantiation_value(tt.OBJECT)})"
                            elif counter > 0 and counter <= 5:
                                filter_exp = filter_exp + \
                                    f", {child.instantiation_value(tt.SUBJECT)} ({child.instantiation_value(tt.OBJECT)})"
                            elif counter == 6:
                                filter_exp = filter_exp + ", etc"
                        else:
                            if counter == 0:
                                if len(filter_exp) > 0:
                                    filter_exp = filter_exp + " and "
                                filter_exp = filter_exp + f"to find the {child.get(tt.PROPERTY)} of" + \
                                    f"{child.instantiation_value(tt.SUBJECT)}"
                            elif counter > 0 and counter <= 5:
                                filter_exp = filter_exp + \
                                    f", {child.instantiation_value(tt.SUBJECT)}"
                            elif counter == 6:
                                filter_exp = filter_exp + ", etc"
                        counter += 1
                if filter_exp.strip():
                    summary = f"Evaluated the sub-query {filter_exp}."

            # * generate explanation for reduce operation.
            reduce_exp = ""
            # * explain any subqueries set comps in children nodes
            time = "" if alist.get(
                tt.TIME) == '' else "in " + alist.get(tt.TIME)

            opDesc = ""
            if alist.get(tt.OP).lower() not in ["value", "values", "comp", "regress", "nnpredict", "gt", "gte", "lt", "lte", "eq"]:
                inferred_value = alist.instantiation_value(alist.get(tt.OPVAR))
                proj_var = alist.projection_variables()
                if len(proj_var) > 0 and alist.get(list(proj_var.keys())[0]):
                    inferred_value = alist.instantiation_value(
                        list(proj_var.keys())[0])
                opDesc = f" Calculated the {self.ops_text[alist.get(tt.OP)]} of the {alist.get(tt.PROPERTY)} {time} " + \
                    f"for the entities. Inferred value is {inferred_value}."
                if opDesc not in reduce_exp:
                    reduce_exp = reduce_exp.strip() + opDesc
            elif alist.get(tt.OP).lower() == "value":
                if alist.get(tt.PROPERTY) and alist.instantiation_value(tt.SUBJECT):
                    opDesc = f" The {self.ops_text[alist.get(tt.OP)]} of the {alist.get(tt.PROPERTY)} of " + \
                        f"{alist.instantiation_value(tt.SUBJECT)} {time} is {alist.instantiation_value(tt.OBJECT)}."
                    if opDesc not in reduce_exp:
                        reduce_exp = reduce_exp.strip() + opDesc
            elif alist.get(tt.OP).lower() in ["gt", "gte", "lt", "lte", "eq"]:
                proj_var = f"?{alist.get(tt.OP).lower()}"
                cmp_vars = alist.get(tt.OPVAR).split(' ')
                if alist.is_instantiated(proj_var) and bool(alist.instantiation_value(proj_var)):
                    opDesc = f"The comparison returned True since {alist.instantiation_value(cmp_vars[0])} is {self.ops_text[alist.get(tt.OP)]} {alist.instantiation_value(cmp_vars[1])}."
                if opDesc not in reduce_exp:
                    reduce_exp = reduce_exp.strip() + opDesc

            summary = (reduce_exp + " " + summary).strip()
            # assign explanation to node (and to its parent).
            if in_place:
                alist.set(tt.EXPLAIN, summary)
                if len(alist.parent) > 0 and \
                        not len(summary.strip()) > 0 and \
                        reduce_exp not in alist.parent[0].get(tt.EXPLAIN):
                    alist.parent[0].set(tt.EXPLAIN, summary)
        except Exception as ex:
            print("error generating explanation: " + str(ex))

        return summary

    def why(self, G:InferenceGraph,  alist: Alist, decomp_op, in_place=True):
        ''' Explain a decomposition of this alist. 
            Assumes a failed instantiation of this alist following KB searches'''
        expl = ""
        time = ""
        children = G.child_alists(alist.id)
        if alist.get(tt.TIME):
            time = f" in {alist.get(tt.TIME)}"
        if decomp_op == 'temporal':
            expl = f"Could not find the {alist.get(tt.PROPERTY)} of {alist.instantiation_value(tt.SUBJECT)}{time}. "
            decomp_items = []
            # for c in alist.children[0].children:
            for c in children:
                decomp_items.append(c.get(tt.TIME))
            if len(decomp_items) >= 2:
                expl += f"Attempted to infer the required value{time} by finding the {alist.get(tt.PROPERTY)} of {alist.instantiation_value(tt.SUBJECT)} " + \
                    f"at other times between {min(decomp_items)} and {max(decomp_items)}."

        elif decomp_op == 'geospatial':
            expl = f"Could not find the {alist.get(tt.PROPERTY)} of {alist.instantiation_value(tt.SUBJECT)}{time}. "
            decomp_items = []
            # for c in alist.children[0].children:
            for c in G.child_alists(children[0].id):
                decomp_items.append(c.instantiation_value(tt.SUBJECT))
            entities = ''
            if len(decomp_items) > 8:
                entities = f"{', '.join(decomp_items[0:8])} etc"
            else:
                entities = f"{', '.join(decomp_items[0:len(decomp_items)-1])} and {decomp_items[-1]}"
            if decomp_items:
                expl += f"Finding the {alist.get(tt.PROPERTY)}{time} for the constituent parts of " + \
                    f" {alist.instantiation_value(tt.SUBJECT)}: {entities}."

        elif decomp_op == 'normalize':
            expl = f"Need to solve the sub-queries before determining the {alist.get(tt.PROPERTY)}{time}."

        elif decomp_op == 'comparison':
            expl = f"Need to solve the sub-queries to determine the items to compare."

        if in_place:
            alist.set("why", expl)
            G.add_alist(alist)

    def what(self, G: InferenceGraph, alist: Alist, is_reduced: bool, in_place=True):
        ''' Explain a reduction of this alist. 
        '''
        what = ''
        how = ''
        time = ""
        if alist.get(tt.TIME):
            time = f" in {alist.get(tt.TIME)}"

        if not is_reduced:
            if alist.get(tt.OP) in ['eq', 'gt', 'gte', 'lt', 'lte']:
                what = f"Failed to compare the values since the values of all items being compare are not known. "
            elif alist.get(tt.OP) in ['comp']:
                what = f"Failed to solve the sub-problem. "
            elif alist.get(tt.OP) in ['value', 'values']:
                what = f"Failed to determine the {self.ops_text[alist.get(tt.OP)]} of {alist.get(tt.PROPERTY)}{time}."
            else:
                what = f"Failed to calculate the {self.ops_text[alist.get(tt.OP)]} of {alist.get(tt.PROPERTY)}{time}."

        else:
            if alist.get(tt.OP) in ['eq', 'gt', 'gte', 'lt', 'lte']:
                vars_compared = alist.get(tt.OPVAR).split(' ')
                if len(vars_compared) > 1:
                    what = f"Inferred value is '{alist.instantiation_value('?'+ alist.get(tt.OP))}'."
                    how = f"Did a comparison to determine if {alist.instantiation_value(vars_compared[0])} is " + \
                          f"{self.ops_text[alist.get(tt.OP)]} {alist.instantiation_value(vars_compared[1])}."
            elif alist.get(tt.OP) in ['comp']:
                listed_str = ''

                listed = alist.instantiation_value(
                    alist.get(tt.OPVAR))
                if listed:
                    listed = listed.split(',')
                    if len(listed) > 8:
                        listed_str += f"{', '.join(listed[0:8])}, etc"
                    else:
                        listed_str += ', '.join(listed)

                if listed_str:
                    what = f"Solved the sub-query and found the following values: {listed_str}."
            else:
                inferred_value = ''
                projected = alist.projection_variables()
                if projected:
                    inferred_value = list(projected.values())[0]
                if not inferred_value:
                    inferred_value = alist.instantiation_value(
                        alist.get(tt.OPVAR))
                if inferred_value:
                    if ':' in alist.get(tt.PROPERTY):
                        listed_str = ''
                        listed = alist.instantiation_value(
                            alist.get(tt.OPVAR)).split(',')
                        if len(listed) > 8:
                            listed_str += f"{', '.join(listed[0:8])}, etc"
                        else:
                            listed_str += ', '.join(listed)
                        what = f"The {alist.get(tt.PROPERTY).split(':')[1]} values found for the sub-query include: {listed_str}."
                    elif (projected or inferred_value) and not alist.get(tt.PROPERTY):
                        # for alists with just a projected value but no property
                        what = f"An input value for operation is {inferred_value}."
                    elif projected and alist.get(tt.OPVAR) not in projected and alist.get(tt.OP) in ['max', 'min']:
                        what = f"The entity whose {alist.get(tt.PROPERTY)}{time} has the {self.ops_text[alist.get(tt.OP)]} of {alist.instantiation_value(alist.get(tt.OPVAR))} is {inferred_value}."
                    elif projected and alist.get(tt.OPVAR) not in projected and alist.get(tt.OP) not in ['max', 'min']:
                        what = f"The {self.ops_text[alist.get(tt.OP)]} of the {alist.get(tt.PROPERTY)}{time} of {inferred_value} is {alist.instantiation_value(alist.get(tt.OPVAR))}."
                    else:
                        what = f"The {self.ops_text[alist.get(tt.OP)]} of the {alist.get(tt.PROPERTY)} of {alist.instantiation_value(tt.SUBJECT)}{time} is {inferred_value}."
                if alist.get(tt.OP) in ['regress', 'nnpredict', 'linregress', 'gpregress', 'nnregress']:
                    decomp_items = []
                    children = G.child_alists(alist.id)
                    # for c in alist.children[0].children:                    
                    for c in G.child_alists(children[0].id):
                        decomp_items.append(c.get(tt.TIME))
                    if len(decomp_items) > 0:
                        how = f"Generated a regression function from times between {min(decomp_items)} and {max(decomp_items)}."

        if in_place:
            alist.set("what", what)
            alist.set("how", how)
            G.add_alist(alist)


    def sources(self, alist):
        sources = ''
        if len(alist.data_sources) == 1:
            sources = f"{list(alist.data_sources)[0]}".strip()
        elif len(alist.data_sources) > 1:
            sources = f"{', '.join(list(alist.data_sources)[0:len(alist.data_sources)-1])} and {list(alist.data_sources)[-1]}".strip(
            )

        return f"Retrieved fact(s) from the {sources} knowledge {'sources' if len(alist.data_sources) > 1 else 'source'}."

    def ancestor_explanation(self, G:InferenceGraph, alist: Alist, summary, max_length, length):
        if length <= max_length:
            # for parent in alist.parent:
            for parent in G.parent_alists(alist.id):
                summary = f"{parent.get('why') if 'why' in parent.attributes else ''} {summary}".strip(
                )
                summary = self.ancestor_explanation(G, parent, summary, max_length, length+1)
        return summary

    def descendant_explanation(self, G:InferenceGraph, alist: Alist, summary, max_length, length):
        if length <= max_length:
            # for child in alist.children:
            for child in G.child_alists(alist.id):
                summary = f"{summary}{' ' + child.get('how') if 'how' in child.attributes else ''}" + \
                    f"{' ' + child.get('what') if 'what' in child.attributes else ''}".strip()
                summary = self.descendant_explanation(G, child, summary, max_length, length+1)
        return summary
