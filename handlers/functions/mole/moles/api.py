import json

import requests


class char:
    def __init__(self, map: dict):
        self.name = map['name']
        self.rarity = map['rarity']
        self.isNew = map['isNew']

    name: str
    rarity: int
    isNew: bool


class draw:
    def __init__(self, map: dict):
        self.uid = map['uid']
        self.ts = map['ts']
        self.chars = []
        for c in map['chars']: self.chars.append(char(c))

    uid: str
    ts: int
    chars: list


host = 'http://www.moles.top'


def get(length=100):
    resp = requests.get(f'{host}/ark/list', params={'length': length})
    data = json.loads(resp.text)
    draws = []
    for j in data:
        draws.append(draw(j))
    return draws


def all(): return get(-1)


if __name__ == '__main__':
    for i in get(1):
        print(i.chars[0].name)
