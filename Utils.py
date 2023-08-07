import requests
from peewee import MySQLDatabase

from models import V2User
from config import URL, EMAIL, PASSWORD, SUFFIX


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
        status = '在线' if item['available_status'] else '离线'
        online = item['online'] if item['online'] else '0'
        online += "人"
        line = '节点名称:' + item['name'] + '\n' + '节点状态:' + status + '\n' + '在线人数:' + online + '\n'
        text += line + '----------------------------' + '\n'
    return text


if __name__ == '__main__':
    print(getNodes())
