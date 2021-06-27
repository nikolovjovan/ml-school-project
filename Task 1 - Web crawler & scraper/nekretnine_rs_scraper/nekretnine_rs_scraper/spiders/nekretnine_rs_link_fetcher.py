from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class NekretnineRsLinkFetcherSpider(CrawlSpider):
    name = 'link_fetcher'
    allowed_domains = ['nekretnine.rs']

    start_urls = [
        'https://www.nekretnine.rs/stambeni-objekti/kuce/lista/po-stranici/20/?order=2',
        'https://www.nekretnine.rs/stambeni-objekti/stanovi/izdavanje-prodaja/izdavanje/lista/po-stranici/20/?order=2',
        'https://www.nekretnine.rs/stambeni-objekti/stanovi/izdavanje-prodaja/prodaja/cena/0_100000/lista/po-stranici/20/?order=2',
        'https://www.nekretnine.rs/stambeni-objekti/stanovi/izdavanje-prodaja/prodaja/cena/0_100000/lista/po-stranici/20/?order=3',
        'https://www.nekretnine.rs/stambeni-objekti/stanovi/izdavanje-prodaja/prodaja/cena/0_100000/lista/po-stranici/20/?order=2',
        'https://www.nekretnine.rs/stambeni-objekti/stanovi/izdavanje-prodaja/prodaja/cena/0_100000/lista/po-stranici/20/?order=2',
        'https://www.nekretnine.rs/stambeni-objekti/stanovi/izdavanje-prodaja/prodaja/cena/100000_99999999/lista/po-stranici/20/?order=2',
        'https://www.nekretnine.rs/stambeni-objekti/stanovi/izdavanje-prodaja/prodaja/cena/100000_99999999/lista/po-stranici/20/?order=3'
    ]

    rules = (
        Rule(LinkExtractor(restrict_css='a.next-article-button'), callback='parse_list_page', follow=True),
    )

    def parse_start_url(self, response, **kwargs):
        return self.parse_list_page(response)

    def parse_list_page(self, response):
        if response.status == 301 or response.status == 302:
            print(response.status)
        else:
            with open('links.txt', 'a') as f:
                for details_link in response.css('.offer-title > a::attr(href)').getall():
                    f.write('https://www.nekretnine.rs{}\n'.format(details_link))