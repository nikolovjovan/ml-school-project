from scrapy import Spider
from scrapy.exceptions import NotConfigured
from scrapy.http import Request
from nekretnine_rs_scraper.parser import parse_and_calculate_distance
import codecs

class NekretnineRsDistanceCalculatorSpider(Spider):
    name = 'distance_calculator'
    allowed_domains = ['nekretnine.rs']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        self = super().from_crawler(crawler, *args, **kwargs)
        db_params = crawler.settings.get('PYMYSQL_PARAMS', None)
        db_params['table'] = 'nekretnina_subset'
        return self

    allowed_domains = ['nekretnine.rs']

    def start_requests(self):
        subset_list_path = self.settings.get('SUBSET_LIST_PATH', None)
        if subset_list_path is not None:
            with codecs.open(subset_list_path, 'r', encoding='utf8') as f:
                subset_list = [line.strip() for line in f if line.strip()]
        else:
            subset_list = []
            link_list_path = self.settings.get('LINK_LIST_PATH', None)
            if link_list_path is not None:
                with codecs.open(link_list_path, 'r', encoding='utf8') as f:
                    link_list = [line.strip() for line in f if line.strip()]
            else:
                raise NotConfigured()
            id_list_path = self.settings.get('ID_LIST_PATH', None)
            if id_list_path is not None:
                with codecs.open(id_list_path, 'r', encoding='utf8') as f:
                    id_list = [line.strip() for line in f if line.strip()]
            else:
                raise NotConfigured()
            for id in id_list:
                url = next((link for link in link_list if link.endswith(id + '/')), None)
                subset_list += url
                with codecs.open('subset_links.txt', 'a') as f:
                    f.write(url + '\n')
        for link in subset_list:
            yield Request(link, dont_filter=True)

    def parse(self, response):
        return parse_and_calculate_distance(response)
