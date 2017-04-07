import sys

from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from samsclub_scraper.spiders.samsclub_spider import SamsclubSpider

def scrape_module():
    crawler = CrawlerProcess(get_project_settings())
    crawler.crawl(SamsclubSpider, task_id=sys.argv[1])
    crawler.start()

if __name__ == '__main__':
    scrape_module()