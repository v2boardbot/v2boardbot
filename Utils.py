import requests
import yaml

from Config import config

START_ROUTES, END_ROUTES = 0, 1

WAITING_INPUT = 2

def _admin_auth():  # 返回网站管理员auth_data
    URL = config.WEBSITE.url
    api = URL + '/api/v1/passport/auth/login'
    data = {
        'email': config.WEBSITE.email,
        'password': config.WEBSITE.password,
    }
    res = requests.post(api, data=data)
    return res.json()['data']['auth_data']

def getNodes():
    URL = config.WEBSITE.url
    SUFFIX = config.WEBSITE.suffix

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
        online = str(item['online']) if item['online'] else '0'
        online += "人"
        line = '节点名称:' + item['name'] + '\n' + '节点状态:' + status + '\n' + '在线人数:' + online + '\n'
        text += line + '----------------------------' + '\n'
    if text == '':
        text = '当前无可用节点'
    return text


# def read_config(item='all', config_path='config.yaml'):
#     with open(config_path, 'r') as fp:
#         config = yaml.safe_load(fp)
#     if item == 'all':
#         return config
#     else:
#         if item.find('.') == -1:
#             return config.get(item, {})
#         else:
#             level1, level2 = item.split('.')
#             return config.get(level1, {}).get(level2, f'没有配置{item}')
#
#