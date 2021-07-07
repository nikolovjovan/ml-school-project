from model import Oglas, get_data, get_normalized_data, min_max
import numpy as np

learned = False
alf = 0.1
lda = 0.1
iters = 1000
w_opt = np.ones([1, 6])
cost = np.zeros(iters)

def compute_cost(X, y, w):
    return np.sum(np.power(X @ w.T - y, 2)) / (2 * len(X))

def gradient_descent(X, y, w, alf, lda, iters):
    cost = np.zeros(iters) # da bismo imali uvid u poboljsanje algoritma
    for i in range(iters):
        w = w * (1 - alf * lda / len(X)) - (alf / len(X)) * np.sum((X @ w.T - y), axis = 0)
        cost[i] = compute_cost(X, y, w)
    return w, cost

def learn():
    global learned, w_opt
    if learned:
        return w_opt
    data = get_normalized_data(min_max)
    X = data.iloc[:, 1:6]
    ones = np.ones([X.shape[0], 1])
    X = np.concatenate((ones, X), axis = 1)
    y = get_data().iloc[:, 0:1].values
    global cost, alf, lda, iters
    w_opt, cost = gradient_descent(X, y, w_opt, alf, lda, iters)
    return w_opt

def predict_price(oglas: Oglas):
    w_opt = learn()
    global cost
    print(cost)
    return \
        w_opt[0][0] + \
        w_opt[0][1] * oglas.udaljenost + \
        w_opt[0][2] * oglas.kvadratura + \
        w_opt[0][3] * oglas.starost + \
        w_opt[0][4] * oglas.broj_soba + \
        w_opt[0][5] * oglas.spratnost