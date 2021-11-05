from core import Message, Chain
from core.database.models import MsgRecord, ReplyRecord
from handlers.constraint import FuncInterface
from core import AmiyaBot
import time

@FuncInterface.is_disable_func(function_id='autoreply')
def autoreply(data: Message, bot: AmiyaBot):
    return False
    with bot.send_custom_message(group_id=data.group_id) as reply:
        reply: Chain
        reply.text('autoreply')

def record(data: Message):
    msg = MsgRecord.select().where(
        MsgRecord.group_id==data.group_id,
        MsgRecord.user_id==data.user_id).order_by(
            MsgRecord.time.desc()).limit(1)
    if msg:
        print('latest message: %s' % msg[0].msg)
    MsgRecord.insert(group_id=data.group_id, 
        user_id=data.user_id, 
        msg=data.text_origin, 
        time=time.time()).execute()
    