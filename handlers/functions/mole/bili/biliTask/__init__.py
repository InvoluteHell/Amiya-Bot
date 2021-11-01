import time

from core import AmiyaBot
from core.resolver.messageChain import Chain
from .api import *
from ...tools import pic

mid=4506341
groups=[672372860]

class biliTask:
    def __init__(self,bot:AmiyaBot):
        self.bot=bot
        self.run()

    last:bool=False
    def time(self):
        user=api.user(mid)
        now =user.room.liveStatus is 1
        if now and not self.last:
            for group in groups:
                with self.bot.send_custom_message(group_id=group) as reply:
                    reply: Chain
                    reply.text(user.room.url).image(pic(user.room.cover))
        self.last=now
        time.sleep(8)

    async def run(self):
        while True:self.time()

