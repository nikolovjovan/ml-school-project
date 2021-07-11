from model import Oglas, get_data, get_normalized_data, get_normalized_input, max, normalize_data
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge # Samo za validiranje performansi
from sklearn.metrics import mean_squared_error

# Hiperparametri modela

alf = 1 # alfa = brzina ucenja
lda = 0 # lambda - stepen regularizacije
iters = 1000 # broj iteracija
training_frac = 0.9 # udeo podataka koji se koristi za treniranje modela

# Parametri modela

w_opt = np.ones([1, 6])

# Jednom pokrecemo ucenje, nakon toga koristimo dobijene koeficijente

learned = False

# Podeljeni dataset-ovi

X_train_nn = None
X_train = None
y_train = None
X_test_nn = None
X_test = None
y_test = None

# Greske u train i test set-u

train_err = 0.0
test_err = 0.0

# sklearn.linear_model.LinearRegression

regr = None 

# Greske u train i test set-u

regr_train_err = 0.0
regr_test_err = 0.0

# sklearn.linear_model.Ridge

ridge = None 

# Greske u train i test set-u

ridge_train_err = 0.0
ridge_test_err = 0.0

# Kretanje cene tokom optimizacije modela

cost = np.zeros(iters)

def split_data(df: pd.DataFrame):
    df = pd.DataFrame(data = df) # iz nekog razloga DataFrame se pretvori u numpy.ndarray prilikom poziva...
    training_set = df.sample(frac = training_frac)
    return \
        training_set.values, \
        df.drop(training_set.index).values

def prepare_datasets():
    global X_train_nn, X_train, y_train, X_test_nn, X_test, y_test
    if X_train_nn is None or X_train is None or y_train is None or X_test_nn is None or X_test is None or y_test is None:
        # Normalizovanje podataka modifikovanom max normalizacijom (min-max gde je min podrazumevano 0)
        # Koristi se ova normalizacija kako bi lakse mogli da normalizujemo ulazne podatke za predikciju...
        #
        data = get_data()
        data = data.loc[(data["cena"] / data["kvadratura"] >= 500) & (data["cena"] / data["kvadratura"] <= 5000)]
        data = data.loc[(data["cena"] >= 30000) & (data["cena"] <= 300000)]
        # data = data.loc[data["broj_soba"] <= 5]

        # Izdvajanje ciljane promenljive (cene) iz nenormalizovanih podataka
        #
        y = data.iloc[:, 0:1]

        print("Broj filtriranih podataka:", data.shape[0])

        # Izdvajanje odlika (pre podele na train-test)
        #
        X = data.iloc[:, 1:6]

        # Dodavanje nulte odlike (vrednost 1) zbog jednostavnosti operacija sa vektorima
        #
        ones = np.ones([X.shape[0], 1])
        X = np.concatenate((ones, X), axis = 1)

        # Podela podataka za treniranje i testiranje
        #
        X_train_nn, X_test_nn = split_data(X)
        y_train, y_test = split_data(y)

        # Normalizovanje podataka max normalizacijom (0, 1)
        #
        X_train = normalize_data(X_train_nn, max)
        X_test = normalize_data(X_test_nn, max)

def compute_cost(X, y, w, lda):
    # print('X', X)
    # print('y', y)
    # print('lda', lda)
    # print('[X @ w.T - y] ^ 2', np.power(X @ w.T - y, 2))
    # print('SUM([X @ w.T - y] ^ 2)', np.sum(np.power(X @ w.T - y, 2), axis = 0))
    # print('w ^ 2', np.power(w, 2))
    # print('SUM(w ^ 2)', np.sum(np.power(w, 2), axis = 0))
    # print('lda @ SUM(w ^ 2)', lda @ np.sum(np.power(w, 2), axis = 0))
    return (np.sum(np.power(X @ w.T - y, 2)) + lda @ np.sum(np.power(w, 2), axis = 0)) / (2 * len(X))

