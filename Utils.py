import requests, asyncio, logging
from functools import wraps
from peewee import MySQLDatabase
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from models import V2User
from config import URL, EMAIL, PASSWORD, SUFFIX, SLOT_MACHINE, DICE_RATE, AUTO_DELETE

START_ROUTES, END_ROUTES = 0, 1

WAITING_INPUT = 2


def _admin_auth():  # 返回网站管理员auth_data
    api = URL + '/api/v1/passport/auth/login'
    data = {
        'email': EMAIL,
        'password': PASSWORD,
    }
    res = requests.post(api, data=data)
    return res.json()['data']['auth_data']


def getNodes():
    api = f'{URL}/api/v1/{SUFFIX}/server/manage/getNodes'
    headers = {
        'Authorization': _admin_auth()
    }
    res = requests.get(api, headers=headers)
    text = ''
    for item in res.json()['data']:
        if item['show'] == 0:
            continue
        status = '在线' if item['available_status'] else '离线'
        online = item['online'] if item['online'] else '0'
        online += "人"
        line = '节点名称:' + item['name'] + '\n' + '节点状态:' + status + '\n' + '在线人数:' + online + '\n'
        text += line + '----------------------------' + '\n'
    return text

def auto_delete_required(func):
    # 用functools.wraps来保留原函数的属性和文档
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 检查auto_delete的值
        if AUTO_DELETE:
            return func(*args, **kwargs)
        else:
            pass
    return wrapper

@auto_delete_required
async def delete_both_messages(update, context):
    # 获取用户消息的id和chat id
    user_message_id = update.message.message_id
    user_chat_id = update.message.chat_id
    # 获取bot消息的id和chat id
    bot_message_id = context.bot_data['bot_message_id']
    bot_chat_id = context.bot_data['bot_chat_id']
    # 获取bot在当前聊天中的状态
    bot_status = await context.bot.get_chat_member(chat_id=user_chat_id, user_id=context.bot.id)
    # 判断bot是否有删除消息的权限
    if bot_status.can_delete_messages:
        # 如果有，就等待5秒
        await asyncio.sleep(5)
        # 同时删除用户和bot的消息
        await asyncio.gather(
            context.bot.delete_message(chat_id=user_chat_id, message_id=user_message_id),
            context.bot.delete_message(chat_id=bot_chat_id, message_id=bot_message_id)
        )
    else:
        # 如果没有，就打印一个警告信息
        logging.warning(f"Warning: Bot does not have permission to delete messages in chat {user_chat_id}")


async def slot_machine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    v2_user = V2User.select().where(V2User.telegram_id == update.effective_user.id).first()
    if not v2_user:
        await update.message.reply_text(text='未绑定,请先绑定')
        return ConversationHandler.END

    traffic = v2_user.transfer_enable / 1024 ** 3
    if not update.message.dice:
        await update.message.reply_text(text='你发送的不是🎰表情，此局无效')
        return ConversationHandler.END
    if traffic < 1:
        bot_message = await update.message.reply_text(text='你的流量已不足1GB，无法进行游戏')
        # 保存bot消息的id和chat id到context.bot_data中
        context.bot_data['bot_message_id'] = bot_message.message_id
        context.bot_data['bot_chat_id'] = bot_message.chat_id
        # 调用delete_both_messages函数来删除用户和bot的消息
        asyncio.get_event_loop().create_task(delete_both_messages(update, context))
        return ConversationHandler.END

    if update.message.forward_from or update.message.forward_sender_name:
        v2_user.transfer_enable -= 1024 ** 3
        v2_user.save()
        bot_message = await update.message.reply_text(text=f'由于你想投机取巧，因此没收你的下注流量!\n不和没有诚信的人玩，游戏结束!\n当前账户流量：{round(v2_user.transfer_enable / 1024 ** 3, 2)}GB')
        context.bot_data['bot_message_id'] = bot_message.message_id
        context.bot_data['bot_chat_id'] = bot_message.chat_id
        asyncio.get_event_loop().create_task(delete_both_messages(update, context))
        return ConversationHandler.END
    elif update.message.dice.emoji == '🎰' and update.message.dice.value in [1, 22, 43, 64]:
        v2_user.transfer_enable += (SLOT_MACHINE - 1) * 1024 ** 3
        v2_user.save()
        await update.message.reply_text(
            text=f'恭喜你中奖了，获得{SLOT_MACHINE}GB流量已经存入你的账户\n当前账户流量：{round(v2_user.transfer_enable / 1024 ** 3, 2)}GB')
    elif update.message.dice.emoji == '🎲':
        user = update.message.dice.value
        bot_message = await update.message.reply_dice(emoji='🎲')
        bot = bot_message.dice.value
        if bot > user:
            v2_user.transfer_enable -= 1024 ** 3
            v2_user.save()
            bot_message = await update.message.reply_text(
                text=f'很遗憾你没有中奖，流量已从你账户扣除1GB\n当前账户流量：{round(v2_user.transfer_enable / 1024 ** 3, 2)}GB')
            context.bot_data['bot_message_id'] = bot_message.message_id
            context.bot_data['bot_chat_id'] = bot_message.chat_id
            asyncio.get_event_loop().create_task(delete_both_messages(update, context))
        elif bot == user:
            bot_message = await update.message.reply_text(
                text=f'平局，已返还下注流量\n当前账户流量：{round(v2_user.transfer_enable / 1024 ** 3, 2)}GB')
            context.bot_data['bot_message_id'] = bot_message.message_id
            context.bot_data['bot_chat_id'] = bot_message.chat_id
            asyncio.get_event_loop().create_task(delete_both_messages(update, context))
        else:
            v2_user.transfer_enable += (DICE_RATE - 1) * 1024 ** 3
            v2_user.save()
            await update.message.reply_text(
                text=f'恭喜你中奖了，获得{DICE_RATE}GB流量已经存入你的账户\n当前账户流量：{round(v2_user.transfer_enable / 1024 ** 3, 2)}GB')
    else:
        v2_user.transfer_enable -= 1024 ** 3
        v2_user.save()
        bot_message = await update.message.reply_text(
            text=f'很遗憾你没有中奖，流量已从你账户扣除1GB\n当前账户流量：{round(v2_user.transfer_enable / 1024 ** 3, 2)}GB')
        # 保存bot消息的id和chat id到context.bot_data中
        context.bot_data['bot_message_id'] = bot_message.message_id
        context.bot_data['bot_chat_id'] = bot_message.chat_id
        asyncio.get_event_loop().create_task(delete_both_messages(update, context))
    print()
    return WAITING_INPUT


if __name__ == '__main__':
    print(getNodes())
