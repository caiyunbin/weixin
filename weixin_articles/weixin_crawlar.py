# -*- coding: utf-8 -*-
from selenium import webdriver
import json
import re
import time
import pymongo
import requests
import random
from pyquery import PyQuery as pq
from get_config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
keyword = KEYWORD
number = PAGE_NUMBER
browser = webdriver.Chrome()
browser.get('https://mp.weixin.qq.com/')
browser.maximize_window()
time.sleep(2)
browser.find_element_by_xpath("//*[@id=\"header\"]/div[2]/div/div/form/div[1]/div[1]/div/span/input").clear()
browser.find_element_by_xpath("//*[@id=\"header\"]/div[2]/div/div/form/div[1]/div[1]/div/span/input").send_keys(USERNAME)
browser.find_element_by_xpath("//*[@id=\"header\"]/div[2]/div/div/form/div[1]/div[2]/div/span/input").clear()
browser.find_element_by_xpath("//*[@id=\"header\"]/div[2]/div/div/form/div[1]/div[2]/div/span/input").send_keys(PASSWORD)
time.sleep(1.5)
browser.find_element_by_xpath("//*[@id=\"header\"]/div[2]/div/div/form/div[3]/label/i").click()
time.sleep(1.5)
browser.find_element_by_xpath("//*[@id=\"header\"]/div[2]/div/div/form/div[4]/a").click()
print('请拿出手机扫')
time.sleep(15)
###取出cookie保存
cookie = browser.get_cookies()
for item in cookie:
    cookiejar[item.get('name')] = item.get('value')

response = requests.get('https://mp.weixin.qq.com/',cookies = cookiejar)
token = re.findall(r'token=(\d+)', response.url)[0]

second_dicts ={
            'action': 'search_biz',
            'token': token,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1',
            'random': random.random(),
            'query': keyword,
            'begin': '0',
            'count': '5'
        }

response1 = requests.get('https://mp.weixin.qq.com/cgi-bin/searchbiz?',params=second_dicts,cookies=cookiejar)
fake_id = response1.json().get('list')[0].get('fakeid')

def get_roll_articles(token,begin,fakeid):
    print('正在爬取第:%d页'%(begin))
    data = {
        'token': token,
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1',
        'random': random.random(),
        'action': 'list_ex',
        'begin': '{}'.format(str(begin)),
        'count': '5',
        'query': '',
        'fakeid': fakeid,
        'type': '9'
    }
    try:
        response = requests.get('https://mp.weixin.qq.com/cgi-bin/appmsg?',params=data,cookies=cookiejar)
        if response.status_code == 200:
            response_json = response.json()
            return response_json
        return None
    except requests.exceptions:
        return None


def get_page_number(number):
    total = int(number.get('app_msg_cnt')) // 5 + 1
    return int(total)


def parse_page(html):
    json_list = html.get('app_msg_list')
    for item in json_list:
        yield item.get('link')

def get_detail(link):
    try:
        response = requests.get(link)
        if response.status_code == 200:
            return response.text
        return None
    except requests.exceptions:
        return None

def parse_detail(html):
    doc = pq(html)
    return {
        'title':doc('.rich_media_title').text().strip(),
        'content':doc('.rich_media_content').text().strip(),
        'nickname':doc('#js_name').text().strip()
    }


def save_to_mongo(data):
    if db['article1'].update({'title':data['title']},{'$set':data},True):
        print('save to mongo',data['title'])
    else:
        print('save to mongo failed',data['title'])



def main():
    for begin in range(973,number):
        urls = get_roll_articles(token,begin*5,fake_id)
        links = parse_page(urls)
        for link in links:
            html = get_detail(link)
            if html:
                parse_ful = parse_detail(html)
                print(parse_ful)
                if parse_ful:
                    save_to_mongo(parse_ful)
                    time.sleep(random.randint(4,6))

if __name__ == '__main__':
    main()








