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

    # TODO: REMOVE THIS!!!
    def start_requests(self):
        yield Request('https://www.nekretnine.rs/stambeni-objekti/stanovi/vlasnik-karaburma-25m2-lep-stan-na-drugom-spratu/NkmsNf5e5tN/', callback=self.parse_details_page)

    def parse_details_page(self, response):
        self.log(response)
        l = NekretninaLoader(response=response)
        res = re.search('^.*/stambeni-objekti/(stanovi|kuce)/[^/]*/([^/]*).*$', response.url)
        l.add_value('id', '' if res is None else res.group(2))
        l.add_value('tip', 'stan' if '/stanovi/' in response.url else 'kuca')
        detalji = response.selector.css('section#detalji').extract_first()
        res = re.search('Transakcija:\s*<strong>\s*(Prodaja|Izdavanje)', detalji)
        l.add_value('prodaja', True if res is None else True if res.group(1).lower() == 'prodaja' else False)
        cena = response.selector.css('.stickyBox__price::text').extract_first()
        l.add_value('cena', -1 if cena is None else float(cena[0:cena.index(' EUR')].replace(' ', '')))
        return l.load_item()