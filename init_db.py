from models import BotUser
from models import BotDb
from datetime import datetime

BotDb.connect()
BotDb.create_tables([BotUser])
BotDb.close()
