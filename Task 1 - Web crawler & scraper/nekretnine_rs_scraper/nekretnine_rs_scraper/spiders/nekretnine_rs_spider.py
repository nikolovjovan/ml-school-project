from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.item import Item

class NekretnineRsSpider(CrawlSpider):

    name = 'nekretnine'

    start_urls = [
        'https://www.nekretnine.rs/stambeni-objekti/stanovi/lista/po-stranici/20/',
        'https://www.nekretnine.rs/stambeni-objekti/kuce/lista/po-stranici/20/'
    ]

    rules = (
        Rule(LinkExtractor(restrict_css='a.next-article-button'), follow=False),
        Rule(LinkExtractor(restrict_css='.offer-title > a'), callback='parse_details_page')
    )

    def parse_details_page(self, response):
        # TODO: Parse details page
        yield Item()