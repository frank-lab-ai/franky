'''
File: regress.py
Description: Linear regression reduce operation


'''
from typing import List

import numpy as np
from sklearn.linear_model import LinearRegression

from frank.alist import Alist
from frank.alist import Attributes as tt
from frank.alist import Branching as br
from frank.alist import NodeTypes as nt
from frank.alist import States as states
from frank.alist import VarPrefix as vx
from frank.graph import InferenceGraph
from frank.reduce import propagate
from frank.uncertainty.aggregateUncertainty import estimate_uncertainty
from frank.util import utils


def reduce(alist: Alist, children: List[Alist], G: InferenceGraph):
    y_predict = None
    X = []
    y = []
    data_pts = []
    for c in children:
        opVarValue = c.instantiation_value(c.get(tt.OPVAR))
        if utils.is_numeric(opVarValue) and utils.is_numeric(c.get(tt.TIME)):
            x_val = utils.get_number(c.get(tt.TIME), None)
            y_val = utils.get_number(opVarValue, None)
            X.append([x_val])
            y.append(y_val)
            data_pts.append([x_val, y_val])
    X = np.array(X)
    y = np.array(y)
    reg = LinearRegression().fit(X, y)
    x_predict = utils.get_number(alist.get(tt.TIME), None)
    y_predict = reg.predict(np.array([[x_predict]]))[0]
    prediction = [x_predict, y_predict]
    coeffs = [v for v in reg.coef_]
    coeffs.insert(0, reg.intercept_)
    fnStr = 'LIN;' + ';'.join([str(v) for v in reg.coef_])
    fnAndData = \
        """{{"function":{coeffs}, "data":{data_pts}, "prediction":{prediction}}}""".format(
            coeffs=coeffs, data_pts=data_pts, prediction=prediction)

    alist.instantiate_variable(alist.get(tt.OPVAR), y_predict)
    alist.set(tt.FNPLOT, fnAndData)

    alist.instantiate_variable(tt.COV, estimate_uncertainty(
        children, len(data_pts) == len(
            children), alist.get(tt.OP), len(children)
    ))
    return alist
