import threading
import time
import random
import json
import datetime

from core import AmiyaBot
from core.resolver.messageChain import Chain
from core.database.models import ReplyRecord, GroupActive, LatestAutoReply, MsgRecord


class ActiveReply:
    def __init__(self, bot: AmiyaBot):
        self.bot = bot

    def start(self):
        threading.Thread(target=self.run).start()

    def time(self):
        groups = GroupActive.select().where(GroupActive.active == 1)

        for group in groups:

            group_id = group.group_id
            print('active reply', group_id)

            auto_reply_time_list = LatestAutoReply.select().where(
                LatestAutoReply.group_id == group_id).limit(1)

            if not auto_reply_time_list:
                LatestAutoReply.insert(group_id=group_id).execute()
                continue
            
            auto_reply_time = auto_reply_time_list[0].time
            print('auto_reply_time', auto_reply_time)

            msg_list = MsgRecord.select().where(
                MsgRecord.group_id == group.group_id
            ).order_by(
                MsgRecord.time.desc()
            ).limit(1)

            if not msg_list:
                continue

            msg_time = msg_list[0].time
            
            print('msg_time', msg_time)

            # 没人说话之后，兔兔仅主动回复一次
            if auto_reply_time and auto_reply_time > msg_time:
                continue
            
            time_interval: int = (time.time() - msg_time) / 60  # 上一次有人说话到现在的时间间隔，单位分钟
            rand_hour = random.randint(30, 180)   # 时间间隔越大，触发主动对话概率越高，180分钟以上就必触发

            if rand_hour < time_interval:
                print('ready to active reply')

                reply_list = ReplyRecord.select().where(
                    ReplyRecord.group_id == group_id,
                    ReplyRecord.count >= 2
                ).order_by(ReplyRecord.count.desc()).limit(20)
                if not reply_list:
                    continue

                LatestAutoReply.update(time=time.time()).where(
                    LatestAutoReply.group_id == group_id).execute()

                reply_rec = reply_list[random.randint(
                    0, len(reply_list) - 1)]
                with self.bot.send_custom_message(group_id=group_id) as reply:
                    reply.chain = json.loads(reply_rec.pre_msg)
                
                # 有一定概率连发两句=。=
                if random.randint(0, 10) < 5:
                    time.sleep(1)
                    with self.bot.send_custom_message(group_id=group_id) as reply:
                        reply.chain = json.loads(reply_rec.reply_msg)
                


    def run(self):
        while True:
            hour = datetime.datetime.now().hour
            if hour > 1 and hour < 9:
                time.sleep(7200)
            min = random.randint(40, 60)
            time.sleep(min * 60)
            self.time()
