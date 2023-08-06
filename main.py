import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler

from v2board import get_sky

os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:1082'
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:1082'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("百度❤️", callback_data="1", url='https://www.baidu.com'),
            InlineKeyboardButton("谷歌🐶", callback_data="2", url='https://www.google.com'),
        ],
        [InlineKeyboardButton("Option 3", callback_data="3")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='my Bot', reply_markup=reply_markup)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


async def sky(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        cityName = context.args[0]
        text_sky = get_sky(cityName)
    except:
        text_sky = '请提供城市名称'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_sky)


if __name__ == '__main__':
    application = ApplicationBuilder().token('6685381817:AAGFiVJx1cykR9Mw8JXCAIBBfLHMMUni4FE').build()

    # 命令处理
    start_handler = CommandHandler('start', start)
    caps_handler = CommandHandler('caps', caps)
    sky_handler = CommandHandler('sky', sky)

    # 消息处理
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    # 添加处理插件
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(caps_handler)
    application.add_handler(sky_handler)

    # 异步运行
    application.run_polling()
