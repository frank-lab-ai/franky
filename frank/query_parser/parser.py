'''
File: parser.py
Description: Template-based parser for NL queries.


'''

import datetime

import json
import hashlib
import hmac
from urllib.parse import urlencode
import re
import uuid
import math
import numbers
from collections import deque
import spacy
import itertools
import time


class Parser:
    nlp_lib = None

    def __init__(self):
        if Parser.nlp_lib == None:
            Parser.nlp_lib = spacy.load('en_core_web_sm')

    # Find a template
    def find_templates(self, querystring):
        """ Match the query string to query templates

        Args: querystring
        """
        # remove multiple spaces from querystring
        querystring = ' '.join(querystring.split())
        return self.getNextSuggestion(querystring)

    def getNextSuggestion(self, querystring):
        doc = Parser.nlp_lib(querystring)
        tkns = []
        for token in doc:
            print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_)
            tkns.append((token.text, token.lemma_, token.pos_, token.tag_, token.dep_))

        pos_mapper = {
            # 'NOUN:WP': 'wh',
            'ADP:IN': 'prep',
            'NOUN:NN': 'propclass',
            'NOUN:NNS': 'propclass',
            'PROPN:NNP': 'entity',
            'VERB:VB': 'verb',
            'VERB:VBD': 'verb',
            'VERB:VBG': 'verb',
            'VERB:VBZ': 'verb',
            'VERB:VBN': 'verb',
            'ADJ:JJ': 'operation',
            'ADJ:JJS': 'operation',
            'ADJ:JJR': 'comparison',
            'NUM:CD': 'datetime',
            'ADV:WRB': 'when'
        }

        operation_triggers = [
            'total', 'average', 'mean']
        stop_words = ['is', 'the', 'was', 'did', 'do']
        query_types = ['what', "how many", "when", "who"]

        mapped_terms = []
        mapped_terms2 = []
        skip_start_char = -1
        skip_end_char = -1
        in_compound = False
        in_jjphrase = False
        compound_NN = ''
        compound_PROPCLASS = ''

        # check if all nouns
        all_nns = True
        for token in doc:
            if token.pos_ != 'NOUN':
                all_nns = False
                break
        
        if all_nns:
            for token in doc:
                if token.text in stop_words:
                    continue
                token_tag = token.pos_ + ':' + token.tag_
                if token.head.i > token.i + 1:
                    # do not append head token
                    if token_tag in pos_mapper:
                        mapped_terms.append([pos_mapper[token_tag], token.text.strip(), token_tag])
                if token.head.i == token.i + 1:
                    # if this token appears just before the head token
                    token_tag = token.head.pos_ + ':' + token.head.tag_
                    if token_tag in pos_mapper:
                        mapped_terms.append([pos_mapper[token_tag], (token.text + ' ' + token.head.text).strip(), token_tag])

        if not all_nns:
            for token in doc:
                token_tag = token.pos_ + ':' + token.tag_
                if token.text in stop_words:
                    continue
                if token.idx >= skip_start_char and token.idx <= skip_end_char:
                    continue
                in_ent = False
                for ent in doc.ents:
                    if token.idx >= ent.start_char and token.idx <= ent.end_char:
                        token_tag = token.pos_ + ':' + token.tag_
                        if token_tag in pos_mapper:
                            in_ent = True
                            skip_start_char = ent.start_char
                            skip_end_char = ent.end_char                    
                            mapped_terms.append([pos_mapper[token_tag], ent.text.replace('the', '').strip(), token_tag])
                        break

                if in_ent == False:
                    skip_start_char = -1
                    skip_end_char = -1
                    if token.tag_ == "JJ" and token.text not in operation_triggers:
                        compound_PROPCLASS = token.text_with_ws
                        continue

                if in_ent == False:
                    skip_start_char = -1
                    skip_end_char = -1
                    token_tag = token.pos_ + ':' + token.tag_
                    if token.dep_ == 'compound' and in_compound == False:
                        in_compound = True
                        compound_NN = compound_PROPCLASS + token.text
                        compound_PROPCLASS = ''

                    elif token.dep_ != 'compound' and in_compound == True:
                        compound_NN += ' ' + token.text
                        if token_tag in pos_mapper:
                            mapped_terms.append([pos_mapper[token_tag], compound_NN.strip(), token_tag])
                        compound_NN = ''
                        in_compound = False

                    else:
                        if token_tag in pos_mapper:
                            mapped_terms.append([pos_mapper[token_tag], compound_PROPCLASS + token.text, token_tag])
                        compound_PROPCLASS = ''
                        
        for x in mapped_terms:
            if x[0] == 'prep':
                x[0] = x[1]

        query_frame = self.GenerateQueryFromRegex(mapped_terms)

        returnObj = {'question': querystring,
                     'template': [x[0] for x in mapped_terms], 
                     'alist': query_frame}
        return (returnObj)

    def GenerateQueryFromRegex(self, tokens):
        tokens_with_idx = ''
        for idx in range(len(tokens)):
            tokens_with_idx += tokens[idx][0] + '-' + str(idx) + ' '
        tokens_with_idx = tokens_with_idx.strip()

        alist = {}
        is_nested = True
        var_ctr = 3
        (alist, var_ctr, pattern) = self.create_alist(
            alist, tokens_with_idx, var_ctr, tokens)
        queue = deque()
        queue = self.scan_alist(alist, queue)

        previous_pattern = pattern
        while queue:
            qitem = queue.pop()
            curr_alist = qitem[0]
            k = qitem[1]
            v = qitem[2]
            if isinstance(v, str):
                if len(v.split()) > 0:
                    is_nested = True
                    (sub_alist, var_ctr, pattern) = self.create_alist(
                        {}, v, var_ctr, tokens)

                    # change other projection vars to aux for pattern where subject is projected
                    if previous_pattern == 70:
                        new_variable = '?x' + str(var_ctr)
                        var_ctr = var_ctr + 1
                        curr_alist[new_variable] = sub_alist
                        curr_alist[k] = new_variable
                        for attr, vv in curr_alist.items():
                            old_var = vv
                            if attr != k and isinstance(vv, str) and vv.startswith('?'):
                                curr_alist[attr] = '$' + vv[1:]
                                if vv in curr_alist:
                                    assigned = curr_alist[vv]
                                    del curr_alist[vv]
                                    curr_alist['$' + vv[1:]] = assigned
                    else:
                        new_variable = '$x' + str(var_ctr)
                        var_ctr = var_ctr + 1
                        curr_alist[new_variable] = sub_alist
                        curr_alist[k] = new_variable

                    queue = self.scan_alist(sub_alist, queue)
                    previous_pattern = pattern
            elif isinstance(v, dict):
                queue = self.scan_alist(v, queue)
            elif isinstance(v, list):
                for item in v:
                    queue = self.scan_alist(item, queue)

        # print(alist)
        return alist

    def scan_alist(self, alist, queue):
        if not alist:
            return queue
        for k, v in alist.items():
            if isinstance(v, dict):
                queue.append((alist, k, v))
            elif isinstance(v, list):
                for item in v:
                    for p, q in item.items():
                        if isinstance(q, dict):
                            queue.append((item, p, q))
            elif isinstance(v, str) and len(v.split()) > 0 and v.startswith('%'):
                queue.append((alist, k, v.replace('%', '')))
        return queue

    def create_alist(self, alist, _attr_value, var_ctr, tokens):
        curr_year = str(datetime.datetime.now().year)
        regex_patterns = [
            # op X of Y in T
            (10, '^(?P<op>operation-\d*) (?P<prop>propclass-\d*) (of)-\d* (?P<entity>entity-\d*) (in|at)-\d* (?P<time>datetime-\d*)$'),
            # X of Y in T
            (15, '^(?P<prop>propclass-\d*) (of)-\d* (?P<entity>entity-\d*) (in|at)-\d* (?P<time>datetime-\d*)$'),
            # op X of  Y>
            (20, '^(?P<op>operation-\d*) (?P<prop>propclass-\d*) (of)-\d* (?P<entity>entity-\d*)$'),
            (25, '^(?P<prop>propclass-\d*) (of)-\d* (?P<entity>entity-\d*)$'),  # X of Y>


            # op X of nested Y in T
            (30, '^(?P<op>operation-\d*) (?P<prop>propclass-\d*) (of)-\d* (?P<entity>.*) (in|at)-\d* (?P<time>datetime-\d*)$'),
            # prop of (nested entity in T )
            (32, '^(?P<prop>propclass-\d*) (of)-\d* (?P<entity>(propclass-\d* (in|at)-\d*.*) (in|at)-\d* (datetime-\d*))$'),
            # X of <nested Y in T
            (35, '^(?P<prop>propclass-\d*) (of)-\d* (?P<entity>.*) (in|at)-\d* (?P<time>datetime-\d*)$'),
            # op X of <nested Y>
            (40, '^(?P<op>operation-\d*) (?P<prop>propclass-\d*) (of)-\d* (?P<entity>.*)$'),
            # X of <nested Y>
            (45, '^(?P<prop>propclass-\d*) (of)-\d* (?P<entity>.*)$'),

            # op X in T of <nested Y
            (50, '^(?P<op>operation-\d*) (?P<prop>propclass-\d*) (in|at)-\d* (?P<time>datetime-\d*) (of)-\d* (?P<entity>.*)$'),
            # X in T of Y
            (55, '^(?P<prop>propclass-\d*) (in|at)-\d* (?P<time>datetime-\d*) (of)-\d* (?P<entity>.*)$'),

            # country in Africa
            (60, '^(?P<class>propclass-\d*) (in|at)-\d* (?P<loc>entity-\d*)$'),
            (65, '^(?P<class>propclass-\d*)$'),  # country ...
            (70, '^(?P<entity>.*) (with|verb)-\d* (?P<op>operation-\d*) (?P<prop>propclass-\d*) (in|at)-\d* (?P<time>datetime-\d*)$'),
            (75, '^(?P<entity>.*) (with|verb)-\d* (?P<op>operation-\d*) (?P<prop>propclass-\d*)$'),

            # comparisons
            # X prop of Y   e.g. is Paris the capital of France.
            # (80, '^(?P<entity>-\d*) (?P<prop>propclass-\d*) (of)-\d* (?P<entity>-\d*)$'),

            # verb propclass
            # sang Infinite Things
            (90, '^(?P<prop>verb-\d*) (of|in|for)-\d* (?P<entity>propclass-\d*)$'),

            # sang <X of/in Y> : nested object
            (95, '^(?P<prop>verb-\d*) (?P<entity>.*)$'),
            # (95, '^(?P<verb>verb-\d*) (?P<class>propclass-\d*) (of|for|in)-\d* (?P<class>propclass-\d*)$'),
            
           
            (100, '^(?P<when>when-\d*) (?P<subj>entity-\d*) (?P<prop>verb-\d*) (?P<obj>entity-\d*)$'),
            (105, '^(?P<when>when-\d*) (?P<subj>entity-\d*) (?P<prop>verb-\d*) (?P<entity>.*)$'), 
            
            # France population
            (110, '^(?P<entity>.*) (?P<prop>propclass-\d*)$'),
            # Friends theme_song
            (115, '^(?P<entity>propclass-\d*) (?P<prop>propclass-\d*)$'),

        ]

        alist_patterns = {

            10: {'h': '@op',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0',  't': '@time'},
            15: {'h': 'value',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0',  't': '@time'},
            20: {'h': '@op',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0'},
            25: {'h': 'value',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0'},

            30: {'h': '@op',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0',  't': '@time'},
            32: {'h': 'value',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0'},
            35: {'h': 'value',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0',  't': '@time'},
            40: {'h': '@op',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0'},
            45: {'h': 'value',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0'},

            50: {'h': '@op',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0',  't': '@time'},
            55: {'h': 'value',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0',  't': '@time'},

            60: {'$filter': [{'p': 'type', 'o': '@class'}, {'p': 'location', 'o': '@loc'}]},
            65: {'$filter': [{'p': 'type', 'o': '@class'}]},
            70: {'h': '@op', 's': '@entity', 'p': '@prop', 'o': '$y0', 'v': '$y0', 't': '@time'},
            75: {'h': '@op', 's': '@entity', 'p': '@prop', 'o': '$y0', 'v': '$y0'},
            
            90: {'h': 'value', 's': '?y0', 'p': '@prop', 'o': '@entity',  'v': '?y0'},
            95: {'h': 'value', 's': '?y0', 'p': '@prop', 'o': '@entity',  'v': '?y0'},
            
            100: {'h': 'value', 's': '@subj', 'p': '@prop', 'o': '@obj',  't': '?y0', 'v': '?y0'},
            105: {'h': 'value', 's': '@subj', 'p': '@prop', 'o': '@entity', 't': '?y0', 'v': '?y0'},

            110: {'h': 'value', 's': '@entity', 'p': '@prop', 'o': '?y0', 'v': '?y0'},
            115: {'h': 'value', 's': '@entity', 'p': '@prop', 'o': '?y0', 'v': '?y0'},
        }

        operator_mapping = {
            'largest': 'max', 'biggest': 'max', 'highest': 'max', 'maximum': 'max',
            'lowest': 'min', 'smallest': 'min', 'tiniest': 'min', 'minimum': 'min',
            'average': 'avg', 'mean': 'avg', 'total': 'value',
            'longest': 'min', 'shortest': 'min'
        }

        matched_pattern = 1
        kv_pairs = {'': _attr_value}
        
        for attr, attr_val in kv_pairs.items():
            curr_alist = []
            if len(attr_val.split()) < 1 and not isinstance(attr_val, dict) and not isinstance(attr_val, list):
                continue
            try:
                for reg_items in regex_patterns:
                    #print(reg_items)
                    idx = reg_items[0]
                    pattn = reg_items[1]
                    re.purge()
                    p = re.compile(pattn)
                    m = p.match(attr_val.strip())
                    s = p.sub('#', attr_val)
                    if m is not None and s == '#':
                        #print("matched...")
                        matched_pattern = idx
                        curr_alist = alist_patterns[idx]

                        for group_name, matched_str in m.groupdict().items():
                            for k, v in curr_alist.items():

                                if v == ('@' + group_name):
                                    token_idx = matched_str.split('-')

                                    if len(token_idx) == 2 and not (matched_pattern in [70, 75] and group_name == "entity"):
                                        curr_alist[k] = tokens[int(token_idx[1])][1]
                                    else:
                                        curr_alist[k] = "%" + matched_str
                            
                                    # if prop is plural, replace VALUE with VALUES op
                                    if v == '@prop' and curr_alist['h'] == 'value' and tokens[int(token_idx[1])][2] == 'NOUN:NNS':
                                        curr_alist['h'] = 'values'
                                    break
                                elif k == '$filter':
                                    for item in curr_alist[k]:
                                        for x, y in item.items():
                                            if y == ('@' + group_name):
                                                token_idx = matched_str.split('-')
                                                if len(token_idx) == 2:
                                                    item[x] = tokens[int(token_idx[1])][1]
                                                else:
                                                    curr_alist[k] = "%" + \
                                                        matched_str
                                                break
                        break
            except Exception as ex:
                print(ex)
            if 'h' in curr_alist and curr_alist['h'] not in  ['value', 'values']:
                curr_alist['h'] = operator_mapping[curr_alist['h']]
            alist = curr_alist
        return (alist, var_ctr, matched_pattern)

    def Sorting(self, lst):
        lst.sort(key=len)
        return lst
