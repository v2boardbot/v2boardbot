## 许可证

<p align="center">
<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="知识共享许可协议" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br /><span xmlns:dct="http://purl.org/dc/terms/" property="dct:title">v2boardbot</span> 由 <a xmlns:cc="http://creativecommons.org/ns#" href="https://github.com/v2boardbot/v2boardbot" property="cc:attributionName" rel="cc:attributionURL">v2boardbot</a> 采用 <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">知识共享 署名-非商业性使用-相同方式共享 4.0 国际 许可协议</a>进行许可。<br />基于<a xmlns:dct="http://purl.org/dc/terms/" href="https://github.com/v2boardbot/v2boardbot" rel="dct:source">https://github.com/v2boardbot/v2boardbot</a>上的作品创作。
</p>

## 安装

#### 1.1克隆仓库

```bash
git clone https://github.com/v2boardbot/v2boardbot.git
```

#### 1.2 安装依赖

```bash
pip install -r requirements.txt
```

#### 1.3 说明

这是我该项目使用的依赖，可以主要就是python-telegram-bot和peewee版本对应一下即可

```python
aiomysql==0.2.0
anyio==3.7.1
asgiref==3.7.2
certifi==2023.7.22
charset-normalizer==3.2.0
databases==0.6.2
exceptiongroup==1.1.2
greenlet==2.0.2
h11==0.14.0
httpcore==0.17.3
httpx==0.24.1
idna==3.4
peewee==3.16.2
pydantic==1.10.8
PyMySQL==1.1.0
python-telegram-bot==20.4
requests==2.31.0
sniffio==1.3.0
socksio==1.0.0
SQLAlchemy==1.4.41
sqlparse==0.4.4
typing_extensions==4.7.1
tzdata==2023.3
urllib3==2.0.4
```

## 使用

请自行 [@BotFather](https://t.me/BotFather) 创建机器人，命令菜单如下

```text
start - 展开管理面板(仅限私聊)
bind - 绑定账号(仅限私聊)
checkin - 签到
lucky - 抽奖
wallet - 查看钱包
traffic - 查看流量
```

新建config.py或者将config.example.py重命名为config.py，按照示例填写自己的配置文件

```python
START_ROUTES, END_ROUTES = 0, 1

DATABASE = {'charset': 'utf8', 'sql_mode': 'PIPES_AS_CONCAT', 'use_unicode': True, 'host': 'mysql服务器地址', 'port': 3306,
            'user': 'mysql数据库用户名', 'password': 'mysql数据库密码'}

TOKEN = 'Telegram机器人token令牌'  # 类似：6*85**1*17:A*********************************Y

HTTP_PROXY = 'http://127.0.0.1:1082'  # 如果需要代理，则填写http代理地址，不需要代理填写None
HTTPS_PROXY = 'http://127.0.0.1:1082'  # 同上
```

先运行init_db.py来初始化机器人使用的数据库，本地sqlite数据库，不需要任何配置

```bash
python init_db.py
```

在运行Bot.py即可

```bash
python Bot.py
```

![image-20230806170408976](images/image-20230806170408976.png)


## 运行截图

![image-20230806170548614](images/image-20230806170548614.png)

![image-20230806171037159](images/image-20230806171037159.png)

## TODO

### 菜单

- [ ] 我的钱包
- [x] 流量查询
- [ ] 订阅链接
- [x] 我的订阅
- [x] 签到
- [x] 节点状态


### 命令

- [x] 绑定账号
- [x] 解绑账号
- [x] 签到
- [ ] 抽奖
- [ ] 查看钱包
- [ ] 查看流量

## 计划开发

可以提交issuesg给我们提供建议功能，提交issuesg请把问题和建议讲清楚

如果对该项目感兴趣，可以参与开发，邮箱地址：zhuli8@protonmail.com

## 作者有话说

订阅链接 涉及到面板后台的**站点网址**配置，但是配置没有添加到数据库，而是保存到php文件，不方便读取

节点状态 是半完成状态，可以读取到数据库的节点数据，但是在线状态是存在Redis中，需要读取Redis 数据库的内容；也可以使用访问V2Board接口的方式来获取数据，但是需要登录而且速度可能较慢

命令版本的查看流量和签到其实已经开发完成了，只是懒癌犯了没有提交