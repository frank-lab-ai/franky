'''
File: parser.py
Description: Template-based parser for NL queries.
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)
Copyright 2014 - 2020  Kobby K.A. Nuamah
'''

import datetime

import json
import requests
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
        #starttime = time.time()
        print(querystring)
        doc = Parser.nlp_lib(querystring)

        for token in doc:
            print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_)

        pos_mapper = {
            # 'NOUN:WP': 'wh',
            'ADP:IN': 'prep',
            'NOUN:NN': 'propclass',
            'PROPN:NNP': 'entity',
            'VERB:VBD': 'verb',
            'VERB:VBG': 'verb',
            'VERB:VBZ': 'verb',
            'ADJ:JJ': 'operation',
            'ADJ:JJS': 'operation',
            'ADJ:JJR': 'comparison',
            'NUM:CD': 'datetime'
        }

        # expand templates
        templates = [
            ['entity', '$propOfentity'],
            ['$propOfentity'],
            #['wh', '$propOfentity'],
            ['$propOfentity', '$compare', '$propOfentity']
        ]

        operation_triggers = [
            'total', 'average', 'mean']
        stop_words = ['is', 'the', 'was']

        mapped_terms = []
        mapped_terms2 = []
        skip_start_char = -1
        skip_end_char = -1
        in_compound = False
        in_jjphrase = False
        compound_NN = ''
        compound_PROPCLASS = ''

        for token in doc:
            if token.text in stop_words:
                continue
            if token.idx >= skip_start_char and token.idx <= skip_end_char:
                continue
            in_ent = False
            for ent in doc.ents:
                if token.idx >= ent.start_char and token.idx <= ent.end_char:
                    token_tags = token.pos_ + ':' + token.tag_
                    if token_tags in pos_mapper:
                        in_ent = True
                        skip_start_char = ent.start_char
                        skip_end_char = ent.end_char

                    mapped_terms.append(
                        [v for k, v in pos_mapper.items() if k == token_tags])
                    mapped_terms2.append([ent.text.replace('the', '').strip(
                    ) for k, v in pos_mapper.items() if k == token_tags])
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
                token_tags = token.pos_ + ':' + token.tag_
                if token.dep_ == 'compound' and in_compound == False:
                    in_compound = True
                    compound_NN = compound_PROPCLASS + token.text
                    compound_PROPCLASS = ''

                elif token.dep_ != 'compound' and in_compound == True:
                    compound_NN += ' ' + token.text
                    mapped_terms.append(
                        [v for k, v in pos_mapper.items() if k == token_tags])
                    mapped_terms2.append([compound_NN.strip()])
                    compound_NN = ''
                    in_compound = False

                else:
                    mapped_terms.append(
                        [v for k, v in pos_mapper.items() if k == token_tags])
                    mapped_terms2.append(
                        [compound_PROPCLASS + token.text for k, v in pos_mapper.items() if k == token_tags])
                    compound_PROPCLASS = ''

        # replace sequence of propclasses with a single propclass
        template_tokens = [
            item for sublist in mapped_terms for item in sublist]
        quest_tokens = [item for sublist in mapped_terms2 for item in sublist]
        for i in range(len(template_tokens)):
            if template_tokens[i] == 'prep':
                template_tokens[i] = quest_tokens[i]
        tokens_zip = list(zip(template_tokens, quest_tokens))
        print(template_tokens)
        print(quest_tokens)
        print(tokens_zip)
        try:
            query_frame = self.GenerateQueryFromRegex(
                quest_tokens, template_tokens, tokens_zip)
        except:
            query_frame = {}

        returnObj = {'question': querystring,
                     'template': template_tokens, 'alist': query_frame}
        return (returnObj)

    def GenerateQueryFromRegex(self, quest_tokens, template_tokens, tokens_zip):
        tokens_with_idx = ''
        for idx in range(len(template_tokens)):
            tokens_with_idx += template_tokens[idx] + '-' + str(idx) + ' '
        tokens_with_idx = tokens_with_idx.strip()

        alist = {}
        is_nested = True
        var_ctr = 3
        (alist, var_ctr, pattern) = self.create_alist(
            alist, tokens_with_idx, var_ctr, quest_tokens)
        queue = deque()
        queue = self.scan_alist(alist, queue)

        previous_pattern = pattern
        while queue:
            qitem = queue.pop()
            curr_alist = qitem[0]
            k = qitem[1]
            v = qitem[2]
            print("===gen===")
            print(v)
            print("===genEND===")
            if isinstance(v, str):
                if len(v.split()) > 0:
                    is_nested = True
                    (sub_alist, var_ctr, pattern) = self.create_alist(
                        {}, v, var_ctr, quest_tokens)

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

        print(alist)
        return alist

    def scan_alist(self, alist, queue):
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

    def create_alist(self, alist, _attr_value, var_ctr, quest_tokens):
        curr_year = str(datetime.datetime.now().year)
        regex_patterns = [
            # op X of Y in T
            (10, '^(?P<op>operation-\d*) (?P<prop>propclass-\d*) (of)-\d* (?P<entity>entity-\d*) (in|at)-\d* (?P<time>datetime-\d*)$'),
            # X of Y in T
            (15, '^(?P<prop>propclass-\d*) (of)-\d* (?P<entity>entity-\d*) (in|at)-\d* (?P<time>datetime-\d*)$'),
            # op X of  Y>
            (20, '^(?P<op>operation-\d*) (?P<prop>propclass-\d*) (of)-\d* (?P<entity>entity-\d*)$'),
            (25, '^(?P<prop>propclass-\d*) (of)-\d* (?P<entity>entity-\d*)$'),  # X of Y>


            # op X of <nested Y in T
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
            #(65, '^(?P<class>propclass-\d*) (with|verb)-\d* (?P<op>operation-\d*) (?P<prop>propclass-\d*) (in|at)-\d* (?P<time>datetime-\d*)$'),
            (70, '^(?P<entity>.*) (with|verb)-\d* (?P<op>operation-\d*) (?P<prop>propclass-\d*) (in|at)-\d* (?P<time>datetime-\d*)$'),
            (75, '^(?P<entity>.*) (with|verb)-\d* (?P<op>operation-\d*) (?P<prop>propclass-\d*)$'),

            # comparisons
            # X prop of Y   e.g. is Paris the capital of France.
            (80, '^(?P<entity>-\d*) (?P<prop>propclass-\d*) (of)-\d* (?P<entity>-\d*)$'),

        ]

        alist_patterns = {

            10:  {'h': '@op',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0',  't': '@time'},
            15:  {'h': 'value',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0',  't': '@time'},
            20:  {'h': '@op',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0'},
            25:  {'h': 'value',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0'},

            30:  {'h': '@op',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0',  't': '@time'},
            32:  {'h': 'value',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0'},
            35:  {'h': 'value',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0',  't': '@time'},
            40:  {'h': '@op',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0'},
            45:  {'h': 'value',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0'},

            50:  {'h': '@op',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0',  't': '@time'},
            55:  {'h': 'value',  'v': '?y0',  's': '@entity',  'p': '@prop',  'o': '?y0',  't': '@time'},

            60:  {'$filter': [{'p': 'type', 'o': '@class'}, {'p': 'location', 'o': '@loc'}]},
            65:  {'$filter': [{'p': 'type', 'o': '@class'}]},
            # 65:  {'h': '@op', 's': '?x3', 'p': '@prop', 'o': '$y0', 'v': '$y0', 't': '@time', '?x3':{'$filter': [{'p':'type', 'o': '@class'}]} },
            70:  {'h': '@op', 's': '@entity', 'p': '@prop', 'o': '$y0', 'v': '$y0', 't': '@time'},
            75:  {'h': '@op', 's': '@entity', 'p': '@prop', 'o': '$y0', 'v': '$y0'},
            # comparisons
            80: {}
        }

        operator_mapping = {
            'largest': 'max', 'biggest': 'max', 'highest': 'max', 'maximum': 'max',
            'lowest': 'min', 'smallest': 'min', 'tiniest': 'min', 'minimum': 'min',
            'average': 'avg', 'mean': 'avg', 'total': 'value',
            'longest': 'min', 'shortest': 'min'
        }

        matched_pattern = 1
        print(_attr_value)
        kv_pairs = {'': _attr_value}
        for attr, attr_val in kv_pairs.items():
            print("***")
            print(attr_val)
            if len(attr_val.split()) < 1 and not isinstance(attr_val, dict) and not isinstance(attr_val, list):
                continue

            for reg_items in regex_patterns:
                print(reg_items)
                idx = reg_items[0]
                pattn = reg_items[1]
                re.purge()
                p = re.compile(pattn)
                m = p.match(attr_val.strip())
                s = p.sub('#', attr_val)
                if m is not None and s == '#':
                    print("matched...")
                    matched_pattern = idx
                    curr_alist = alist_patterns[idx]
                    #curr_alist['pattern'] = idx

                    for group_name, matched_str in m.groupdict().items():
                        for k, v in curr_alist.items():

                            if v == ('@' + group_name):
                                token_idx = matched_str.split('-')

                                if len(token_idx) == 2 and not (matched_pattern in [70, 75] and group_name == "entity"):
                                    print("---")
                                    print(group_name)
                                    print(matched_str)
                                    print(token_idx)
                                    curr_alist[k] = quest_tokens[int(
                                        token_idx[1])]
                                    print(curr_alist[k])
                                else:
                                    curr_alist[k] = "%" + matched_str
                                    print(curr_alist[k])
                                break
                            elif k == '$filter':
                                for item in curr_alist[k]:
                                    for x, y in item.items():
                                        if y == ('@' + group_name):
                                            token_idx = matched_str.split('-')
                                            if len(token_idx) == 2:
                                                item[x] = quest_tokens[int(
                                                    token_idx[1])]
                                            else:
                                                curr_alist[k] = "%" + \
                                                    matched_str
                                            break
                        print(curr_alist)
                    break
            if 'h' in curr_alist and curr_alist['h'] != 'value':
                curr_alist['h'] = operator_mapping[curr_alist['h']]
            alist = curr_alist

        return (alist, var_ctr, matched_pattern)

    def Sorting(self, lst):
        lst.sort(key=len)
        return lst
