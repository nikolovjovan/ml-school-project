from model import Oglas, import_data
import linreg as lr
from linreg import predict_price, iters, prepare_datasets
import knn
from knn import cls_names, calculate_k, chebyshev, euclid, manhattan, most_probable_class, predict_class

import tkinter as tk
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

    if training is not None:
        g.fig.suptitle(("Training" if training else "Testing") + " set")
    g.fig.canvas.manager.set_window_title("Grafik zavisnosti cene od odlika")

    if training is not None and lr.learned:
        g.map(plot_regression_lines, w = lr.w_opt[0], data = data, color = "tab:green", label = "My regression")
        g.map(plot_regression_lines, w = lr.regr.coef_[0], data = data, color = "tab:orange", label = "sklearn LinearRegression")
        g.map(plot_regression_lines, w = lr.ridge.coef_[0], data = data, color = "tab:red", label = "sklearn Ridge")
        g.fig.legend(handles = g._legend_data.values(), labels = g._legend_data.keys(), loc = "upper right")

    plt.tight_layout()
    plt.ion()
    plt.show()

def show_plots():
    prepare_datasets()
    pairplot(np.concatenate((lr.X_train, lr.X_test), axis = 0), np.concatenate((lr.y_train, lr.y_test), axis = 0), None)
    pairplot(lr.X_train, lr.y_train)
    pairplot(lr.X_test, lr.y_test, False)

    if lr.learned:
        fig = plt.figure()
        fig.canvas.manager.set_window_title("Grafik zavisnosti greske modela od trenutne iteracije")
        ax = fig.add_subplot(111)
        ax.plot(np.arange(iters), lr.cost, 'r')
        ax.set_xlabel('Broj iteracija')
        ax.set_ylabel('Greška modela')

        plt.tight_layout()
        plt.ion()
        plt.show()

def exec_lin_reg():
    rezultatframe.grid_remove()
    rezultat.set(f"Predviđena cena: {predict_price(create_oglas()):.2f} EUR")
    rezultatframe.grid()

def get_dist_fn(dist_fn_name):
    if dist_fn_name == "Euclid":
        return euclid
    elif dist_fn_name == "Manhattan":
        return manhattan
    elif dist_fn_name == "Chebyshev":
        return chebyshev
    # use Euclid distance by default
    return euclid

def get_class_name(cls_id):
    return cls_names[cls_id] if cls_id >= 0 and cls_id < 5 else "nevalidna klasa"

def exec_knn(k, dist_fn):
    rezultatframe.grid_remove()
    oglas = create_oglas()

    verovatnoce, prosecna_cena = predict_class(
        int(k) if len(k) > 0 else calculate_k(),
        oglas,
        dist_fn)

    predvidjena_klasa = most_probable_class(verovatnoce)
    rezultat.set(f"Predviđena klasa: {predvidjena_klasa} - {get_class_name(predvidjena_klasa)}\nProsečna cena: {prosecna_cena}")
    rezultatframe.grid()

    fig = plt.figure()
    fig.canvas.manager.set_window_title("Verovatnoće cenovnih klasa")
    ax = fig.add_subplot(111)
    verovatnoce = [verovatnoca * 100 for verovatnoca in verovatnoce]
    colors = np.full(len(verovatnoce), "tab:blue")
    colors[np.argmax(verovatnoce)] = "tab:red"
    width = 0.8
    rects = ax.bar(cls_names, verovatnoce, width, color = colors)
    ax.set_ylim([0, 100])
    ax.set_xticklabels(cls_names, rotation = 45, rotation_mode = "anchor", ha = "right")
    ax.set_ylabel('Verovatnoća [%]')

    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2., 1.05 * height, f"{float(height):.2f}%", ha = "center", va = "bottom")

    plt.tight_layout()
    plt.ion()
    plt.show()

