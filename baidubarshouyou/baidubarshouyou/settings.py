# -*- coding: utf-8 -*-

# Scrapy settings for baidubarshouyou project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'baidubarshouyou'

SPIDER_MODULES = ['baidubarshouyou.spiders']
NEWSPIDER_MODULE = 'baidubarshouyou.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'baidubarshouyou (+http://www.yourdomain.com)'


ITEM_PIPELINES = {
    'baidubarshouyou.pipelines.BaidubarshouyouPipeline':100,
    }


LOG_ENABLED = True
LOG_ENCODING = 'utf-8'
LOG_FILE = '../../log/baidubarshouyou.log'
LOG_LEVEL = 'DEBUG'
LOG_STDOUT = True


