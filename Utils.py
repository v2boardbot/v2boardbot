import requests
from peewee import MySQLDatabase
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from models import V2User
from config import URL, EMAIL, PASSWORD, SUFFIX, SLOT_MACHINE

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
        await update.message.reply_text(text='你的流量已不足1GB，无法进行游戏')
        return ConversationHandler.END
    elif update.message.dice.value in [1, 22, 43, 64]:
        v2_user.transfer_enable += SLOT_MACHINE * 1024 ** 3
        v2_user.save()
        await update.message.reply_text(text=f'恭喜你中奖了，获得{SLOT_MACHINE}GB流量已经存入你的账户')
    else:
        await update.message.reply_text(text='很遗憾你没有中奖，流量已从你账户扣除1GB')
        v2_user.transfer_enable -= 1024 ** 3
        v2_user.save()
    return WAITING_INPUT

if __name__ == '__main__':
    print(getNodes())