def show_knn_config_window():
    config_window = tk.Toplevel(root)
    config_window.title("K-NN klasifikacija")
    config_window.minsize(300, 200)
    config_window.wm_resizable(False, False)

    frame = Frame(config_window)
    frame.pack(fill = BOTH, expand = True, padx = 20, pady = 20)    

    Label(frame, text = "Uneti parametre K-NN algoritma pa pokrenuti klasifikaciju:", justify = CENTER).grid(column = 0, row = 0, pady = [0, 10])

    baseframe = Frame(frame)
    baseframe.grid(column = 0, row = 1)

    Label(baseframe, text = "K:", justify = RIGHT).grid(column = 0, row = 0, sticky = E)
    k = StringVar()
    k.set(str(calculate_k()))
    Spinbox(baseframe, from_ = 1, to = 10000, textvariable = k).grid(column = 1, row = 0, sticky = W)

    Label(baseframe, text = "Funkcija rastojanja:", justify = RIGHT).grid(column = 0, row = 1, sticky = E, pady = [10, 0])
    fja_rastojanja = StringVar()
    fja_rastojanja.set("Manhattan")
    OptionMenu(baseframe, fja_rastojanja, "Manhattan", *["Euclid", "Chebyshev"]).grid(column = 1, row = 1, sticky = EW, pady = [10, 0])

    Label(frame, text = "Težinski koeficijenti:", justify = CENTER).grid(column = 0, row = 2, pady = 10)

    advframe = Frame(frame)
    advframe.grid(column = 0, row = 3)

    Label(advframe, text = "Udaljenost:", justify = RIGHT).grid(column = 0, row = 0, sticky = E)
    coef_udaljenost = StringVar()
    coef_udaljenost.set(knn.coef.udaljenost)
    Entry(advframe, textvariable = coef_udaljenost).grid(column = 1, row = 0, sticky = W)

    Label(advframe, text = "Kvadratura:", justify = RIGHT).grid(column = 0, row = 1, sticky = E)
    coef_kvadratura = StringVar()
    coef_kvadratura.set(knn.coef.kvadratura)
    Entry(advframe, textvariable = coef_kvadratura).grid(column = 1, row = 1, sticky = W)

    Label(advframe, text = "Starost:", justify = RIGHT).grid(column = 0, row = 2, sticky = E)
    coef_starost = StringVar()
    coef_starost.set(knn.coef.starost)
    Entry(advframe, textvariable = coef_starost).grid(column = 1, row = 2, sticky = W)

    Label(advframe, text = "Broj soba:", justify = RIGHT).grid(column = 0, row = 3, sticky = E)
    coef_broj_soba = StringVar()
    coef_broj_soba.set(knn.coef.broj_soba)
    Entry(advframe, textvariable = coef_broj_soba).grid(column = 1, row = 3, sticky = W)

    Label(advframe, text = "Spratnost:", justify = RIGHT).grid(column = 0, row = 4, sticky = E)
    coef_spratnost = StringVar()
    coef_spratnost.set(knn.coef.spratnost)
    Entry(advframe, textvariable = coef_spratnost).grid(column = 1, row = 4, sticky = W)

    Button(frame, text = "Pokreni klasifikaciju", command = lambda: (
        exec_knn(k.get(), get_dist_fn(fja_rastojanja.get())),
        config_window.destroy()
    )).grid(column = 0, row = 4, pady = [10, 0])

# Importovanje dataset-a

import_data()

# Kreiranje prozora aplikacije

root = Tk()
root.title("Prediktor cene/cenovne klase nekretnine")
root.minsize(350, 200)
root.wm_resizable(False, False)

# Kreiranje glavnog okvira aplikacije

frame = Frame(root)
frame.pack(fill = BOTH, expand = True, padx = 20, pady = 20)

# Dodavanje uputstva

Label(frame, text = "Uneti karakteristike nekretnine pa pokrenuti regresiju/klasifikaciju.").grid(column = 0, row = 0, pady = [0, 10])

# Dodavanje dela prozora za unos oglasa

adframe = Frame(frame)
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

# Dodavanje dugmeta za crtanje grafika

Button(frame, text = "Iscrtaj grafike zavisnosti", command = show_plots).grid(column = 0, row = 3, pady = 10)

# Dodavanje dugmica za pokretanje regresije/klasifikacije

btnframe = Frame(frame)
btnframe.grid(column = 0, row = 4)
Button(btnframe, text = "Linearna regresija", command = exec_lin_reg).grid(column = 0, row = 0, padx = 5)
Button(btnframe, text = "K-NN klasifikacija", command = show_knn_config_window).grid(column = 1, row = 0, padx = 5)

# Dodavanje rezultata linearne regresije/K-NN klasifikacije

rezultatframe = Frame(frame)
rezultatframe.grid(column = 0, row = 5, pady = [10, 0])
rezultat_info = StringVar()
rezultat_info.set("")
Label(rezultatframe, textvariable = rezultat_info).grid(column = 0, row = 0)
rezultat = StringVar()
rezultat.set("")
Label(rezultatframe, textvariable =  rezultat).grid(column = 1, row = 0)
rezultatframe.grid_remove()

# Pokretanje glavne petlje aplikacije

root.mainloop()