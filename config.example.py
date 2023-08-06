START_ROUTES, END_ROUTES = 0, 1

DATABASE = {'charset': 'utf8', 'sql_mode': 'PIPES_AS_CONCAT', 'use_unicode': True, 'host': 'mysql服务器地址', 'port': 3306,
            'user': 'mysql数据库用户名', 'password': 'mysql数据库密码'}

TOKEN = 'Telegram机器人token令牌'  # 类似：6*85**1*17:A*********************************Y

HTTP_PROXY = 'http://127.0.0.1:1082'  # 如果需要代理，则填写http代理地址，不需要代理填写None
HTTPS_PROXY = 'http://127.0.0.1:1082'  # 同上
