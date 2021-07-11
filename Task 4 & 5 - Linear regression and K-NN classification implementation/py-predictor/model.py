from tkinter.constants import NONE
import pandas as pd
import pymysql
from pymysql.cursors import DictCursor

class Oglas:
    udaljenost: float
    kvadratura: float
    starost: int
    broj_soba: int
    spratnost: int

nekretnine = pd.DataFrame()
def import_data():
    global nekretnine
    if nekretnine.empty:
        con = pymysql.connect(
            host = 'localhost',
            user = 'root',
            password = '',
            db = 'nekretnine',
            charset = 'utf8',
            cursorclass = DictCursor)

        nekretnine = pd.read_sql(sql = 'SELECT * FROM nekretnina_subset', con = con, index_col = 'id')

        con.close()

        print(nekretnine)

def get_data():
    global nekretnine
    if nekretnine.empty:
        import_data()
    return nekretnine

def min_max(data: pd.DataFrame):
    return \
        data.min(), \
        data.max() - data.min(), \
        (data - data.min()) / (data.max() - data.min())

def max(data: pd.DataFrame):
    return \
        0.0, \
        data.max(), \
        data / data.max()

def mean(data: pd.DataFrame):
    return \
        data.mean(), \
        data.max() - data.min(), \
        (data - data.mean()) / (data.max() - data.min())

def standardization(data: pd.DataFrame):
    return \
        data.mean(), \
        data.std(), \
        (data - data.mean()) / data.std()

normalize_fn = min_max
nekretnine_normalized = pd.DataFrame()

def normalize_data(data, normalize = min_max):
    global normalize_fn
    normalize_fn = normalize
    _, _, data_normalized = normalize(data)
    return data_normalized

def get_normalized_data(normalize = min_max):
    global nekretnine_normalized
    if nekretnine_normalized.empty:
        _, _, nekretnine_normalized = normalize_data(get_data(), normalize)
    return nekretnine_normalized

def get_normalized_input(oglas: Oglas, normalize = None):
    global normalize_fn
    if normalize is None:
        normalize = normalize_fn
    decrementor, divisor, _ = normalize(nekretnine)
    series = series_from_oglas(oglas)
    tmp = ((series - decrementor) / divisor).values
    tmp[0] = 1
    return [tmp]

def oglas_from_series(row: pd.Series):
    oglas = Oglas()
    oglas.udaljenost = row.at['udaljenost']
    oglas.kvadratura = row.at['kvadratura']
    oglas.starost = row.at['starost']
    oglas.broj_soba = row.at['broj_soba']
    oglas.spratnost = row.at['spratnost']
    return oglas

def series_from_oglas(oglas: Oglas):
    return pd.Series(data = {
        'cena': 1,
        'udaljenost': oglas.udaljenost,
        'kvadratura': oglas.kvadratura,
        'starost': oglas.starost,
        'broj_soba': oglas.broj_soba,
        'spratnost': oglas.spratnost
    })