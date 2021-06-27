from nekretnine_rs_scraper.parser import parse_ad
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class NekretnineRsSpider(CrawlSpider):
    name = 'nekretnine'
    allowed_domains = ['nekretnine.rs']

    start_urls = [
        'https://www.nekretnine.rs/stambeni-objekti/stanovi/lista/po-stranici/20/',
        'https://www.nekretnine.rs/stambeni-objekti/kuce/lista/po-stranici/20/'
    ]

    rules = (
        Rule(LinkExtractor(restrict_css='a.next-article-button'), follow=False), # TODO: Change follow to True once item creation, proxies and db insert works!
        Rule(LinkExtractor(restrict_css='.offer-title > a'), callback='parse_details_page')
    )

    def parse_details_page(self, response):
        return parse_ad(response)