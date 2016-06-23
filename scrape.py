import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy.utils.log import configure_logging
from os import path

class Listing(scrapy.Item):
    userid = scrapy.Field()
    user = scrapy.Field()
    listingid = scrapy.Field()
    name = scrapy.Field()
    summary = scrapy.Field()
    listing_img = scrapy.Field()
    user_img = scrapy.Field()



class ListingSpider(scrapy.Spider):
    name = "listing"
    allowed_domains = ["airbnb.com"]
    start_urls = [
        'http://www.airbnb.com/s/Stanardsville--VA--United-States?page=1'
    ]

    def parse(self, response):
        listings = response.xpath('//div[@class="listing"]')
        for listing in listings:
            item = Listing()
            xpaths = [('listingid','.//@data-hosting_id'),
                        ('userid','.//@data-host_id'),
                        ('name','.//@data-name'),
                        ('summary','.//div[@class="listing__summary"]/text()'),
                        ]
            for key,xp  in xpaths:
                item[key] = listing.xpath(xp).extract_first()

            
            item['user_img'] = listing.xpath('.//div[@class="media-photo media-round"]/img/@src').extract_first().replace('medium','x_medium')
            item['user'] = listing.xpath('.//div[@class="media-photo media-round"]/img/@alt').extract_first().split(' from')[0]
            item['listing_img']= listing.xpath('.//div[@class="listing-img-container media-cover text-center"]/img/@src').extract_first().replace('https','http').replace('x_medium','x_large')
            yield item

        next_page = response.xpath('//a[@rel="next"]/@href')
        next_page=1
        if next_page:
            url = response.urljoin(next_page.extract_first())
            yield scrapy.Request(url, self.parse)




def scrape_it(output_path):
    csv_filename= path.join(output_path, 'items.csv')
    # TODO fix cantrestartreactor problem
    settings = Settings(dict(FEED_FORMAT='csv',
                            FEED_URI=csv_filename,
                            
                            ))


    configure_logging({'LOG_ENABLED':False})

    process = CrawlerProcess( settings)

    process.crawl(ListingSpider)
    process.start()#stop_after_crawl=False)
