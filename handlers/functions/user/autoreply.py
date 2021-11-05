from core import Message, Chain
from core.database.models import MsgRecord, ReplyRecord
from handlers.constraint import FuncInterface
from core import AmiyaBot
import time
import random

reply_count_threshold = 3

@FuncInterface.is_disable_func(function_id='autoreply')
def autoreply(data: Message, bot: AmiyaBot):
    reply_list = ReplyRecord.select().where(
        ReplyRecord.group_id==data.group_id,
        ReplyRecord.pre_msg==data.text_origin,
        ReplyRecord.count >= reply_count_threshold
    ).order_by(ReplyRecord.count.desc()).limit(3)

    if reply_list:
        rand_index = random.randint(0, len(reply_list) - 1)
        reply_rec = reply_list[rand_index]
        with bot.send_custom_message(group_id=data.group_id) as reply:
            reply.text(reply_rec.reply_msg)

def record(data: Message):
    msg_list = MsgRecord.select().where(
        MsgRecord.group_id==data.group_id
        ).order_by(
            MsgRecord.time.desc()
        ).limit(1)
    if msg_list:
        msg = msg_list[0]
        if msg.msg == data.text_origin:
            pass    # 说明是在复读
        else:
            print('latest message: %s' % msg.msg, 'cur message : %s' % data.text_origin)
            reply_list = ReplyRecord.select().where(
                ReplyRecord.group_id==msg.group_id,
                ReplyRecord.pre_msg==msg.msg,
                ReplyRecord.reply_msg==data.text_origin
            ).limit(1)
            if reply_list:
                reply = reply_list[0]
                new_cout = reply.count+1
                print('update count', new_cout)
                ReplyRecord.update(count=new_cout).where(ReplyRecord.id==reply.id).execute()
            else:
                print('insert')
                ReplyRecord.insert(
                    group_id=msg.group_id,
                    pre_msg=msg.msg,
                    reply_msg=data.text_origin
                ).execute()

    MsgRecord.insert(
        group_id=data.group_id, 
        user_id=data.user_id, 
        msg=data.text_origin, 
        time=time.time()
    ).execute()
    