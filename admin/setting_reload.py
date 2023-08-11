import json

from Config import config
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from Utils import START_ROUTES


async def setting_reload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    result = json.dumps(config.reload(), indent=4, ensure_ascii=False)
    await query.message.reply_text(text=f'重载成功，当前配置:\n{result}')
    return START_ROUTES
