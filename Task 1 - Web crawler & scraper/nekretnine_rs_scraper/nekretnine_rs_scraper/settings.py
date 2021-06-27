BOT_NAME = 'nekretnine_rs_scraper'

SPIDER_MODULES = ['nekretnine_rs_scraper.spiders']
NEWSPIDER_MODULE = 'nekretnine_rs_scraper.spiders'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'

ROBOTSTXT_OBEY = False

COOKIES_ENABLED = False

TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language':'en-US,en;q=0.8',
    'DNT': '1',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'www.nekretnine.rs'
}

# PyMySqlPipeline params
#
PYMYSQL_PARAMS = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'pass': '',
    'db': 'nekretnine',
    'table': 'nekretnina',
    'retries': 3,
    'close_on_error': True,
    'charset': 'utf8',
    'upsert': True
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': None,
    'nekretnine_rs_scraper.middlewares.RandomUserAgentMiddleware': 543,
    'nekretnine_rs_scraper.middlewares.RotateProxyRetryMiddleware': 120,
}

import os

PROXY_LIST_PATH = os.path.dirname(os.path.abspath(__file__)) + '\proxies.txt'

LINK_LIST_PATH = os.path.dirname(os.path.abspath(__file__)) + '\links_to_parse.txt'

ITEM_PIPELINES = {
   'nekretnine_rs_scraper.pipelines.PyMySqlPipeline': 300
}

HTTPCACHE_ENABLED = True
# HTTPCACHE_IGNORE_HTTP_CODES = [301, 302, 303, 304, 305, 306, 307]