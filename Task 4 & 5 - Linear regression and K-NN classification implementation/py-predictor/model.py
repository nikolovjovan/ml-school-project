import pandas as pd
import pymysql
from pandas.core.frame import DataFrame
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

def min_max(data: DataFrame):
    return (data - data.min()) / (data.max() - data.min())

def mean(data: DataFrame):
    return (data - data.mean()) / (data.max() - data.min())

def standardization(data: DataFrame):
    return (data - data.mean()) / data.std()

normalize_fn = standardization
nekretnine_normalized = pd.DataFrame()

def get_normalized_data(normalize = standardization):
    global normalize_fn
    global nekretnine_normalized
    if nekretnine_normalized.empty or normalize_fn != normalize:
        normalize_fn = normalize
        nekretnine_normalized = normalize(get_data())
    return nekretnine_normalized

def oglas_from_row(row):
    oglas = Oglas()
    oglas.udaljenost = row.at['udaljenost']
    oglas.kvadratura = row.at['kvadratura']
    oglas.starost = row.at['starost']
    oglas.broj_soba = row.at['broj_soba']
    oglas.spratnost = row.at['spratnost']
    return oglas