from tkinter import *
from model import Oglas, import_data
from linreg import predict_price
from knn import calculate_k, chebyshev, euclid, manhattan, most_probable_class, predict_class

def create_oglas():
    oglas = Oglas()
    oglas.udaljenost = float(udaljenost.get()) if len(udaljenost.get()) > 0 else 0.0
    oglas.kvadratura = float(kvadratura.get()) if len(kvadratura.get()) > 0 else 0.0
    oglas.starost = int(starost.get()) if len(starost.get()) > 0 else 0
    oglas.broj_soba = int(broj_soba.get()) if len(broj_soba.get()) > 0 else 1
    oglas.spratnost = int(spratnost.get()) if len(spratnost.get()) > 0 else 0
    return oglas

def get_class_name(cls_id):
    if not hasattr(get_class_name, "cls_names"):
        get_class_name.cls_names = [
            "manje od 49 999 EUR",
            "izmedju 50 000 i 99 999 EUR",
            "izmedju 100 000 i 149 999 EUR",
            "izmedju 150 000 EUR i 199 999 EUR",
            "200 000 EUR ili vise"
        ]
    return get_class_name.cls_names[cls_id] if cls_id >= 0 and cls_id < 5 else "nevalidna klasa"

def exec_lin_reg():
    rezultatframe.grid_remove()
    verovatnocaframe.grid_remove()
    oglas = create_oglas()
    predvidjena_cena = predict_price(oglas)
    rezultat.set(f"Predvidjena cena: {predvidjena_cena} EUR")
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

def exec_knn():
    rezultatframe.grid_remove()
    verovatnocaframe.grid_remove()
    oglas = create_oglas()
    verovatnoce = predict_class(
        int(k.get()) if len(k.get()) > 0 else calculate_k(),
        oglas,
        get_dist_fn(fja_rastojanja.get()))
    predvidjena_klasa = most_probable_class(verovatnoce)
    rezultat.set(f"Predvidjena klasa: {predvidjena_klasa} - {get_class_name(predvidjena_klasa)}")
    verovatnoce_str = ""
    for i in range(len(verovatnoce)):
        verovatnoce_str += f"{(verovatnoce[i] * 100):.2f}%" + ("\n" if i < len(verovatnoce) - 1 else "")
    verovatnoce_klasa.set(verovatnoce_str)
    rezultatframe.grid()
    verovatnocaframe.grid()

# Importovanje dataset-a

import_data()

# Kreiranje prozora aplikacije

window = Tk()
window.title("Prediktor cene/cenovne klase nekretnine")
window.minsize(350, 400)
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

# Dodavanje dugmica za pokretanje regresije/klasifikacije

btnframe = Frame(window)
btnframe.grid(column = 0, row = 2)
Button(btnframe, text = "Linearna regresija", command = exec_lin_reg).grid(column = 0, row = 0)
Button(btnframe, text = "K-NN klasifikacija", command = exec_knn).grid(column = 1, row = 0)

# Dodavanje rezultata linearne regresije/K-NN klasifikacije

rezultatframe = Frame(window)
rezultatframe.grid(column = 0, row = 3)
rezultat_info = StringVar()
rezultat_info.set("")
Label(rezultatframe, textvariable = rezultat_info).grid(column = 0, row = 0)
rezultat = StringVar()
rezultat.set("")
Label(rezultatframe, textvariable =  rezultat).grid(column = 1, row = 0)
rezultatframe.grid_remove()

verovatnocaframe = Frame(window)
verovatnocaframe.grid(column = 0, row = 4)
verovatnoca_info = StringVar()
verovatnoca_info_str = ""
for i in range(5):
    verovatnoca_info_str += f"{i}: {get_class_name(i)} = " + ("\n" if i < 4 else "")
verovatnoca_info.set(verovatnoca_info_str)
Label(verovatnocaframe, textvariable = verovatnoca_info, justify = RIGHT).grid(column = 0, row = 0)
verovatnoce_klasa = StringVar()
verovatnoce_klasa.set("")
Label(verovatnocaframe, textvariable =  verovatnoce_klasa, font = ('Segoe UI', 9, 'bold'), justify = LEFT).grid(column = 1, row = 0)
verovatnocaframe.grid_remove()

# Pokretanje glavne petlje aplikacije

window.mainloop()