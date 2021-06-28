from nekretnine_rs_scraper.parser import parse_ad
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

# Unused spider, use link_fetcher then page_parser separately...
# It should work, however it is not tested!

class NekretnineRsSpider(CrawlSpider):
    name = 'nekretnine'
    allowed_domains = ['nekretnine.rs']

    start_urls = [
        'https://www.nekretnine.rs/stambeni-objekti/stanovi/lista/po-stranici/20/',
        'https://www.nekretnine.rs/stambeni-objekti/kuce/lista/po-stranici/20/'
    ]

    rules = (
        Rule(LinkExtractor(restrict_css='a.next-article-button'), follow=True),
        Rule(LinkExtractor(restrict_css='.offer-title > a'), callback='parse_details_page')
    )

    def parse_details_page(self, response):
        return parse_ad(response)