from peewee import *
from playhouse.pool import PooledMySQLDatabase, PooledSqliteDatabase

from config2 import DATABASE
Db = PooledMySQLDatabase(**DATABASE)

BotDb = PooledSqliteDatabase('bot.db', max_connections=8, stale_timeout=300)


class BaseModel(Model):
    class Meta:
        database = Db

# 定义 Vmess节点 模型
class V2ServerVmess(BaseModel):
    created_at = IntegerField()
    dns_settings = TextField(column_name='dnsSettings', null=True)
    group_id = CharField()
    host = CharField()
    name = CharField()
    network = CharField()
    network_settings = TextField(column_name='networkSettings', null=True)
    parent_id = IntegerField(null=True)
    port = CharField()
    rate = CharField()
    route_id = CharField(null=True)
    rule_settings = TextField(column_name='ruleSettings', null=True)
    rules = TextField(null=True)
    server_port = IntegerField()
    show = IntegerField(constraints=[SQL("DEFAULT 0")])
    sort = IntegerField(null=True)
    tags = CharField(null=True)
    tls = IntegerField(constraints=[SQL("DEFAULT 0")])
    tls_settings = TextField(column_name='tlsSettings', null=True)
    updated_at = IntegerField()

    class Meta:
        table_name = 'v2_server_vmess'


# 定义 订阅 模型
class V2Plan(BaseModel):
    capacity_limit = IntegerField(null=True)
    content = TextField(null=True)
    created_at = IntegerField()
    group_id = IntegerField()
    half_year_price = IntegerField(null=True)
    month_price = IntegerField(null=True)
    name = CharField()
    onetime_price = IntegerField(null=True)
    quarter_price = IntegerField(null=True)
    renew = IntegerField(constraints=[SQL("DEFAULT 1")])
    reset_price = IntegerField(null=True)
    reset_traffic_method = IntegerField(null=True)
    show = IntegerField(constraints=[SQL("DEFAULT 0")])
    sort = IntegerField(null=True)
    three_year_price = IntegerField(null=True)
    transfer_enable = IntegerField()
    two_year_price = IntegerField(null=True)
    updated_at = IntegerField()
    year_price = IntegerField(null=True)

    class Meta:
        table_name = 'v2_plan'


# 定义 用户 模型
class V2User(BaseModel):
    id = AutoField(primary_key=True)
    invite_user_id = IntegerField(null=True)
    telegram_id = BigIntegerField(null=True)
    email = CharField(max_length=64, unique=True)
    password = CharField(max_length=64)
    password_algo = CharField(max_length=10, null=True)
    password_salt = CharField(max_length=10, null=True)
    balance = IntegerField(default=0)
    discount = IntegerField(null=True)
    commission_type = SmallIntegerField(default=0, choices=[(0, 'system'), (1, 'period'), (2, 'onetime')])
    commission_rate = IntegerField(null=True)
    commission_balance = IntegerField(default=0)
    t = IntegerField(default=0)
    u = BigIntegerField(default=0)
    d = BigIntegerField(default=0)
    transfer_enable = BigIntegerField(default=0)
    banned = BooleanField(default=False)
    is_admin = BooleanField(default=False)
    is_staff = BooleanField(default=False)
    last_login_at = IntegerField(null=True)
    last_login_ip = IntegerField(null=True)
    uuid = CharField(max_length=36)
    group_id = IntegerField(null=True)
    plan_id = ForeignKeyField(V2Plan, backref='v2plan')
    remind_expire = BooleanField(default=True)
    remind_traffic = BooleanField(default=True)
    token = CharField(max_length=32)
    remarks = TextField(null=True)
    expired_at = BigIntegerField(default=0)
    created_at = IntegerField()
    updated_at = IntegerField()

    class Meta:
        table_name = 'v2_user'


# 定义机器人用户模型
class BotUser(Model):
    id = AutoField(primary_key=True)
    telegram_id = BigIntegerField(null=True)
    v2_user = ForeignKeyField(V2User, backref='v2user')
    sign_time = DateTimeField(null=True)
    lucky_time = DateTimeField(null=True)

    class Meta:
        database = BotDb
