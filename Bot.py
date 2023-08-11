from init import init
from admin import *
from admin import game_settings, game_tiger, tiger_switch, tiger_rate, edit_tiger_rate
from admin import bot_settings, set_title, edit_title
from games import *
import logging
import os
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, Dice
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler, MessageHandler, filters,
)
from MenuHandle import *
from MyCommandHandler import *
from Config import config
from games import gambling
from keyboard import start_keyboard, start_keyboard_admin
from v2board import _bind, _checkin, _traffic, _lucky, _addtime
from models import Db, BotDb, BotUser
from Utils import START_ROUTES, END_ROUTES

# 加载不需要热加载的配置项
TOKEN = config.TELEGRAM.token
HTTP_PROXY = config.TELEGRAM.http_proxy
HTTPS_PROXY = config.TELEGRAM.https_proxy

if HTTP_PROXY.find('未配置') == -1:
    os.environ['HTTP_PROXY'] = HTTP_PROXY
if HTTPS_PROXY.find('未配置') == -1:
    os.environ['HTTPS_PROXY'] = HTTPS_PROXY

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_telegram_id = config.TELEGRAM.admin_telegram_id
    if type(admin_telegram_id) == str:
        config.TELEGRAM.admin_telegram_id = update.effective_user.id
        admin_telegram_id = config.TELEGRAM.admin_telegram_id
        config.save()
    if update.effective_user.id == admin_telegram_id and update.effective_message.chat.type == 'private':
        reply_markup = InlineKeyboardMarkup(start_keyboard_admin)
    else:
        reply_markup = InlineKeyboardMarkup(start_keyboard)
    # await context.bot.send_message(chat_id=update.effective_chat.id, text='my Bot', reply_markup=reply_markup)
    await update.message.reply_text(config.TELEGRAM.title, reply_markup=reply_markup)
    return START_ROUTES


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    admin_telegram_id = config.TELEGRAM.admin_telegram_id
    if update.effective_user.id == admin_telegram_id and update.effective_message.chat.type == 'private':
        reply_markup = InlineKeyboardMarkup(start_keyboard_admin)
    else:
        reply_markup = InlineKeyboardMarkup(start_keyboard)
    # await context.bot.send_message(chat_id=update.effective_chat.id, text='my Bot', reply_markup=reply_markup)
    await query.edit_message_text(config.TELEGRAM.title, reply_markup=reply_markup)
    return START_ROUTES


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="欢迎下次光临！")
    return ConversationHandler.END


# 获取电报id
async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_user.id, text=update.effective_chat.id)


async def handle_input_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    try:
        text = _addtime(int(user_input))
    except:
        text = '输入有误，请输入整数'
    await update.message.reply_text(text)
    return ConversationHandler.END


if __name__ == '__main__':
    # 面板数据库连接
    Db.connect()
    if os.path.exists('bot.db'):
        res = BotDb.connect()
    else:
        res = BotDb.connect()
        BotDb.create_tables([BotUser])

    application = Application.builder().token(TOKEN).build()
    CommandList = [
        CommandHandler("start", start),
        CommandHandler("myid", myid),
        CommandHandler("checkin", command_checkin),  # 处理签到命令
        CommandHandler('bind', command_bind),  # 处理绑定命令
        CommandHandler('unbind', command_unbind),  # 处理解绑命令
        CommandHandler('lucky', command_lucky),  # 处理幸运抽奖命令
        CommandHandler('wallet', command_wallet),  # 处理查看钱包命令
        CommandHandler('traffic', command_traffic),  # 处理查看流量命令
        CallbackQueryHandler(start_over, pattern="^start_over$"),
        MessageHandler(filters.Text(['不玩了', '退出', 'quit']), quit_game),
        MessageHandler(filters.Dice(), gambling),
    ]
    conv_handler = ConversationHandler(
        entry_points=CommandList,
        states={
            START_ROUTES: [
                CallbackQueryHandler(menu_addtime, pattern="^addtime"),
                CallbackQueryHandler(bot_settings, pattern="^settings"),
                CallbackQueryHandler(setting_reload, pattern="^setting_reload"),
                CallbackQueryHandler(game_settings, pattern="^game_settings"),
                CallbackQueryHandler(start_game, pattern="^start_game"),
                CallbackQueryHandler(select_flow, pattern="^[1-9]|10GB|xGB$"),
                # CallbackQueryHandler(menu_gambling, pattern="^gambling"),
                CallbackQueryHandler(menu_wallet, pattern="^wallet"),
                CallbackQueryHandler(menu_checkin, pattern="^checkin$"),
                CallbackQueryHandler(menu_sub, pattern="^sub$"),
                CallbackQueryHandler(menu_mysub, pattern="^mysub"),
                CallbackQueryHandler(menu_traffic, pattern="^traffic$"),
                CallbackQueryHandler(menu_lucky, pattern="^lucky"),
                CallbackQueryHandler(menu_node, pattern="^node"),
                CallbackQueryHandler(end, pattern="^end$"),
                # CallbackQueryHandler(three, pattern="^" + str(THREE) + "$"),
                # CallbackQueryHandler(four, pattern="^" + str(FOUR) + "$"),
            ],
            # WAITING_INPUT: [
            #     MessageHandler(filters.Text(['不玩了', '退出', 'quit']), quit_input),
            #     MessageHandler(filters.Dice(), gambling),
            # ],
            'addtime': [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input_text)
            ],
            'settings': [
                CallbackQueryHandler(set_title, pattern="^set_title"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_title)
            ],
            'game_settings': [
                CallbackQueryHandler(game_switch, pattern="^game_switch"),

                CallbackQueryHandler(game_tiger, pattern="^game_tiger"),
                CallbackQueryHandler(tiger_switch, pattern="^tiger_switch"),
                CallbackQueryHandler(tiger_rate, pattern="^tiger_rate"),



            ],
            'tiger_rate': [
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_tiger_rate)
            ],
            'input_betting': [
                MessageHandler(filters.TEXT, select_flow),
            ]
        },
        fallbacks=CommandList,
    )

    application.add_handler(conv_handler)

    # 异步运行
    application.run_polling()

    # 关闭数据库
    Db.close()
    BotDb.close()

    # 命令处理
    # start_handler = CommandHandler('start', start)
    # bind_handler = CommandHandler('bind', bind)  # 处理绑定命令
    # checkin_handler = CommandHandler('checkin', checkin)  # 处理签到命令
    # traffic_handler = CommandHandler('traffic', traffic)  # 处理查看流量命令
    # lucky_handler = CommandHandler('lucky', lucky)  # 处理抽奖命令

    # 消息处理

    # 添加处理插件
    # application.add_handler(start_handler)
    # application.add_handler(bind_handler)  # 添加绑定处理方法
    # application.add_handler(checkin_handler)  # 添加签到处理方法
    # application.add_handler(traffic_handler)  # 添加查看流量处理方法
    # application.add_handler(lucky_handler)  # 添加抽奖处理方法
