import scrapy
from scrapy_playwright.page import PageMethod
from playwright.async_api import Page


class PlaywrightSpider(scrapy.Spider):
    name = 'Playwright2'
    allowed_domains = ['hugoboss.com']
    start_urls = ['https://www.hugoboss.com/de/damen-kleidung/?srule=sort_by_most_popular&start=0&sz=36']

            # Speichert immer in JSON Datei
    custom_settings = {
        'FEEDS': {
            'BOSStest.json': {'format': 'json', 'overwrite': True},
        }
    }


    def start_requests(self):
        yield scrapy.Request(
            url='https://www.hugoboss.com/de/damen-kleidung/?srule=sort_by_most_popular&start=0&sz=36',
            meta={
                'playwright': True,
                'playwright_include_page':True,
                'playwright_page_methods': [
                PageMethod("wait_for_selector","button.sc-dcJsrY.jvRBls"),
                PageMethod("click", "button.sc-dcJsrY.jvRBls"),
                # PageMethod("wait_for_timeout", 10000),
                ]
            }
        )

    def parse(self, response):

        results = response.xpath('//div[@id="wrapper"]')
        shop_items = results.xpath('.//div[contains(@class, "product-tile-plp__info-wrapper")]')
        for shop_item in shop_items:
            item = {
                'Title': shop_item.xpath('.//a[contains(@class, "product-tile-plp__title-link")]/@title').get(),
                'Price': shop_item.xpath('.//div[contains(@class, "pricing__main-price")]/text()').get().replace("\n",''),
                'URL': response.urljoin(shop_item.xpath('.//a[contains(@class, "product-tile-plp__title-link")]/@href').get())
            }
            yield response.follow(item['URL'], callback=self.parse_item,errback=self.errback_close_page, meta={
                'item': item,
                'playwright': True,
                'playwright_include_page':True,
                'playwright_page_methods': [
                    # PageMethod("wait_for_selector", "button.sc-dcJsrY.jvRBls"),
                    # PageMethod("wait_for_timeout", 1000),
                    # PageMethod("click", "button.sc-dcJsrY.jvRBls"),
                    # PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                    # PageMethod("wait_for_timeout", 3000),
                    # PageMethod("evaluate", "window.scrollTo(0, 0)"),
                    PageMethod("wait_for_selector", "div.tagg-reset.tagg-txt", timeout=180000),
                    PageMethod("wait_for_timeout", 2000),
                    
                ]
                }
            )


	    #Suche nach dem Link zur nächsten Seite
        next_page_url = response.xpath('//a[contains(@title, "Weiter")]/@href').get()
        if next_page_url:
            # next_page_url = next_page_url[1]
            self.logger.info(f"Nächste Seite URL gefunden: {next_page_url}")
            yield response.follow(next_page_url, callback=self.parse)
        else:
            self.logger.info("Keine nächste Seite URL gefunden.")


    async def parse_item(self, response):
        page = response.meta['playwright_page']
        try:
            item = response.meta['item']
            temp={}
            FIT_Filter = response.css('div.pdp-stage__header-flag::text').getall()

            if len(FIT_Filter) == 1:
                if 'SALE' in FIT_Filter[0]:
                    print("ACHTUNG")
                    temp = "Kein spezieller Fit(manuell)"
                else:
                    temp = FIT_Filter[0]
            elif len(FIT_Filter) >= 2:
                temp = FIT_Filter[1]
            else:
                temp= 'Fit nicht vorhanden!'
                print("Fit von ITEM Fehlt!")

            item['Fit'] = temp.replace("\n",'')
            item ['Color'] = response.xpath('//*[@id="pdp-stage-color-selector"]/div[1]/div[1]/nav/a[1]/span/strong/u/text()').get()
            item['Description'] = response.xpath('//div[contains(@class, "pdp-stage__accordion-description")]/text()').get().replace("\n",'')
            item['Material'] = response.xpath('//div[@id="product-container-care-panel"]/text()').get().replace("\n",'')
            item['info'] = response.css('div.tagg-reset.tagg-txt::text').getall()

            yield item

        
        except Exception as e:
            self.logger.error(f"Ein Fehler trat auf beim Verarbeiten der Seite {response.url}: {str(e)}")
            await page.close()  # Schließt die Seite, wenn ein Fehler auftritt

        finally:
            await page.close()

    async def errback_close_page(self, failure):
        page: Page = failure.request.meta["playwright_page"]
        await page.close()
        
