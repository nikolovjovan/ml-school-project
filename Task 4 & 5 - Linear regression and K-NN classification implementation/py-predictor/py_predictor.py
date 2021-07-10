from model import Oglas, import_data
import linreg as lr
from linreg import predict_price, iters, prepare_datasets
from knn import cls_names, calculate_k, chebyshev, euclid, manhattan, most_probable_class, predict_class

from tkinter import *
import numpy as np
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt

def create_oglas():
    oglas = Oglas()
    oglas.udaljenost = float(udaljenost.get()) if len(udaljenost.get()) > 0 else 0.0
    oglas.kvadratura = float(kvadratura.get()) if len(kvadratura.get()) > 0 else 0.0
    oglas.starost = int(starost.get()) if len(starost.get()) > 0 else 0
    oglas.broj_soba = int(broj_soba.get()) if len(broj_soba.get()) > 0 else 1
    oglas.spratnost = int(spratnost.get()) if len(spratnost.get()) > 0 else 0
    return oglas

def plot_regression_lines(x, y, w, data, color, label, **kwargs):
    x_max = x.max()
    x_axis = np.arange(0, x_max, x_max / 10000)
    a = w[data.columns.get_loc(x.name)]
    b = w[0]
    line = lambda x: a * x + b
    # Ne pokrece se regresija za pojedinacne odlike vec se na osnovu regresije za sve odlike iscrtavaju uocene zavisnosti
    # Potrebno je skaliranje kako bi se rezultati mogli uociti na grafiku
    #
    a *= 30
    y_axis = line(x_axis)
    ax = plt.gca()
    ax.plot(x_axis, y_axis, color = color, label = label)
    ax.legend()

def pairplot(X, y, training = True):
    dfx = pd.DataFrame(X, columns = [
        'visak',
        'udaljenost',
        'kvadratura',
        'starost',
        'broj_soba',
        'spratnost'
    ])
    dfy = pd.DataFrame(y, columns = ['cena'])

    data = pd.concat([dfx, dfy], axis = 1)

    g = sb.pairplot(
        data,
        x_vars = [
            'udaljenost',
            'kvadratura',
            'starost',
            'broj_soba',
            'spratnost'
        ],
        y_vars = 'cena',
        kind = 'scatter',
        plot_kws = { "s" : 5 })

    g.fig.suptitle(("Training" if training else "Testing") + " set")
    g.fig.canvas.manager.set_window_title("Grafik zavisnosti cene od odlika")

    if lr.learned:
        g.map(plot_regression_lines, w = lr.w_opt[0], data = data, color = "tab:green", label = "My regression")
        g.map(plot_regression_lines, w = lr.regr.coef_[0], data = data, color = "tab:orange", label = "sklearn LinearRegression")
        g.map(plot_regression_lines, w = lr.ridge.coef_[0], data = data, color = "tab:red", label = "sklearn Ridge")
        g.fig.legend(handles = g._legend_data.values(), labels = g._legend_data.keys(), loc = "upper right")

    plt.tight_layout()
    plt.ion()
    plt.show()

def get_class_name(cls_id):
    return cls_names[cls_id] if cls_id >= 0 and cls_id < 5 else "nevalidna klasa"

def show_plots():
    prepare_datasets()
    pairplot(lr.X_train, lr.y_train)
    pairplot(lr.X_test, lr.y_test, False)

def exec_lin_reg():
    rezultatframe.grid_remove()
    oglas = create_oglas()

    rezultat.set(f"Predvidjena cena: {predict_price(oglas):.2f} EUR")
    rezultatframe.grid()

    fig = plt.figure()
    fig.canvas.manager.set_window_title("Grafik zavisnosti greske modela od trenutne iteracije")
    ax = fig.add_subplot(111)
    ax.plot(np.arange(iters), lr.cost, 'r')
    ax.set_xlabel('Broj iteracija')
    ax.set_ylabel('Greska modela')

    plt.tight_layout()
    plt.ion()
    plt.show()

def get_dist_fn(dist_fn_name):
    if dist_fn_name == "Euclid":
        return euclid
    elif dist_fn_name == "Manhattan":
        return manhattan
    elif dist_fn_name == "Chebyshev":
        return chebyshev
    # use Euclid distance by default
    return euclid

