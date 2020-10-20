'''
File: nnpredict.py
Description: A neural network-based regression operation
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)

'''

# imports
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
# import keras
from sklearn.metrics import mean_absolute_error
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

np.random.seed(20)
# params
window_size = 3
epochs = 50
batch_size = 5
train_ratio = 0.7


def reduce(alist: Alist, children: List[Alist], G: InferenceGraph):
    # y_predict = None
    # X = []
    # y = []
    # data_pts = []
    # for c in children:
    #     opVarValue = c.instantiation_value(c.get(tt.OPVAR))
    #     if utils.is_numeric(opVarValue) and utils.is_numeric(c.get(tt.TIME)):
    #         x_val = utils.get_number(c.get(tt.TIME), None)
    #         y_val = utils.get_number(opVarValue, None)
    #         X.append(x_val)
    #         y.append(y_val)
    #         data_pts.append([x_val, y_val])

    # if len(data_pts) < window_size + 4:
    #   return None

    # nn = NeuralNetPredict(X, y)
    # nn.preprocess()
    # nn.train_mlp_model()
    # x_predict = utils.get_number(alist.get(tt.TIME), None)
    # predictions = nn.predict(x_predict)
    # y_predict = predictions[x_predict]
    # prediction = [x_predict, y_predict]
    # # coeffs = [v for v in reg.coef_]
    # # coeffs.insert(0, reg.intercept_)
    # # fnStr = 'LIN;' + ';'.join([str(v) for v in reg.coef_])
    # # fnAndData = \
    # #     """{{"function":{coeffs}, "data":{data_pts}, "prediction":{prediction}}}""".format(
    # #         coeffs=coeffs, data_pts=data_pts, prediction=prediction)

    # alist.instantiate_variable(alist.get(tt.OPVAR), y_predict)
    # # alist.set(tt.FNPLOT, fnAndData )

    # alist.instantiate_variable(tt.COV, estimate_uncertainty(
    #   children, len(data_pts)==len(children), alist.get(tt.OP), len(children)
    # ))
    return alist

# class NeuralNetPredict:

#   def __init__(self, X, y):
#     self.X = X
#     self.y = y
#     self.training_data = np.array([])
#     self.training_labels = np.array([])
#     self.test_data = np.array([])
#     self.test_labels = np.array([])
#     self.sequences = []
#     self.seq_X = []
#     self.test_seq_X = []
#     self.labels = []
#     self.labels_true = []
#     self.mae_noise_avg = 0
#     self.mae_true_avg = 0
#     self.mlp_model = None


#   def preprocess(self):
#     ''' preprocess dataset for learning and prediction '''
#     # create training data using a window of a sequence of 100 data points

#     for i in range(len(self.y)-(window_size)): # -1 to get a label for last training sequence
#       self.sequences.append(self.y[i:(i+window_size)])
#       self.labels.append(self.y[i+window_size])
#       self.labels_true.append(self.y[i+window_size])
#       self.seq_X.append(self.X[i+window_size])

#     # train with all data and predict using the last sequence
#     train_size = math.ceil(train_ratio * len(self.sequences))
#     test_size = len(self.sequences) - train_size
#     self.training_data = np.array(self.sequences[0:-test_size])
#     self.training_labels = np.array(self.labels[0:-test_size])
#     # print(len(sequences), train_size, test_size)
#     self.test_data = np.array(self.sequences[-test_size:])
#     self.test_labels = self.labels[-test_size:]
#     self.test_labels_true = self.labels_true[-test_size:]
#     self.test_seq_X = self.seq_X[-test_size:]
#     self.sequences = np.array(self.sequences)

#     # window sequence averages
#     label_avg = np.average(self.sequences,axis=1)
#     self.mae_noise_avg = mean_absolute_error(np.array(self.labels), label_avg)
#     self.mae_true_avg = mean_absolute_error(np.array(self.labels_true), label_avg)
#     label_avg = label_avg.reshape((label_avg.shape[0],))

#   def build_mlp_model(self, inputs, input_dim, output_size, neurons, activation='relu', optimizer='adam', loss='mae'):
#     ''' build and mlp model'''
#     model = keras.models.Sequential()
#     model.add(keras.layers.Dense(neurons, activation=activation, input_dim=input_dim))
#     # model.add(keras.layers.Dropout(0.1))
#     model.add(keras.layers.Dense(int(neurons/2)))
#     model.add(keras.layers.Dense(1))
#     model.compile(loss=loss, optimizer=optimizer)
#     return model


#   def train_mlp_model(self):
#     self.mlp_model = self.build_mlp_model(self.training_data, window_size, output_size=1, neurons=32)
#     mlp_history = self.mlp_model.fit(
#       self.training_data,
#       self.training_labels,
#       epochs=epochs ,
#       batch_size=batch_size,
#       verbose=1,
#       shuffle=False)


#   def predict(self, predict_X):
#     curr_prediction_sequence = self.sequences.tolist()[-1]
#     predicted_y_list = []
#     predicted_data = {}
#     max_X = max(self.X)
#     #create full sequence
#     for i in range(math.ceil(predict_X-max_X)):
#       prediction =  self.mlp_model.predict(np.array([np.array(curr_prediction_sequence)]))
#       prediction = prediction.tolist()[0][0]
#       predicted_data[max_X+i+1] = prediction
#       curr_prediction_sequence.append(prediction)
#       curr_prediction_sequence = curr_prediction_sequence[1: 1+window_size]

#     return predicted_data


#     # print(len(self.test_labels), len(predictions))
#     # predict_test = self.mlp_model.predict(self.test_data)
#     # self.plot(predictions, predict_test)


#   def plot(self, predictions, predict_test):
#     '''plot data and predictions'''
#     mae_noise_nn = mean_absolute_error(np.array(self.test_labels).reshape(len(self.test_labels),1), predict_test)
#     mae_true_nn = mean_absolute_error(np.array(self.test_labels_true).reshape(len(self.test_labels),1), predict_test)
#     print(f"MAE NN Noisy Data: {mae_noise_nn},  MAE NN True: {mae_true_nn}")
#     print(f"MAE AVG Noisy Data: {self.mae_noise_avg},  MAE AVG True: {self.mae_true_avg}")
#     plt.rcParams['figure.figsize'] = [25,12]
#     plt.plot(self.X, self.y, linestyle='--', linewidth='0.5', label='true_dist')
#     # plt.plot(self.X[0:math.ceil(train_ratio * len(self.X))] ,y[0:math.ceil(train_ratio * len(y))], label='noisy train data')
#     plt.plot(self.seq_X, predictions, label="train_predict_nn")
#     plt.plot(self.test_seq_X, predict_test, label="test_predict_nn")
#     plt.plot(self.test_seq_X, self.test_labels, '.', label="actual")
#     # plt.fill_between(X, y+(2*noise_stdev), y-(2*noise_stdev), color='grey',alpha=0.1 , label='2 st.dev')
#     plt.axvline(x=self.X[math.ceil(train_ratio * len(self.X))], color='r', linestyle='--', linewidth='0.5')
#     plt.title(f'Window size:{window_size}, MLP_MAE:{mae_noise_nn}, WINAVG_MAE={self.mae_noise_avg}', )
#     plt.legend()


# data = {2000:65, 2001: 63, 2002:65, 2003:64, 2004:67, 2005:69, 2006: 68, 2007:69, 2008:70, 2009:75, 2010: 76}

# nn = NeuralNetPredict(list(data.keys()), list(data.values()))
# nn.preprocess()
# nn.train_mlp_model()
# predict_X = 2015
# predictions = nn.predict(predict_X)
# print(predictions)
