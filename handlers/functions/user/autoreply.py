from core import Message, Chain
from core.database.models import MsgRecord, ReplyRecord
from handlers.constraint import FuncInterface
from core import AmiyaBot
import time
import random
import json

reply_count_threshold = 2

@FuncInterface.is_disable_func(function_id='autoreply')
def autoreply(data: Message, bot: AmiyaBot):
    chain = json.dumps(data.raw_chain)

    reply_list = ReplyRecord.select().where(
        ReplyRecord.group_id==data.group_id,
        ReplyRecord.pre_msg==chain,
        ReplyRecord.count >= reply_count_threshold
    ).order_by(ReplyRecord.count.desc()).limit(5)

    if reply_list:
        rand_index = random.randint(0, len(reply_list) - 1)
        reply_rec = reply_list[rand_index]
        with bot.send_custom_message(group_id=data.group_id) as reply:
            reply.chain = json.loads(reply_rec.reply_msg)

def record(data: Message):
    chain = json.dumps(data.raw_chain)

    # 上一条不是这个人的
    msg_list = MsgRecord.select().where(
        MsgRecord.group_id==data.group_id,
        MsgRecord.user_id!=data.user_id
        ).order_by(
            MsgRecord.time.desc()
        ).limit(1)
    update_reply_record(chain, msg_list, False)

    # 这个人说的上一条
    msg_list = MsgRecord.select().where(
        MsgRecord.group_id==data.group_id,
        MsgRecord.user_id==data.user_id
        ).order_by(
            MsgRecord.time.desc()
        ).limit(1)
    update_reply_record(chain, msg_list, True)  # 第三个参数True，自己复读自己，多半是想教兔兔

    MsgRecord.insert(
        group_id=data.group_id, 
        user_id=data.user_id, 
        msg=chain, 
        time=time.time()
    ).execute()
    
def update_reply_record(chain, msg_list: list, enable_repeat = False):
    if msg_list:
        msg = msg_list[0]
        if msg.msg == chain:    # 说明是在复读
            if enable_repeat:
                pass
            else:
                return
        print('latest message: %s' % msg.msg, 'cur message : %s' % chain)
        reply_list = ReplyRecord.select().where(
            ReplyRecord.group_id==msg.group_id,
            ReplyRecord.pre_msg==msg.msg,
            ReplyRecord.reply_msg==chain
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
                reply_msg=chain
            ).execute()