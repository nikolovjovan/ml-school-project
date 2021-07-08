from model import Oglas, get_data, get_normalized_data, min_max
import numpy as np

learned = False

# Hiperparametri modela

alf = 1    # alfa = brzina ucenja
lda = 5    # lambda - stepen regularizacije
iters = 1000 # broj iteracija

# Parametri modela

w_opt = np.ones([1, 6])

# Kretanje cene tokom optimizacije modela

cost = np.zeros(iters)

def compute_cost(X, y, w, lda):
    # print('X', X)
    # print('y', y)
    # print('w', w)
    # print('lda', lda)
    # print('[X @ w.T - y] ^ 2', np.power(X @ w.T - y, 2))
    # print('SUM([X @ w.T - y] ^ 2)', np.sum(np.power(X @ w.T - y, 2), axis = 0))
    # print('w ^ 2', np.power(w, 2))
    # print('SUM(w ^ 2)', np.sum(np.power(w, 2), axis = 0))
    # print('lda @ SUM(w ^ 2)', lda @ np.sum(np.power(w, 2), axis = 0))
    return (np.sum(np.power(X @ w.T - y, 2)) + lda @ np.sum(np.power(w, 2), axis = 0)) / (2 * len(X))

def gradient_descent(X, y, w, alf, lda, iters):
    cost = np.zeros(iters) # da bismo imali uvid u poboljsanje algoritma
    # print('lda', lda)
    # print('gd', 1 - alf * lda / len(X))
    # print('X', X)
    # print('y', y)
    # print('w before', w)
    # print('w', w * (1 - alf * lda / len(X)))
    # print('X @ w.T', X @ w.T)
    # print('X @ w.T - y', X @ w.T - y)
    # print('X * (X @ w.T - y)', X * (X @ w.T - y))

    # compute_cost(X, y, w, lda)
    for i in range(iters):
        w = w * (1 - alf * lda / len(X)) - (alf / len(X)) * np.sum(X * (X @ w.T - y), axis = 0)
        cost[i] = compute_cost(X, y, w, lda)
    return w, cost

def learn():
    global learned, w_opt
    if learned:
        return w_opt
    data = get_normalized_data(min_max)
    print(data)
    print(get_data().max())
    X = data.iloc[:, 1:6]
    ones = np.ones([X.shape[0], 1])
    X = np.concatenate((ones, X), axis = 1)
    y = get_data().iloc[:, 0:1].values
    global cost, alf, lda, iters
    lda_vec = np.full([1, X.shape[1]], lda)
    lda_vec[0][0] = 0 # nulti clan nije regularizovan
    w_opt, cost = gradient_descent(X, y, w_opt, alf, lda_vec, iters)
    return w_opt

def predict_price(oglas: Oglas):
    w_opt = learn()
    print(w_opt)
    # global cost
    # print(cost)
    return \
        w_opt[0][0] + \
        w_opt[0][1] * oglas.udaljenost + \
        w_opt[0][2] * oglas.kvadratura + \
        w_opt[0][3] * oglas.starost + \
        w_opt[0][4] * oglas.broj_soba + \
        w_opt[0][5] * oglas.spratnost