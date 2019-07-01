# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from dgmc.items import DgmcItem

class ZbSpider(CrawlSpider):
    name = 'zb'
    allowed_domains = ['www.dg.gov.cn']
    start_urls = ['http://www.dg.gov.cn/machong/zfcg/list_{}.shtml'.format(i) for i in range(2, 72)]

    rules = (
        Rule(LinkExtractor(allow=r'\/.*\.shtml',
                        restrict_xpaths='//div[contains(@class,"cen-div-1")]/div[contains(@class,"con-right")]/div[contains(@class,"list_div")]/div[contains(@class,"list-right_title")]/a'),
                        callback='parse_item',
                        follow=False),
    )

    def parse_item(self, response):
        item = DgmcItem()
        item['title'] = response.xpath('//div[contains(@class,"cen-div")]/div[contains(@class,"title")]/ucaptitle/text()').extract_first()
        item['time'] = response.xpath('//div[contains(@class,"line")]/table/tr/td[2]/publishtime/text()').extract_first()
        item['content'] = response.xpath('//div[contains(@class,"cen-div")]/div[contains(@class,"con_cen")]/ucapcontent//text()').extract()
        yield item