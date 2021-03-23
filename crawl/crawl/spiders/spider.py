import scrapy

from ..urls import urls

class TravelSpider(scrapy.Spider):
    name = "travel"
    start_urls = urls

    def parse(self, response):
        for url in urls:
            try:
                yield {
                    'url': url,
                    'text': ''.join(response.xpath('//body//p//text()').extract())
                  }
            except ValueError:
                print('not found')
