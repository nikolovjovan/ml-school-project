from tkinter import *

class Oglas:
    udaljenost: float
    kvadratura: float
    starost: int
    broj_soba: int
    spratnost: int

def printOglas():
    oglas = Oglas()
    oglas.udaljenost = float(udaljenost.get()) if len(udaljenost.get()) > 0 else 0.0
    oglas.kvadratura = float(kvadratura.get()) if len(kvadratura.get()) > 0 else 0.0
    oglas.starost = int(starost.get()) if len(starost.get()) > 0 else 0
    oglas.broj_soba = int(broj_soba.get()) if len(broj_soba.get()) > 0 else 1
    oglas.spratnost = int(spratnost.get()) if len(spratnost.get()) > 0 else 0
    print(vars(oglas))

def execLinReg():
    printOglas()

def execKNN():
    printOglas()

# Kreiranje prozora aplikacije

window = Tk()
window.title("Prediktor cene/cenovne klase nekretnine")
window.minsize(400, 400)

# Dodavanje uputstva

Label(window, text = "Uneti karakteristike nekretnine pa pokrenuti regresiju/klasifikaciju.").grid(column = 0, row = 0)

adframe = Frame(window)
adframe.grid(column = 0, row = 1)

Label(adframe, text = "Udaljenost od centra Beograda [km]:").grid(column = 0, row = 0)
udaljenost = Entry(adframe)
udaljenost.insert(0, "0")
udaljenost.grid(column = 1, row = 0)

Label(adframe, text = "Kvadratura [m^2]:").grid(column = 0, row = 1)
kvadratura = Entry(adframe)
kvadratura.insert(0, "0")
kvadratura.grid(column = 1, row = 1)

Label(adframe, text = "Starost [godina]:").grid(column = 0, row = 2)
starost_var = StringVar()
starost_var.set("0")
starost = Spinbox(adframe, from_ = -10, to = 150, textvariable = starost_var)
starost.grid(column = 1, row = 2)

Label(adframe, text = "Broj soba:").grid(column = 0, row = 3)
broj_soba_var = StringVar()
broj_soba_var.set("0")
broj_soba = Spinbox(adframe, from_ = 1, to = 1000, textvariable = broj_soba_var)
broj_soba.grid(column = 1, row = 3)

Label(adframe, text = "Spratnost:").grid(column = 0, row = 4)
spratnost_var = StringVar()
spratnost_var.set("0")
spratnost = Spinbox(adframe, from_ = 0, to = 100, textvariable = spratnost_var)
spratnost.grid(column = 1, row = 4)

btnframe = Frame(window)
btnframe.grid(column = 0, row = 2)
Button(btnframe, text = "Linearna regresija", command = execLinReg).grid(column = 0, row = 0)
Button(btnframe, text = "K-NN klasifikacija", command = execKNN).grid(column = 1, row = 0)

# Pokretanje glavne petlje aplikacije

window.mainloop()