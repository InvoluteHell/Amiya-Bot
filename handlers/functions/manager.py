import time
import json

from core import Message, Chain
from core.database.models import GroupActive, ReplyRecord
from core.util.common import word_in_sentence, calc_time_total


def manager_handler(data: Message):
    message = data.text
    reply = Chain(data)

    if data.is_call and (data.is_admin or data.is_group_admin):
        if word_in_sentence(message, ['休息', '下班']):
            if data.group_active.active == 1:
                GroupActive.update(active=0, sleep_time=int(time.time())).where(
                    GroupActive.group_id == data.group_id).execute()
                return reply.text('打卡下班啦！博士需要阿米娅的时候再让阿米娅工作吧。^_^')

        if word_in_sentence(message, ['工作', '上班']):
            if data.group_active.active == 0:
                seconds = int(time.time()) - int(data.group_active.sleep_time)
                total = calc_time_total(seconds)
                text = '打卡上班啦~阿米娅%s休息了%s……' % (
                    '才' if seconds < 600 else '一共', total)
                if seconds < 600:
                    text += '\n博士真是太过分了！哼~ >.<'
                else:
                    text += '\n充足的休息才能更好的工作，博士，不要忘记休息哦 ^_^'

                GroupActive.update(active=1, sleep_time=0).where(
                    GroupActive.group_id == data.group_id).execute()
                return reply.text(text)
            else:
                return reply.text('阿米娅没有偷懒哦博士，请您也不要偷懒~')

        if word_in_sentence(message, ['不可以涩涩', '不准涩涩']):
            if data.group_active.active == 1 and data.group_active.hso == 1:
                GroupActive.update(hso=0).where(
                    GroupActive.group_id == data.group_id).execute()
                return reply.text('涩涩下班啦！博士需要涩涩的时候再让阿米娅工作吧。^_^')
                
        elif word_in_sentence(message, ['可以涩涩']):
            if data.group_active.active == 1 and data.group_active.hso == 0:
                GroupActive.update(hso=1).where(
                    GroupActive.group_id == data.group_id).execute()
                return reply.text('涩涩上班啦！充足的休息才能更好的工作，博士，不要忘记休息哦 ^_^')

        if word_in_sentence(message, ['不可以', '不准', '不能']):
            if data.raw_chain[0]['type'] == 'Quote':
                quote_text = data.raw_chain[0]['origin'][0]
                # 图片在引用里只有这俩字，似乎是使用id字段定位的，暂时不知道怎么处理
                if word_in_sentence(quote_text, ['[图片]', '[动画表情]']):
                    pass
                else:
                    dumps = json.dumps(quote_text)
                    ReplyRecord.update(
                        count=-5).where(ReplyRecord.reply_msg.contains(dumps)).execute()
                    return reply.text('阿米娅知道错了……')

    return data.group_active.active == 1
