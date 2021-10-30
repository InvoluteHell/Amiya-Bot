from core.database.models import Message
from core.resolver.messageChain import Chain
from dataSource import DataSource
from handlers.constraint import FuncInterface


class PixivHandler(FuncInterface):
    def __init__(self,data_source: DataSource):
        super().__init__(function_id='sese')
        self.data = data_source

    @FuncInterface.is_disable
    def verify(self, data: Message):
        for item in ['涩涩']:
            if item in data.text:
                return 10

    @FuncInterface.is_used
    def action(self, data: Message):
        reply = Chain(data)
        return reply.text('不可以涩涩！')