def exec_knn():
    rezultatframe.grid_remove()
    oglas = create_oglas()

    verovatnoce = predict_class(
        int(k.get()) if len(k.get()) > 0 else calculate_k(),
        oglas,
        get_dist_fn(fja_rastojanja.get()))

    predvidjena_klasa = most_probable_class(verovatnoce)
    rezultat.set(f"Predvidjena klasa: {predvidjena_klasa} - {get_class_name(predvidjena_klasa)}")
    rezultatframe.grid()

    fig = plt.figure()
    fig.canvas.manager.set_window_title("Verovatnoce cenovnih klasa")
    ax = fig.add_subplot(111)
    verovatnoce = [verovatnoca * 100 for verovatnoca in verovatnoce]
    colors = np.full(len(verovatnoce), "tab:blue")
    colors[np.argmax(verovatnoce)] = "tab:red"
    ax.bar(cls_names, verovatnoce, color = colors)
    ax.set_ylim([0, 100])
    ax.set_xticklabels(cls_names, rotation = 45, rotation_mode = "anchor", ha = "right")
    ax.set_ylabel('Verovatnoca [%]')

    plt.tight_layout()
    plt.ion()
    plt.show()

# Importovanje dataset-a

import_data()

# Kreiranje prozora aplikacije

window = Tk()
window.title("Prediktor cene/cenovne klase nekretnine")
window.minsize(350, 250)
window.wm_resizable(False, False)

# Dodavanje uputstva

Label(window, text = "Uneti karakteristike nekretnine pa pokrenuti regresiju/klasifikaciju.").grid(column = 0, row = 0)

# Dodavanje dela prozora za unos oglasa

adframe = Frame(window)
adframe.grid(column = 0, row = 1)

Label(adframe, text = "Udaljenost od centra Beograda [km]:", justify = RIGHT).grid(column = 0, row = 0, sticky = E)
udaljenost = StringVar()
udaljenost.set("0")
Entry(adframe, textvariable = udaljenost).grid(column = 1, row = 0, sticky = W)

Label(adframe, text = "Kvadratura [m^2]:", justify = RIGHT).grid(column = 0, row = 1, sticky = E)
kvadratura = StringVar()
kvadratura.set("0")
Entry(adframe, textvariable = kvadratura).grid(column = 1, row = 1, sticky = W)

Label(adframe, text = "Starost [godina]:", justify = RIGHT).grid(column = 0, row = 2, sticky = E)
starost = StringVar()
starost.set("0")
Spinbox(adframe, from_ = -10, to = 150, textvariable = starost).grid(column = 1, row = 2, sticky = W)

Label(adframe, text = "Broj soba:", justify = RIGHT).grid(column = 0, row = 3, sticky = E)
broj_soba = StringVar()
broj_soba.set("0")
Spinbox(adframe, from_ = 1, to = 1000, textvariable = broj_soba).grid(column = 1, row = 3, sticky = W)

Label(adframe, text = "Spratnost:", justify = RIGHT).grid(column = 0, row = 4, sticky = E)
spratnost = StringVar()
spratnost.set("0")
Spinbox(adframe, from_ = 0, to = 100, textvariable = spratnost).grid(column = 1, row = 4, sticky = W)

Label(adframe, text = "K (za K-NN):", justify = RIGHT).grid(column = 0, row = 5, sticky = E)
k = StringVar()
k.set(str(calculate_k()))
Spinbox(adframe, from_ = 1, to = 10000, textvariable = k).grid(column = 1, row = 5, sticky = W)

Label(adframe, text = "Funkcija rastojanja:", justify = RIGHT).grid(column = 0, row = 6, sticky = E)
fja_rastojanja = StringVar()
fja_rastojanja.set("Manhattan")
OptionMenu(adframe, fja_rastojanja, "Manhattan", *["Euclid", "Chebyshev"]).grid(column = 1, row = 6, sticky = EW)

# Dodavanje dugmeta za crtanje grafika

Button(window, text = "Iscrtaj grafike zavisnosti", command = show_plots).grid(column = 0, row = 2)

# Dodavanje dugmica za pokretanje regresije/klasifikacije

btnframe = Frame(window)
btnframe.grid(column = 0, row = 3)
Button(btnframe, text = "Linearna regresija", command = exec_lin_reg).grid(column = 0, row = 0)
Button(btnframe, text = "K-NN klasifikacija", command = exec_knn).grid(column = 1, row = 0)

# Dodavanje rezultata linearne regresije/K-NN klasifikacije

rezultatframe = Frame(window)
rezultatframe.grid(column = 0, row = 4)
rezultat_info = StringVar()
rezultat_info.set("")
Label(rezultatframe, textvariable = rezultat_info).grid(column = 0, row = 0)
rezultat = StringVar()
rezultat.set("")
Label(rezultatframe, textvariable =  rezultat).grid(column = 1, row = 0)
rezultatframe.grid_remove()

# Pokretanje glavne petlje aplikacije

window.mainloop()