# !/usr/bin/env python
# -*- coding:utf-8 -*-
import time
import datetime
import asyncio
import aiohttp
import pymongo
from lxml import html
from learnpython.picture.settings import *

class base_spider:
    def __init__(self,url):
        self.total_count_set=set()
        self.finish_count_set=set()
        self.error_count_set=set()
        self.loop=asyncio.get_event_loop()
        self.session= aiohttp.ClientSession(loop=self.loop)
        self.url=url
        self.headers={}
        self.client = pymongo.MongoClient()
        self.db = self.client[MONGO_DB]
        self.collection = self.db[MONGO_DETAIL]
        asyncio.ensure_future(self.fetch())

    async def fetch(self):
        with aiohttp.Timeout(60):
            async with self.session.get(self.url, headers=self.headers) as resp:
                asyncio.ensure_future(self.find_all_img_url(await resp.read()))

    async def find_all_img_url(self,response):
        response=html.fromstring(response)
        img_url_list=response.xpath('//img/@src')
        img_url_list=[img if img.startswith('http') else ('http://photo.poco.cn/'+img if not img.startswith('//') else 'http://'+img) for img in img_url_list]
        print(img_url_list)
        asyncio.ensure_future(self.dowlond_all_img_url(img_url_list))

    async def dowlond_all_img_url(self, img_url_list):
        for img in img_url_list:
            name = img.split('/')[-1]
            img_dic={
                'source':self.url,
                'name':name,
                'url':img,
                'status':False, #默认都没有爬成功
                'ts_string': str(datetime.date.today()),
                'ts':str(datetime.datetime.fromtimestamp(time.time(), None)),
            }
            asyncio.ensure_future(self.insert_mongo(img_dic))
            with aiohttp.Timeout(60):
                async with self.session.get(img, headers=self.headers) as resp:
                    asyncio.ensure_future(self.write_img(await resp.read(),name))

    async def write_img(self,img_resp,img_name):
        path='../pics/'
        f=open(path+img_name,'wb')
        f.write(img_resp)
        f.close()
        asyncio.ensure_future(self.update_img_status_mongo(img_name))

    async def insert_mongo(self,img_dic):
        self.collection.insert(img_dic)

    async def update_img_status_mongo(self, img_name):
        '''
        更新图片状态为下载成功
        :param img_name: 
        :return: 
        '''
        self.collection.update({'name':img_name},{'$set':{'status':True}})

    def run(self):
        self.loop.run_forever()

    def stop(self):
        self.loop.stop()

if __name__ == '__main__':
    data_crawl = base_spider('http://photo.poco.cn/')
    data_crawl.run()

