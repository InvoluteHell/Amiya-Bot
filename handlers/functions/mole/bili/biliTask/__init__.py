import threading
import time

from core import AmiyaBot
from core.resolver.messageChain import Chain
from .api import *
from ...tools import pic

mid=4506341
groups=[672372860, 716692626]

class biliTask:
    def __init__(self,bot:AmiyaBot):
        self.bot=bot

    def start(self):
        threading.Thread(target=self.run).start()

    last:bool=api.user(mid).room.liveStatus is 1
    def time(self):
        user=api.user(mid)
        now =user.room.liveStatus is 1
        if now and not self.last:
            for group in groups:
                with self.bot.send_custom_message(group_id=group) as reply:
                    reply: Chain
                    reply.text('开播啦！').text(user.room.title).image(pic(user.room.cover)).text(user.room.url)
        self.last=now
        time.sleep(8)

    def run(self):
        while True:
            self.time()

