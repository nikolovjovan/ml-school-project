from scrapy.item import Item, Field
from scrapy.loader import ItemLoader

class Nekretnina(Item):
    id = Field()
    tip = Field()
    prodaja = Field()
    cena = Field()
    drzava = Field()
    grad = Field()
    deo_grada = Field()
    kvadratura = Field()
    godina_izgradnje = Field()
    klasa = Field()
    povrsina_zemljista = Field()
    ukupna_spratnost = Field()
    sprat = Field()
    uknjizenost = Field()
    tip_grejanja = Field()
    broj_soba = Field()
    broj_kupatila = Field()
    parking = Field()
    lift = Field()
    terasa = Field()

class NekretninaLoader(ItemLoader):
    default_item_class = Nekretnina