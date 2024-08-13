import scrapy
from scrapy_tutorial.items import QuoteItem


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com"]

    def parse(self, response):
        quotes = response.css('.quote')
        for quote in quotes:
            quote_item = QuoteItem()
            quote_item['text'] = quote.css('.text::text').extract_first()
            quote_item['author'] = quote.css('.author::text').extract_first()
            quote_item['tags'] = quote.css('.tags .tag::text').extract()
            yield quote_item
        next = response.css('.pager .next a::attr(href)').extract_first()
        url = response.urljoin(next)
        yield scrapy.Request(url=url, callback=self.parse)
