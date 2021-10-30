import random

from core.database.models import Message
from core.resolver.messageChain import Chain
from dataSource import DataSource
from handlers.constraint import FuncInterface
from .pixivel import *

class keeper:
    def __init__(self):
        self.page=0
        self.history=set()
        self.cache=list()

    def reload(self):
        new = rec(self.page)
        self.page += 1
        for pic in new:
            if pic['id'] not in self.history:self.cache.append(pic)
    def random(self):
        while len(self.cache)==0:self.reload()
        pic=self.cache.pop(random.randint(0,len(self.cache)-1))
        self.history.add(pic['id'])
        return pic

class PixivHandler(FuncInterface):
    def __init__(self,data_source: DataSource):
        super().__init__(function_id='sese')
        self.data = data_source
        self.keeper=keeper()

    @FuncInterface.is_disable
    def verify(self, data: Message):
        for item in ['涩涩']:
            if item in data.text:
                return 10

    @FuncInterface.is_used
    def action(self, data: Message):
        reply = Chain(data)
        pic = self.keeper.random()
        return reply.text('https://www.pixiv.net/artworks/{}'.format(pic['id'])).image(url(pic))
