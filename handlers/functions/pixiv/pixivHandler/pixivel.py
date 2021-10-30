import json
import requests

def rec(page:int):
    url = "https://api-jp1.pixivel.moe/pixiv?type=illust_recommended&page={}".format(page)
    res = json.loads(requests.get(url).text)
    return res['illusts']

def url(pic):
    meta_pages = pic['meta_pages']
    if len(meta_pages)==0: url = pic['meta_single_page']['original_image_url']
    else: url = meta_pages[0]['image_urls']['original']
    return url.replace('i.pximg.net','proxy-jp1.pixivel.moe')
import os
def make_folder(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except FileExistsError:
            pass

def pic(url):
    name = url.split('/')[-1]
    suffix = name.split('.')[-1]
    temp = 'log/weibo'
    path = f'{temp}/{name}'
    make_folder(temp)
    if os.path.exists(path) is False:
        stream = requests.get(url, stream=True)
        if stream.status_code == 200:
            open(path, 'wb').write(stream.content)
    return path
