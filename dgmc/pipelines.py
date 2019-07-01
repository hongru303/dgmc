# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import pymysql


#对item进行数据清洗
class DgmcPipeline(object):
    def process_item(self, item, spider):
        title = ''.join(item['title'])#从spider中接收item并赋值为变量，之后再重新为item赋值#replace是str的属性
        item['title'] = title.replace('\n', '').replace('\r', '').replace('\t', '').replace('\xa0', '').replace(' ', '')
        time = ''.join(item['time'])
        item['time'] = time.replace('\n', '').replace('\r', '').replace('\t', '').replace('\xa0', '').replace(' ', '')
        content = ''.join(item['content'])
        item['content'] = content.replace('\n', '').replace('\r', '').replace('\t', '').replace('\xa0', '').replace(' ', '')
        return item


class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod#pipeline中可选方法，比open_spider要早调用
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )
    def open_spider(self, spider):#爬虫开始时调用，连接数据库
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):#每个pipeline必须的方法
        # name = item.collection
        self.db['zfcg'].insert_one(dict(item))
        return item

    def close_spider(self, spider):#爬虫结束时调用，关闭数据库
        self.client.close()


class MysqlPipeline(object):
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            port=crawler.settings.get('MYSQL_PORT'),
        )

    def open_spider(self, spider):
        self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8',
                                  port=self.port)
        self.cursor = self.db.cursor()

    def close_spider(self, spider):
        self.db.close()

    #mysql数据库更新，爬取全部数据，查找数据库是否有这条数据，没有就添加，否则pass
    def process_item(self, item, spider):
        data = dict(item)
        keys = ', '.join(data.keys())#title,time,content
        values = ', '.join(['%s'] * len(data))#%s%s%s
        sql_select = 'select * from {} where title="{}" and time="{}" and content="{}"'.format('zfcg', tuple(data.values())[0], tuple(data.values())[1], tuple(data.values())[2])
        sql = 'insert into {} ({}) values ({})'.format('zfcg', keys, values)
        select_all = self.cursor.execute(sql_select)
        if select_all == 0:
            self.cursor.execute(sql, tuple(data.values()))
            self.db.commit()
        else:
            pass
        return item

