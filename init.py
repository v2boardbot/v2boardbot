import os
import requests
import yaml
from peewee import *


def print_log(log, type_='tips'):
    if type_ == 'tips':
        print(f'\033[32mTips: {log}\033[0m')
    elif type_ == 'error':
        print(f'\033[31mError: {log}\033[0m')
    else:
        print('Info', log)


def save_config(config, config_path='config.yaml'):
    with open(config_path, "w") as yaml_file:
        yaml.dump(config, yaml_file, default_style=None)


def check_database(config_path):
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf8') as fp:
            config = yaml.safe_load(fp)
    else:
        config = {
            'DATABASE': {}
        }

    if config.get('DATABASE'):
        db = MySQLDatabase(**config.get('DATABASE'))
        try:
            db.connect()
            print_log('Successfully connected to database')
            db.close()
        except:
            print_log('Failed to connect to database', type_='error')
            config['DATABASE'] = {}
            save_config(config, config_path)
            check_database(config_path)
    else:
        config['DATABASE'] = {}
        config['DATABASE']['host'] = input('请输入数据库地址（默认:localhost） [localhost]:') or 'localhost'
        config['DATABASE']['database'] = input('请输入数据库名:')
        config['DATABASE']['user'] = input('请输入数据库用户名:')
        config['DATABASE']['password'] = input('请输入数据库密码:')
        save_config(config, config_path)
        check_database(config_path)


def init_database(config_path):
    from models import V2User, Db, BotDb, BotUser, BotBetting, BotBettingLog
    Db.connect()
    if os.path.exists('bot.db'):
        res = BotDb.connect()
    else:
        res = BotDb.connect()
        BotDb.create_tables([BotUser])
    if not BotDb.table_exists('bot_betting'):
        BotDb.create_tables([BotBetting])

    if not BotDb.table_exists('bot_betting_log'):
        BotDb.create_tables([BotBettingLog])

    for v2_user in V2User.select():
        if v2_user.telegram_id:
            bot_user = BotUser.select().where(BotUser.telegram_id == v2_user.telegram_id).first()
            if not bot_user:  # 数据库绑定了，但是本地bot.db没有数据
                BotUser.create(telegram_id=v2_user.telegram_id, v2_user=v2_user)
                print(v2_user.telegram_id, '本地bot.db没有该绑定信息')
    Db.close()
    BotDb.close()


def check_telegram_connect(config_path):
    with open(config_path, 'r', encoding='utf8') as fp:
        config = yaml.safe_load(fp)
    if config.get('TELEGRAM').get('http_proxy'):
        os.environ['HTTP_PROXY'] = config.get('TELEGRAM').get('http_proxy')
        os.environ['HTTPS_PROXY'] = config.get('TELEGRAM').get('https_proxy')
    if not config.get('TELEGRAM').get('token'):
        config['TELEGRAM']['token'] = input('请输入机器人Token:')
    try:
        res = requests.get(f'https://api.telegram.org/bot{config["TELEGRAM"]["token"]}/getMe')
        if res.json()['ok'] == False:
            print_log('Telegram token setting error', 'error')
            config['TELEGRAM']['token'] = input('请输入机器人Token:')
            save_config(config, config_path)
            check_telegram_connect(config_path)
        else:
            save_config(config, config_path)
            print_log(f'Welcome {res.json()["result"]["first_name"]} uses v2boardbot')
    except Exception as e:
        print_log(f'Telegram API connection failed:{e}', 'error')
        config['TELEGRAM']['http_proxy'] = input('请输入代理地址:')
        config['TELEGRAM']['https_proxy'] = config['TELEGRAM']['http_proxy']
        save_config(config, config_path)
        check_telegram_connect(config_path)


def check_v2board(config_path):
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf8') as fp:
            config = yaml.safe_load(fp)
    else:
        config = {
            'WEBSITE': {}
        }

    if config.get('WEBSITE'):
        api = config.get('WEBSITE').get('url') + '/api/v1/passport/auth/login'
        data = {
            'email': config.get('WEBSITE').get('email'),
            'password': config.get('WEBSITE').get('password')
        }
        res = requests.post(api, data=data)
        try:
            auth_data = res.json()['data']['auth_data']
            print_log(f'Airport administrator successfully logged in, Authorization: {auth_data}')
        except:
            print_log(f'Airport administrator login failed, result: {res.text}', 'error')
            config['WEBSITE'] = {}
            save_config(config, config_path)
            check_v2board(config_path)

    else:
        config['WEBSITE'] = {}
        while True:
            url = input('请输入机场面板管理员地址:')
            try:
                protocol = url.split('//')[0] + '//'
                host = url.split('//')[1].split('/')[0]
                suffix = url.split('//')[1].split('/')[1].replace('#', '').replace('/', '')
                config['WEBSITE']['url'] = protocol + host
                config['WEBSITE']['suffix'] = suffix
                break
            except:
                pass
        config['WEBSITE']['email'] = input('请输入机场管理员邮箱:')
        config['WEBSITE']['password'] = input('请输入机场管理员密码:')
        save_config(config, config_path)
        check_v2board(config_path)


def check_file(config_path):
    if not os.path.exists(config_path):
        with open('config.yaml.example', encoding='utf8') as fp:
            config = yaml.safe_load(fp)
        save_config(config)


def init(config_path='config.yaml'):
    check_file(config_path)
    check_database(config_path)
    check_telegram_connect(config_path)
    init_database(config_path)
    check_v2board(config_path)

    with open(config_path, 'r', encoding='utf8') as fp:
        config = yaml.safe_load(fp)
        return config

init()
