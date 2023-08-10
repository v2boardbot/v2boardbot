import time
from datetime import datetime

import requests
from peewee import *
import random

from Utils import getNodes
from config2 import URL
from models import V2User, BotUser, V2ServerVmess


def get_sky(cityName):
    url = 'https://ssch.api.moji.com/citymanage/json/h5/searchCity'
    data = {
        'keyWord': cityName
    }
    res = requests.post(url, data=data)
    try:
        cityId = res.json()['city_list'][0]['cityId']
    except:
        return 'cty_name error'
    url = 'https://h5ctywhr.api.moji.com/weatherDetail'
    data = {"cityId": cityId, "cityType": 0}
    res = requests.post(url, json=data)
    obj = res.json()
    temp = obj['condition']['temp']
    humidity = obj['condition']['humidity']
    weather = obj['condition']['weather']
    wind = obj['condition']['windDir'] + ' ' + str(obj['condition']['windLevel']) + '级'
    tips = obj['condition']['tips']
    city = f"{obj['provinceName']}-{obj['cityName']}"
    return f'''地区:{city}
温度:{temp} 湿度:{humidity}
天气:{weather} 风向:{wind}
提示:{tips}'''


def _addtime(day: int):
    v2_users = V2User.select().where(V2User.expired_at > 0).execute()
    second = day * 24 * 60 * 60
    print(second)
    for v2_user in v2_users:
        v2_user.expired_at += second
        v2_user.save()
    return f'{len(v2_users)}个有效用户添加成功{day}天时长成功'


def _wallet(telegram_id):
    v2_user = V2User.select().where(V2User.telegram_id == telegram_id).first()
    if not v2_user:
        return '未绑定,请先绑定'
    text = f'''💰我的钱包
————————————
钱包总额：{round((v2_user.balance + v2_user.commission_balance) / 100, 2)} 元
账户余额：{round(v2_user.balance / 100, 2)} 元
推广佣金：{round(v2_user.commission_balance / 100, 2)} 元
'''
    return text


def _bind(token, telegram_id):
    # 查询telegram_id是否绑定了其他账号
    botuser = BotUser.select().where(BotUser.telegram_id == telegram_id).first()
    if botuser:
        return '该Telegram已经绑定了一个账号，请先解绑再绑定'
    v2_user = V2User.select().where(V2User.token == token).first()
    if not v2_user:
        return '用户不存在'
    if v2_user.telegram_id:
        return '该账号已经绑定了Telegram账号'

    BotUser.create(telegram_id=telegram_id, v2_user=v2_user)
    v2_user.telegram_id = telegram_id
    v2_user.save()
    return '绑定成功'


def _unbind(telegram_id):
    bot_user = BotUser.select().where(BotUser.telegram_id == telegram_id).first()
    if bot_user:
        bot_user.v2_user.telegram_id = None
        bot_user.v2_user.save()
        bot_user.delete_instance()
        # V2User.update(telegram_id=None).where(V2User.telegram_id == telegram_id).execute()
        return '解绑成功'
    else:
        return '该Telegram未绑定任何账号'


def _checkin(telegram_id):
    botuser = BotUser.select().where(BotUser.telegram_id == telegram_id).first()
    if not botuser:
        return '未绑定,请先绑定'

    if botuser.v2_user.expired_at in [None, 0]:
        return '不限时套餐或未订阅不支持签到'

    # 检查今天是否签到过了
    if botuser.sign_time and botuser.sign_time.date() == datetime.today().date():
        return '你今天已经签到过了，明天再来哦'

    num = random.randint(1024, 2048)
    flow = num * 1024 * 1024
    botuser.v2_user.transfer_enable += flow
    botuser.sign_time = datetime.now()
    botuser.v2_user.save()
    botuser.save()

    return f'签到成功,获得{round(num / 1024, 2)}GB流量'


def _sub(telegram_id):
    v2_user = V2User.select().where(V2User.telegram_id == telegram_id).first()
    if not v2_user:
        return '未绑定,请先绑定'
    if v2_user.expired_at == None:
        expired_at = '∞'
        expired_time = '不限时套餐'
    elif v2_user.expired_at == 0:
        expired_at = '-∞'
        expired_time = '未订阅'
    else:
        now_time = datetime.now()
        expired_at = (datetime.fromtimestamp(v2_user.expired_at) - now_time).days
        expired_time = datetime.fromtimestamp(v2_user.expired_at).strftime('%Y-%m-%d')
    if expired_time == '未订阅':
        text = '未订阅任何套餐，请先订阅'
    else:
        text = f'''我的订阅
————————————
套餐名称：{v2_user.plan_id.name}
套餐流量：{v2_user.plan_id.transfer_enable} GB
离重置流量还有： {expired_at}天
到期时间：{expired_time}
'''
    return text


def _mysub(telegram_id):
    v2_user = V2User.select().where(V2User.telegram_id == telegram_id).first()
    if not v2_user:
        return '未绑定,请先绑定'
    return f'您的订阅链接:{URL}/api/v1/client/subscribe?token={v2_user.token}'


def _lucky(telegram_id):
    botuser = BotUser.select().where(BotUser.telegram_id == telegram_id).first()
    if not botuser:
        return '未绑定,请先绑定'

    if botuser.v2_user.expired_at in [None, 0]:
        return '不限时套餐或未订阅不支持签到'

    # 检查抽奖间隔时间
    if botuser.lucky_time and (datetime.now() - botuser.lucky_time).seconds < 3600:
        return f'请{3600 - (datetime.now() - botuser.lucky_time).seconds}秒后再来抽奖哦!'
    num = random.randint(-10240, 10240)
    flow = num * 1024 * 1024
    botuser.v2_user.transfer_enable += flow
    botuser.lucky_time = datetime.now()

    botuser.v2_user.save()
    botuser.save()
    return f'抽奖成功,{round(num / 1024, 2)}GB流量'


def _traffic(telegram_id):
    v2_user = V2User.select().where(V2User.telegram_id == telegram_id).first()
    if not v2_user:
        return '未绑定,请先绑定'
    if v2_user.expired_at == 0:
        return '未订阅任何套餐，请先订阅'
    num = v2_user.transfer_enable / 1024 ** 3
    text = f'''🚥流量查询
--------
计划流量：{v2_user.plan_id.transfer_enable} GB
已用上行：{round(v2_user.u / 1024 ** 3, 2)} GB
已用下行：{round(v2_user.d / 1024 ** 3, 2)} GB
剩余流量：{round(num, 2)} GB
'''
    return text


def _node(telegram_id):
    v2_user = V2User.select().where(V2User.telegram_id == telegram_id).first()
    if not v2_user:
        return '未绑定,请先绑定'
    return getNodes()


# b9bc3bee61de39f04047dbf8dca12e97
if __name__ == '__main__':
    print(_bind('896776c848efb99a1b8b324225c33277', '1111', sub_domain='172.16.1.14'))
    # print(_bind('3a23da6ebb70a66e2c00b8250df03c62', '1111', sub_domain='172.16.1.14'))
    # print(_bind('bc1d3d0d99bb8348f803665821d145f1', '1111', sub_domain='172.16.1.14'))
