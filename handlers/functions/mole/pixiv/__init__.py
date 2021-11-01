from dataSource import DataSource
from .pixivHandler import PixivHandler


class Pixiv(DataSource):
    def __init__(self, bot):
        super().__init__(auto_update=True, check_assets=True)

        self.PixivHandler =PixivHandler(self)

        self.funcs = [
            self.PixivHandler,
        ]
