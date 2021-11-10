from core import Message, Chain
from core.database.models import MsgRecord, ReplyRecord, LatestAutoReply
from handlers.constraint import FuncInterface
from core import AmiyaBot
import time
import random
import json
import threading

reply_count_threshold = 2

@FuncInterface.is_disable_func(function_id='autoreply')
def autoreply(data: Message, bot: AmiyaBot):
    chain = json.dumps(data.raw_chain)

    latest_reply = LatestAutoReply.select().where(LatestAutoReply.group_id== data.group_id).execute()

    if latest_reply:
        time_interval: int = time.time() - latest_reply[0].time
        rand_sec = random.randint(5, 10)   # 时间间隔越大，触发主动对话概率越高
        if rand_sec > time_interval:
            return

    reply_list = ReplyRecord.select().where(
        ReplyRecord.group_id == data.group_id,
        ReplyRecord.pre_msg == chain,
        ReplyRecord.count >= reply_count_threshold
    ).order_by(ReplyRecord.count.desc()).limit(5)

    if reply_list:
        rand_index = random.randint(0, len(reply_list) - 1)
        msg = reply_list[rand_index].reply_msg
        delay = random.randint(10, 30)
        LatestAutoReply.insert(
            group_id=data.group_id,
            msg=chain,
            time=time.time() + delay
        ).on_conflict('replace').execute()
        timer = threading.Timer(delay, reply_func, (data.group_id, msg, bot,))
        timer.start()

def reply_func(group_id, msg, bot: AmiyaBot):
    with bot.send_custom_message(group_id=group_id) as rep:
        rep.chain = json.loads(msg)

def record(data: Message):
    chain = json.dumps(data.raw_chain)

    msg_list = MsgRecord.select().where(
        MsgRecord.group_id == data.group_id
    ).order_by(
        MsgRecord.time.desc()
    ).limit(1)
    if msg_list:
        msg = msg_list[0]
        if msg.user_id == data.user_id:
            # 上一条也是这个人说的
            # 第三个参数True，自己复读自己，有可能是兔兔时间间隔拒掉了，这个人又发了一遍
            update_reply_record(chain, msg, False)
        else:
            # 上一条不是这个人说的
            update_reply_record(chain, msg, False)
            # 这个人说的上一条
            self_msg_list = MsgRecord.select().where(
                MsgRecord.group_id == data.group_id,
                MsgRecord.user_id == data.user_id
            ).order_by(
                MsgRecord.time.desc()
            ).limit(1)
            if self_msg_list:
                self_msg = self_msg_list[0]
                if msg.msg != self_msg.msg:
                    update_reply_record(chain, self_msg_list[0], False)

    MsgRecord.insert(
        group_id=data.group_id,
        user_id=data.user_id,
        msg=chain,
        time=time.time()
    ).execute()


def update_reply_record(chain, msg: MsgRecord, enable_repeat=False):
    if time.time() - msg.time > 600:   # 十分钟之前的了，忽略掉
        return
    if msg.msg == chain:    # 说明是在复读
        if enable_repeat:
            pass
        else:
            return
    print('latest message: %s' % msg.msg, 'cur message : %s' % chain)
    # 如果有反过来的，直接退出，说明可能是两句话在轮流复读。只取正向的（先达到阈值的）
    reverse_list = ReplyRecord.select().where(
        ReplyRecord.group_id == msg.group_id,
        ReplyRecord.pre_msg == chain,
        ReplyRecord.reply_msg == msg.msg,
        ReplyRecord.count >= reply_count_threshold
    ).limit(1)
    if reverse_list:
        return

    reply_list = ReplyRecord.select().where(
        ReplyRecord.group_id == msg.group_id,
        ReplyRecord.pre_msg == msg.msg,
        ReplyRecord.reply_msg == chain
    ).limit(1)
    if reply_list:
        reply = reply_list[0]
        new_cout = reply.count+1
        print('update count', new_cout)
        ReplyRecord.update(count=new_cout).where(
            ReplyRecord.id == reply.id).execute()
    else:
        print('insert')
        ReplyRecord.insert(
            group_id=msg.group_id,
            pre_msg=msg.msg,
            reply_msg=chain
        ).execute()
