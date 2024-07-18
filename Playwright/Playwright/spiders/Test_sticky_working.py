import scrapy
from scrapy_playwright.page import PageMethod
from playwright.async_api import Page


class PlaywrightSpider(scrapy.Spider):
    name = 'Playwright'
    allowed_domains = ['hugoboss.com']
    start_urls = ['https://www.hugoboss.com/de/regular-fit-hose-aus-knitterfreiem-japanischem-krepp-mit-tunnelzug/hbeu50427841_466.html?cgid=11000']


        # Speichert immer in JSON Datei
    custom_settings = {
        'FEEDS': {
            'BOSStest.json': {'format': 'json', 'overwrite': True},
        }
    }

    def start_requests(self):
        yield scrapy.Request(
            url='https://www.hugoboss.com/de/regular-fit-hose-aus-knitterfreiem-japanischem-krepp-mit-tunnelzug/hbeu50427841_466.html?cgid=11000',
            meta={
                'playwright': True,
                'playwright_include_page':True,
                'playwright_page_methods': [
                PageMethod("wait_for_selector","button.sc-dcJsrY.jvRBls"),
                #PageMethod("wait_for_timeout", 3000),
                PageMethod("click", "button.sc-dcJsrY.jvRBls"),
                PageMethod("wait_for_navigation"),
                PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                PageMethod("wait_for_timeout", 3000),
                PageMethod("evaluate", "window.scrollTo(0, 0)"),
                PageMethod("wait_for_selector", "div.tagg-reset.tagg-txt"),
                PageMethod("wait_for_timeout", 2000),
                ]
            }
        )
    def parse(self, response):
        self.logger.info(f"Parsing item from URL: {response.url}")
        print (response.text)
        products = response.css('div.pdp-main')
        
        for product in products:
            name = product.css('h1.pdp-stage__header-title::text').get()
            price = product.css('div.pricing__main-price::text').get()
            info = product.css('div.tagg-reset.tagg-txt::text').getall()

            yield {
                'name': name,
                'price': price,
                'info': info,
            }
        # await Page.close()