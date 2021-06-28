from scrapy.spiders import Spider
from scrapy.exceptions import NotConfigured
from scrapy.http import Request
from nekretnine_rs_scraper.parser import parse_ad
import codecs

class NekretnineRsPageParserSpider(Spider):
    name = 'page_parser'
    allowed_domains = ['nekretnine.rs']

    def start_requests(self):
        link_list_path = self.settings.get('LINK_LIST_PATH', None)
        if link_list_path is not None:
            with codecs.open(link_list_path, 'r', encoding='utf8') as f:
                link_list = [line.strip() for line in f if line.strip()]
        else:
            raise NotConfigured()
        for link in link_list:
            yield Request(link, dont_filter=True)

    def parse(self, response):
        nekretnina = parse_ad(response)
        if nekretnina['drzava'][0] != 'Srbija':
            self.logger.critical(f"Oglas {response.url} (id = {nekretnina['id']}) nije iz Srbije vec iz: {nekretnina['drzava']}\n")
        return nekretnina
