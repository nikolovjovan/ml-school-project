from nekretnine_rs_scraper.items import NekretninaLoader # This is only used for VSCode, comment out before running!
from scrapy.http.request import Request
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
import re

class NekretnineRsSpider(CrawlSpider):

    name = 'nekretnine'

    start_urls = [
        'https://www.nekretnine.rs/stambeni-objekti/stanovi/lista/po-stranici/20/',
        'https://www.nekretnine.rs/stambeni-objekti/kuce/lista/po-stranici/20/'
    ]

    rules = (
        Rule(LinkExtractor(restrict_css='a.next-article-button'), follow=False), # TODO: Change follow to True once item creation, proxies and db insert works!
        Rule(LinkExtractor(restrict_css='.offer-title > a'), callback='parse_details_page')
    )

    def parse_details_page(self, response):
        self.log(response)
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

        # Lokacija: grad i deo grada gde se lokacija nalazi
        #
        location_selector = response.xpath('//div[@class="property__location"]/ul')
        if location_selector is None:
            l.add_value('grad', None)
            l.add_value('deo_grada', None)
        else:
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