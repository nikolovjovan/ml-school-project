from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.exceptions import NotConfigured
from scrapy.utils.response import get_meta_refresh

import logging
import codecs
import random

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
    'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
]

class RandomUserAgentMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(user_agents)
        request.meta['dont_redirect'] = True
        return None

class RotateProxyRetryMiddleware(RetryMiddleware):
    def __init__(self, proxy_list = None):
        self.proxies = proxy_list
        self.idx = 0

    @classmethod
    def from_crawler(cls, crawler):
        s = crawler.settings
        proxy_path = s.get('PROXY_LIST_PATH', None)
        if proxy_path is not None:
            with codecs.open(proxy_path, 'r', encoding='utf8') as f:
                proxy_list = [line.strip() for line in f if line.strip()]
        else:
            proxy_list = s.getlist('PROXY_LIST')
        if not proxy_list:
            raise NotConfigured()
        return cls(proxy_list)

    def rotate_proxy(self, request):
        if request is None:
            return None
        if self.idx >= len(self.proxies):
            self.idx = 0
        logger.info('Rotating proxy! Now using: {}'.format(self.proxies[self.idx]))
        request.meta['proxy'] = self.proxies[self.idx]
        return request

    def process_response(self, request, response, spider):
        # handle http status redirect
        url = response.url
        if response.status in [301, 307]:
            logger.info("trying to redirect us: %s" %url, level=log.INFO)
            reason = 'redirect %d' %response.status
            return self.rotate_proxy(self._retry(request, reason, spider)) or response
        # handle meta redirect
        interval, redirect_url = get_meta_refresh(response)
        if redirect_url:
            logger.info("trying to redirect us: %s" %url, level=log.INFO)
            reason = 'meta'
            return self.rotate_proxy(self._retry(request, reason, spider)) or response
        return response