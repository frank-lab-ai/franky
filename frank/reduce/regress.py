'''
File: regress.py
Description: Linear regression reduce operation


'''
import SMART.Tagger.EDA
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from SMART.Reasoner.reasoner import *
from SMART.Methods.catalogue import *
from SMART.Tagger.tagger import *

from frank.alist import Alist
from frank.alist import Attributes as tt
from frank.alist import VarPrefix as vx
from frank.alist import Branching as br
from frank.alist import States as states
from frank.alist import NodeTypes as nt
from frank.util import utils
from frank.uncertainty.aggregateUncertainty import estimate_uncertainty
from frank.reduce import propagate
from frank.graph import InferenceGraph

from typing import List


def reduce(alist: Alist, children: List[Alist], G: InferenceGraph):
    X, y, data_pts = [], [], []

    for c in children:
        opVarValue = c.instantiation_value(c.get(tt.OPVAR))
        if utils.is_numeric(opVarValue) and utils.is_numeric(c.get(tt.TIME)):
            x_val = utils.get_number(c.get(tt.TIME), None)
            y_val = utils.get_number(opVarValue, None)
            X.append(x_val)
            y.append(y_val)
            data_pts.append([x_val, y_val])

    if len(X) == 1:
        # own_CoV = 1
        fnAndData = '{{"function":{coeffs}, "data":{data_pts}, "prediction":{prediction}}}'.format(
            coeffs = None, data_pts = data_pts, prediction = data_pts)
        alist.instantiate_variable(alist.get(tt.OPVAR), y[0])
        alist.set(tt.FNPLOT, fnAndData)
    else:
        df = pd.DataFrame({alist.get(tt.PROPERTY): y, tt.TIME: X})
        rs = new_reasoner()
        rs.state = initialise_state(rs.state, query_alist = {}, df = df,
            __tag_list_fields_extras = dict(Query = alist.get('cx')[3]['Query Tags'] + [])) # Add 'Multivariate', 'Refined' to force GLM

        rs.consecutive_steps([['Distribution']], [['Method']])

        method = fetch_tags_warn(rs, 'Method')
        mod = method_catalogue[method](rs)
        mod.apply(df)

        expl = mod.text_explanation()
        alist.set(tt.EXPLAIN, expl)

        x_predict = [utils.get_number(alist.get(tt.TIME), None)]
        prediction = mod.predict(pd.DataFrame({tt.TIME: x_predict}))

        # own_CoV = (abs(prediction['Upper'] - prediction['Lower']) / (2 * prediction['Pred']))[0]

        alist.instantiate_variable(alist.get(tt.OPVAR), prediction['Pred'][0])

        pl = mod.plot(plotly = True)
        alist.set(tt.FNPLOT, pl.to_json())

        ## Other possibly useful model info
        # mod.extract_params()

    child_CoV = estimate_uncertainty(children, len(data_pts) == len(children), alist.get(tt.OP), len(children))
    alist.instantiate_variable(tt.COV, child_CoV)# * own_CoV)

    return alist


