import sys

from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from samsclub_scraper.spiders.samsclub_spider import SamsclubSpider

def scrape_module():
    params = sys.argv[1] if len(sys.argv) > 1 else None
    crawler = CrawlerProcess(get_project_settings())
    crawler.crawl(SamsclubSpider, param=params)
    crawler.start()

if __name__=='__main__':
    scrape_module()