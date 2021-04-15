import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.utils.request import referer_str
from scrapy.linkextractors import LinkExtractor
from w3lib.url import url_query_cleaner
from wordninja import split

from ..urls import urls, allowed_domains
from ..cleaner import clean_text
from ..utils import text_to_remove_list

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

def fixup_text(text_list):
    main_text = ''
    for text in text_list:
        text = ' '.join(split(text))
        for remove_text in text_to_remove_list:
            text = text.replace(remove_text, '')
        main_text += clean_text(text)
    return main_text

class TravelSpider(CrawlSpider):
    name = "travel"
    allowed_domains = allowed_domains
    start_urls = urls

    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'DEPTH_LIMIT': 1,
        #  'CLOSESPIDER_PAGECOUNT': 5
    }

    rules = [Rule(LinkExtractor(unique=True), callback='parse', follow=True, process_links=process_links)]

    def parse(self, response):
        item = {}
        item['url_from'] = referer_str(response.request)
        item['url_to'] = response.url

        para_text = ' '.join(response.xpath('//p//text()').getall()[:30])
        span_text = ' '.join(response.xpath('//span//text()').getall()[:30])
        div_text = ' '.join(response.xpath('//div/text()').getall()[:30])

        text_list = [para_text, span_text, div_text]
        combined_text = fixup_text(text_list)

        item['text'] = combined_text
        yield item

