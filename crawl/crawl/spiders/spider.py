import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.utils.request import referer_str
from scrapy.linkextractors import LinkExtractor
from w3lib.url import url_query_cleaner

from ..urls import urls, allowed_domains
from ..cleaner import clean_text

def process_links(links):
    for link in links:
        link.url = url_query_cleaner(link.url)
        yield link

class ScraperItem(scrapy.Item):
    # The source URL
    url_from = scrapy.Field()
    # The destination URL
    text = scrapy.Field()
    url_to = scrapy.Field()

class TravelSpider(CrawlSpider):
    name = "travel"
    allowed_domains = allowed_domains
    start_urls = urls

    custom_settings = {
        'DOWNLOAD_DELAY': 5,
        'DEPTH_LIMIT': 1,
        #  'CLOSESPIDER_PAGECOUNT': 5
    }

    rules = [Rule(LinkExtractor(unique=True), callback='parse_single', follow=True, process_links=process_links)]

    #def parse(self, response):
        #items = []
        #links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)

        #for link in links:
            #is_allowed = False
            #for allowed_domain in self.allowed_domains:
                #if allowed_domain in link.url:
                    #is_allowed = True

            #if is_allowed:
                #item = ScraperItem()
                #item['url_from'] = response.url
                #item['url_to'] = link.url
                #request = scrapy.Request(link.url, callback=self.parse_single, meta={'item': item}, dont_filter=True)
                #items.append(request.meta['item'])
            #yield request
    def parse_single(self, response):
        item = {}
        item['url_from'] = referer_str(response.request)
        item['url_to'] = response.url

        para_text = ''.join(response.xpath('//p//text()').getall())
        span_text = ''.join(response.xpath('//span//text()').getall())
        div_text = ''.join(response.xpath('//div/text()').getall())
        combined_text = clean_text(para_text + ' ' + span_text + ' ' + div_text)
        item['text'] = combined_text
        yield item

