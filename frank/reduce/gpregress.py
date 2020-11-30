'''
File: gpregress.py
Description: Basic Gaussian Process Regression reduce operation (with exponential kernel)


'''
import datetime
import time
import numpy as np
import matplotlib.pyplot as pl
import GPy

from typing import List
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


def reduce(alist: Alist, children: List[Alist], G: InferenceGraph):
    allNumeric = True
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
        else:
            allNumeric = False
    X = np.array(X)
    y = np.array(y)

    x_to_predict = utils.get_number(alist.get(tt.TIME), None)
    if not x_to_predict:
        return None
    else:
        x_to_predict = np.array([x_to_predict])

    gp_prediction = do_gpregress(
        X, y, x_to_predict, (np.max(y)-np.min(y))**2, 1)

    if gp_prediction is None:
        return None

    y_predict = gp_prediction[0]['y']
    try:
        prediction = [x_to_predict, y_predict]
        alist.instantiate_variable(alist.get(tt.OPVAR), y_predict)
        alist.instantiate_variable(tt.COV, gp_prediction[0]['stdev']/y_predict)

        alist.instantiate_variable(tt.COV, estimate_uncertainty(
            children, allNumeric, alist.get(tt.OP), len(children)
        ))
    except Exception as ex:
        print(ex)
        return None

    return alist


def do_gpregress(observed_X, observed_Y, prediction_X, noise_var, len_scale):
    X = observed_X.reshape(-1, 1)
    Y = observed_Y.reshape(-1, 1)
    Xp = prediction_X.reshape(-1, 1)
    # kernel  = GPy.kern.RBF(input_dim=1, variance= noise_var, lengthscale=len_scale)
    # kernel with automatic relevance determination (ARD)
    try:
        SQE = GPy.kern.RBF(input_dim=1, variance=noise_var, ARD=True) 
        LIN = GPy.kern.Linear(input_dim=1)
        PER = GPy.kern.StdPeriodic(input_dim=1)
        RQ = GPy.kern.RatQuad(input_dim=1) 
        kernel = (SQE * LIN) + (SQE * RQ) + PER # using default kernel params
        #kernel  = GPy.kern.RBF(input_dim=1, variance=np.var(Y), lengthscale= (np.max(Y)-np.min(Y))/2)
        # kernel = squared_exp #+ periodic
        m = GPy.models.GPRegression(X, Y, kernel)
        m.optimize(max_iters=1000)
    except Exception as ex:
        print(str(ex))
        return None

    Yp, Vp = m.predict(Xp)

    all_Xs = X.flatten().tolist()+Xp.flatten().tolist()
    all_Ys = Y.flatten().tolist()+Yp.flatten().tolist()
    plot_limits = np.array(
        [[min(all_Xs), min(all_Ys)], [max(all_Xs), max(all_Ys)]])
    x_limits = np.array([min(all_Xs)-1, max(all_Xs)+1])

    fig = m.plot(plot_limits=x_limits)
    pl.plot(Xp, Yp, 'or', ms=7)
    st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
    pl.legend().remove()
    pl.savefig("plot-" + st + ".jpg")

    # prepare result to be returned
    predictions = []
    mu_flat = Yp.ravel().tolist()
    s_flat = ((Vp**0.5)).ravel().tolist()

    for i in range(0, len(mu_flat)):
        predictions.append(
            {'x': prediction_X[i],
             'y': mu_flat[i],
             'stdev': s_flat[i]})

    return predictions