def gradient_descent(X, y, w, alf, lda, iters):
    cost = np.zeros(iters) # da bismo imali uvid u poboljsanje algoritma
    # print('w0', w)
    # print('cost0', compute_cost(X, y, w, lda))
    # print('X[0]', X[0], 'y[0]', y[0])
    for i in range(iters):
        # print('w.T', w.T)
        # print('X @ w.T', X @ w.T)
        # print('X @ w.T - y', X @ w.T - y)
        # print('(X @ w.T - y) * X', (X @ w.T - y) * X)
        # print('alf / len(X)', alf / len(X))
        # print('SUM((X @ w.T - y) * X)', np.sum(X * (X @ w.T - y), axis = 0))
        # print('(alf / len(X)) * SUM((X @ w.T - y) * X)', (alf / len(X)) * np.sum(X * (X @ w.T - y), axis = 0))
        w = w * (1 - alf * lda / len(X)) - (alf / len(X)) * np.sum(X * (X @ w.T - y), axis = 0)
        # print('w', w)
        # print('compute_cost')
        # print()
        cost[i] = compute_cost(X, y, w, lda)
        # print(f"cost[{i}] = {cost[i]}")
        # print()
    return w, cost

def rmse(y_act, y_exp):
    return np.average(np.sqrt(np.average((y_act - y_exp) ** 2, axis = 0)))

def predict(X, w = None):
    if w is None:
        global w_opt
        w = w_opt
    y = np.zeros(len(X))
    for i in range(len(X)):
        y[i] = np.sum(w * X[i], axis = 1)[0]
    return y

def learn():
    global learned, w_opt, regr, ridge

    # Ako je vec jednom izvrseno ucenje, vrati optimalne koeficijente...
    #
    if learned:
        return w_opt, regr, ridge

    # Skupovi podataka se pripremaju samo jednom...
    #
    prepare_datasets()

    global cost, alf, lda, iters, X_train, y_train, X_test, y_test

    # Kreiranje lambda vektora da bi se izbegla regularizacija nulte odlike (konstante)
    #
    lda_vec = np.full([1, X_train.shape[1]], lda)
    lda_vec[0][0] = 0 # nulti clan nije regularizovan

    # Pokretanje ucenja
    #
    w_opt, cost = gradient_descent(X_train, y_train, w_opt, alf, lda_vec, iters)
    print('My coefficients:', w_opt)

    # Referentna implementacija linearne regresije (bez regularizacije)
    #
    regr = LinearRegression()
    regr.fit(X_train, y_train)
    print('LinearRegression coefficients:', regr.coef_)

    # Referentna implementacija grebene regresije
    #
    ridge = Ridge(alpha = lda) # stepen regularizacije, sklearn to zove alpha
    ridge.fit(X_train, y_train)
    print('Ridge coefficients:', ridge.coef_)

    learned = True # YOLO (You Only LEARN Once)

    # Testiranje na podacima za ucenje i testiranje zbog provere performansi
    #
    global train_err, test_err, regr_train_err, regr_test_err, ridge_train_err, ridge_test_err

    train_err = rmse(predict(X_train), y_train)
    test_err = rmse(predict(X_test), y_test)

    print('Train err:', train_err, 'Test err:', test_err)
    print('sklearn Train err:', mean_squared_error(predict(X_train), y_train, squared = False), 'sklearn Test err:', mean_squared_error(predict(X_test), y_test, squared = False))

    regr_train_err = rmse(regr.predict(X_train), y_train)
    regr_train_err = rmse(regr.predict(X_test), y_test)

    print('Regr train err:', regr_train_err, 'Regr test err:', regr_test_err)
    print('sklearn Regr train err:', mean_squared_error(regr.predict(X_train), y_train, squared = False), 'sklearn Regr test err:', mean_squared_error(regr.predict(X_test), y_test, squared = False))

    ridge_train_err = rmse(ridge.predict(X_train), y_train)
    ridge_test_err = rmse(ridge.predict(X_test), y_test)

    print('Ridge train err:', ridge_train_err, 'Ridge trr:', ridge_test_err)
    print('sklearn Ridge train err:', mean_squared_error(ridge.predict(X_train), y_train, squared = False), 'sklearn Ridge test err:', mean_squared_error(ridge.predict(X_test), y_test, squared = False))

    return w_opt, regr, ridge

def predict_price(oglas: Oglas):
    w_opt, regr, ridge = learn()
    norm = get_normalized_input(oglas) #, normalize = lambda _: (0, 1, 0))
    print("Normalized input:", norm[0])
    print('sklearn.linear_model.LinearRegression:', regr.predict(norm)[0][0])
    print('sklearn.linear_model.Ridge:', ridge.predict(norm)[0][0])
    price = predict(norm, w_opt)[0]
    print('My implementation:', price)
    return price