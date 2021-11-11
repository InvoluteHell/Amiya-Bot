import os

import requests


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
