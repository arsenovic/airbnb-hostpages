import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy.utils.log import configure_logging
from os import path

import logging 
class Listing(scrapy.Item):
    '''
    Scrapy database-like object to fill  with values
    '''
    userid = scrapy.Field()
    user = scrapy.Field()
    listingid = scrapy.Field()
    name = scrapy.Field()
    summary = scrapy.Field()
    listing_img = scrapy.Field()
    user_img = scrapy.Field()



class ListingSpider(scrapy.Spider):
    '''
    Crawls search pages and extract listings objects
    
    initialize with the `start_urls` pointing to to a airbnb 
    search result page[s]. 
    
    Examples
    --------------
    start_urls=['http://airbnb.com/s?host_id=41657617']
    l = ListingSpider(start_urls = start_urls)
    '''
    name = "listing"
    allowed_domains = ["airbnb.com"]
    start_urls = ['http://airbnb.com/s?host_id=41657617']

    def parse(self, response):
        logging.getLogger('scrapy').setLevel(logging.CRITICAL)
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
            item['listing_img']= listing.xpath('.//div[@class="listing-img-container media-cover text-center"]/img/@src').extract_first().replace('https','https').replace('x_medium','x_large')
            yield item

        paginate = True
        next_page = response.xpath('//a[@rel="next"]/@href')
        if paginate:
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
