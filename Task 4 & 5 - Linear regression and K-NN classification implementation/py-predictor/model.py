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

def oglas_from_row(row):
    oglas = Oglas()
    oglas.udaljenost = row.at['udaljenost']
    oglas.kvadratura = row.at['kvadratura']
    oglas.starost = row.at['starost']
    oglas.broj_soba = row.at['broj_soba']
    oglas.spratnost = row.at['spratnost']
    return oglas