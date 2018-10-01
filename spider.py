import requests
from urllib.parse import urlencode

from pyquery import PyQuery as pq
from pymongo import MongoClient

base_url = 'https://m.weibo.cn/api/container/getIndex?'
max_page = 10
client = MongoClient()
db = client['weibo']
collection = db['weibo']

headers = {
    'Host':'m.weibo.cn',
    'Referer':'https://m.weibo.cn/u/2830678474',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    'X-Requested-With':'XMLHttpRequest',
}

def get_page(page):
    params = {
        'type':'uid',
        'value':'2830678474',
        'containerid':'1076032830678474',
        'page':page
    }
    url = base_url + urlencode(params)
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.json(),page
    except requests.ConnectionError as e:
        print('Error',e.args)

def parse_page(json,page:int):
    if json:
        items = json.get('data').get('cards')
        for index,item in enumerate(items):
            if page == 1 and index == 1:
                continue
            else:
                item = item.get('mblog')
                weibo = {}
                weibo['id'] = item.get('id')  # 用户id
                weibo['text'] = pq(item.get('text')).text()  # 微博文本
                weibo['attitudes'] = item.get('attitudes_count')  # 点赞数
                weibo['comments'] = item.get('comments_count')  # 评论数
                weibo['reposts'] = item.get('reposts_count')  # 转发数
                yield weibo

def save_to_mongo(result):
    if collection.insert(result):
        print('Saved to Mongo')

if __name__ == '__main__':
    for page in range(1,max_page+1):
        json = get_page(page)
        results = parse_page(*json)
        for result in results:
            print(result)
            save_to_mongo(result)



