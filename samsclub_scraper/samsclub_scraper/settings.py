# -*- coding: utf-8 -*-

# Scrapy settings for samsclub_scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'samsclub_scraper'

SPIDER_MODULES = ['samsclub_scraper.spiders']
NEWSPIDER_MODULE = 'samsclub_scraper.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'samsclub_scraper (+http://www.yourdomain.com)'

# Obey robots.txt rules
# ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'samsclub_scraper.middlewares.SamsclubScraperSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'samsclub_scraper.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'samsclub_scraper.pipelines.SamsclubScraperPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 3
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

ALL_CATEGORIES = {
    'apparel-shoes/1959',
    'appliances/1004',
    'auto-tires/1055',
    'baby-supplies/1946',
    'child-care-supplies-classroom-supplies/2074',
    'cigarettes-tobacco/1580',
    'computers/1116',
    'concession-supplies/2046',
    'construction-repair/2139',
    'convenience-stores-supplies/2043',
    'electronics/1086',
    'electronics/1086',
    'family-caregiving/15720473',
    'foodservice/15770140',
    'furniture/1286',
    'gift-cards/1003',
    'grocery/1444',
    'home-collection/1285',
    'home-improvement/1390',
    'spring-renewal/5160101',
    'floorcare/15700202',
    'jewelry-flowers-gifts/7520117',
    'movies-tv-blu-ray-dvd/6120119',
    'new-items-online/8131',
    'office-supplies/1706',
    'outdoor-living/1852',
    'pet-care/2011',
    'health-and-beauty/1585',
    'religious-organizations/2111',
    'restaurant-supplies/2209',
    'salons-barber-shops/2042',
    'seasonal-special-occasions/1900101',
    'shops-promotions/7130108',
    'sports-equipment-fitness-equipment/1888',
    'start-saving-green/1130105',
    'toys-and-video-games/1929',
    'vending-machines-vending-concession/2247' 
}
