from nekretnine_rs_scraper.items import NekretninaLoader, UdaljenostLoader
from geopy.geocoders import Nominatim, ArcGIS
from geopy.distance import geodesic
import re

# Sredina ulice Knez Mihajlova

belgrade = (44.8178131, 20.4568974)

def parse_ad(response):
    l = NekretninaLoader(response=response)

    # Id nekretnine: jedinstveni niz alphanumerickih karaktera
    #
    res = re.search('^.*/stambeni-objekti/(stanovi|kuce)/[^/]*/([^/]*).*$', response.url)
    l.add_value('id', '' if res is None else res.group(2))
    
    # Tip nekretnine: stan ili kuca
    #
    l.add_value('tip', 'stan' if '/stanovi/' in response.url else 'kuca')

    # Dohvatanje detalja oglasa
    #
    detalji = response.css('section#detalji').get()

    # Tip transakcije: prodaja ili iznajmljivanje/izdavanje
    #
    res = re.search('Transakcija:\s*<strong>\s*(Prodaja|Izdavanje)\s*', detalji)
    l.add_value('prodaja', True if res is None else res.group(1).lower() == 'prodaja')

    # Cena nekretnine: prodajna odnosno cena iznajmljivanja
    #
    res = response.css('.stickyBox__price::text').get()
    idx = res.find(' EUR')
    l.add_value('cena', None if res is None else -1 if idx == -1 else float(res[0:idx].replace(' ', '')))

    # Lokacija: drzava, grad i deo grada gde se lokacija nalazi
    #
    location_selector = response.xpath('//div[@class="property__location"]/ul')
    if location_selector is None:
        l.add_value('drzava', None)
        l.add_value('grad', None)
        l.add_value('deo_grada', None)
    else:
        res = location_selector.xpath('li[1]/text()')
        l.add_value('drzava', None if res is None else res.get())
        res = location_selector.xpath('li[3]/text()')
        l.add_value('grad', None if res is None else res.get())
        res = location_selector.xpath('li[4]/text()')
        l.add_value('deo_grada', None if res is None else res.get())

    # Kvadratura
    #
    res = re.search('Kvadratura:\s*<strong>\s*(\d+)\s*', detalji)
    l.add_value('kvadratura', None if res is None else float(res.group(1)))

    # Godina izgradnje
    #
    res = re.search('Godina izgradnje:\s*<strong>\s*(\d+)\s*', detalji)
    l.add_value('godina_izgradnje', None if res is None else int(res.group(1)))

    # Klasa (stanje) nekretnine
    #
    res = re.search('Stanje nekretnine:\s*<strong>\s*(.*)\s*</strong>', detalji)
    l.add_value('klasa', None if res is None else res.group(1).lower())

    # Povrsina zemljista (samo za kuce)
    #
    res = re.search('Površina zemljišta:\s*<strong>\s*(\d+)\s*', detalji)
    l.add_value('povrsina_zemljista', None if res is None else res.group(1).lower())

    # Ukupna spratnost
    #
    res = re.search('Ukupan broj spratova:\s*<strong>\s*(\d+)\s*', detalji)
    l.add_value('ukupna_spratnost', None if res is None else int(res.group(1)))

    # Sprat (samo za stanove)
    #
    res = re.search('Spratnost:\s*<strong>\s*(\d+)\s*', detalji)
    if res is None:
        res = re.search('Spratnost:\s*<strong>\s*(.*)\s*</strong>', detalji)
        # Suteren/Prizemlje/Visoko prizemlje
        l.add_value('sprat', 0)
    else:
        l.add_value('sprat', None if res is None else int(res.group(1)))

    # Uknjizenost
    #
    res = re.search('Uknjiženo:\s*<strong>\s*(Da|Ne)\s*', detalji)
    l.add_value('uknjizenost', False if res is None else res.group(1).lower() == 'da')

    # Tip grejanja
    #
    res = re.search('Grejanje:\s*(.*)\s*', detalji)
    l.add_value('tip_grejanja', None if res is None else res.group(1))

    # Broj soba
    #
    res = re.search('Ukupan broj soba:\s*<strong>\s*(\d+)\s*', detalji)
    l.add_value('broj_soba', None if res is None else int(res.group(1)))

    # Broj kupatila
    #
    res = re.search('Broj kupatila:\s*<strong>\s*(\d+)\s*', detalji)
    l.add_value('broj_kupatila', None if res is None else int(res.group(1)))

    # Parking
    #
    res = re.search('(Garaža|Garažno mesto|Spoljno parking mesto|JavniRezervisan parking)', detalji)
    l.add_value('parking', res is not None)

    # Lift
    #
    res = re.search('Lift', detalji)
    l.add_value('lift', res is not None)

    # Terasa/lodja/balkon
    #
    res = re.search('(Terasa|Lođa|Balkon)', detalji)
    l.add_value('terasa', res is not None)

    return l.load_item()

def parse_and_calculate_distance(response):
    l = UdaljenostLoader(response=response)

    # Id nekretnine: jedinstveni niz alphanumerickih karaktera
    #
    res = re.search('^.*/stambeni-objekti/(stanovi|kuce)/[^/]*/([^/]*).*$', response.url)
    l.add_value('id', '' if res is None else res.group(2))

    lat = -1
    lng = -1
    search_text = ''

    script_selector = response.xpath('//script/text()')
    if script_selector is not None:
        scripts = script_selector.getall()
        for script in scripts:
            res = re.search('ppLat\s+=\s+([\d\.]+)', script)
            if res is not None:
                lat = float(res.group(1))
            res = re.search('ppLng\s+=\s+([\d\.]+)', script)
            if res is not None:
                lng = float(res.group(1))
                break

    distance = -1

    if lat != -1 and lng != -1:
        # print('Latitude:', lat, 'Longitude:', lng)
        distance = geodesic(belgrade, (lat, lng)).km
    else:
        location_selector = response.xpath('//div[@class="property__location"]/ul')

        if location_selector is not None:
            location_list = location_selector.xpath('li/text()').getall()
            if location_list is None:
                location_list = []
            cnt = len(location_list)
            i = cnt - 3
            if i < 0:
                i = 0
            while i < cnt:
                search_text += location_list[i] + ' '
                i += 1
            # print('Search text:', search_text)

        if not search_text:
            l.add_value('udaljenost', -1)
            return l.load_item()

        # Try get location using Nominatim

        geolocator = Nominatim(user_agent='nekretnine_rs_scraper')
        location_nominatim = geolocator.geocode(search_text)
        if location_nominatim is not None:
            # print('Nominatim:', location_nominatim.latitude, location_nominatim.longitude)
            distance = geodesic(belgrade, (location_nominatim.latitude, location_nominatim.longitude)).km
            # print('Distance Nominatim:', distance)
        else:
            # Try get location using ArcGIS
            geolocator = ArcGIS(user_agent='nekretnine_rs_scraper')
            location_arcgis = geolocator.geocode(search_text)
            if location_arcgis is not None:
                # print('ArcGIS:', location_arcgis.latitude, location_nominatim.longitude)
                distance = geodesic(belgrade, (location_arcgis.latitude, location_arcgis.longitude)).km
                # print('Distance ArcGIS:', distance)
            else:
                print(f'Failed to get location using both Nominatim and ArcGIS! Search text: "{search_text}"')

    l.add_value('udaljenost', distance)

    return l.load_item()