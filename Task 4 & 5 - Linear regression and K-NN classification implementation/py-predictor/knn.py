from model import Oglas, get_data, oglas_from_row
from numpy import exp2, sqrt

# Cenovne klase:
# 0: manje od 49 999 EUR
# 1: izmedju 50 000 i 99 999 EUR
# 2: izmedju 100 000 i 149 999 EUR
# 3: izmedju 150 000 EUR i 199 999 EUR
# 4: 200 000 EUR ili vise

coef = Oglas()
coef.udaljenost = 1.1
coef.kvadratura = 0.3
coef.starost = 0.7
coef.broj_soba = 1.4
coef.spratnost = 0.5

def calculate_k():
    return int(sqrt(get_data().shape[0]))

def manhattan(a: Oglas, b: Oglas):
    return \
        coef.udaljenost * abs(a.udaljenost - b.udaljenost) + \
        coef.kvadratura * abs(a.kvadratura - b.kvadratura) + \
        coef.starost * abs(a.starost - b.starost) + \
        coef.broj_soba * abs(a.broj_soba - b.broj_soba) + \
        coef.spratnost * abs(a.spratnost - b.spratnost)

def euclid(a: Oglas, b: Oglas):
    return sqrt( \
        exp2(coef.udaljenost * (a.udaljenost - b.udaljenost)) + \
        exp2(coef.kvadratura * (a.kvadratura - b.kvadratura)) + \
        exp2(coef.starost * (a.starost - b.starost)) + \
        exp2(coef.broj_soba * (a.broj_soba - b.broj_soba)) + \
        exp2(coef.spratnost * (a.spratnost - b.spratnost)))

def chebyshev(a: Oglas, b: Oglas):
    distances = [ \
        coef.udaljenost * abs(a.udaljenost - b.udaljenost), \
        coef.kvadratura * abs(a.kvadratura - b.kvadratura), \
        coef.starost * abs(a.starost - b.starost), \
        coef.broj_soba * abs(a.broj_soba - b.broj_soba), \
        coef.spratnost * abs(a.spratnost - b.spratnost)]
    return max(distances)

def get_class(cena):
    if cena < 50000:
        return 0
    elif cena < 100000:
        return 1
    elif cena < 150000:
        return 2
    elif cena < 200000:
        return 3
    return 4

def most_probable_class(probabilities):
    res = 0
    maxval = -1
    for i in range(len(probabilities)):
        if probabilities[i] > maxval:
            maxval = probabilities[i]
            res = i
    return res

def predict_class(k: int, oglas: Oglas, dist_fn = manhattan):
    distances = []
    nekretnine = get_data()
    if k > nekretnine.shape[0]:
        print(f'Greska! K = {k} > {nekretnine.shape[0]} (broj elemenata skupa za obucavanje). Smanjujem K...')
        k = nekretnine.shape[0]
        print(f'K = {k}')
    for i in range(nekretnine.shape[0]):
        row = nekretnine.iloc[i]
        distances.append((dist_fn(oglas, oglas_from_row(row)), get_class(row.at['cena'])))
    distances.sort(key = lambda tup: tup[0])
    probabilities = [ 0, 0, 0, 0, 0 ] # init counts for each class to 0
    for i in range(k):
        probabilities[distances[i][1]] += 1
    for i in range(len(probabilities)):
        probabilities[i] /= k
    return probabilities