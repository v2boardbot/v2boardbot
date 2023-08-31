from init import init
from admin import *
from games import *
from betting import *
import logging
import os
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, Dice, Bot
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler, MessageHandler, filters, TypeHandler, BaseHandler,
)
from MenuHandle import *
from MyCommandHandler import *
from Config import config
from games import gambling
from keyboard import start_keyboard, start_keyboard_admin
from v2board import _bind, _checkin, _traffic, _lucky, _addtime
from models import Db, BotDb, BotUser
from Utils import START_ROUTES, END_ROUTES, get_next_first

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
    await update.message.reply_text(config.TELEGRAM.title, reply_markup=reply_markup, disable_web_page_preview=True)
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
    await query.edit_message_text(config.TELEGRAM.title, reply_markup=reply_markup, disable_web_page_preview=True)
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


async def delete_message(context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.deleteMessage(chat_id=context.job.chat_id, message_id=context.job.user_id, pool_timeout=30)
    except Exception as e:
        # text = f'delete message error report:\nchat_id: {context.job.chat_id}\nmessage_id:{context.job.user_id}\nError: {e}'
        # await context.bot.send_message(chat_id=config.TELEGRAM.admin_telegram_id, text=text)
        pass


class Mybot(Bot):
    async def add_message_dict(self, botmessage, dice=False):
        when = config.TELEGRAM.delete_message
        if type(when) == str:
            return
        if botmessage.reply_to_message:
            chat_id = botmessage.chat.id
            if dice:
                job_queue.run_once(delete_message, when, chat_id=chat_id, user_id=botmessage.id)
            else:
                job_queue.run_once(delete_message, when, chat_id=chat_id, user_id=botmessage.id)
                job_queue.run_once(delete_message, when, chat_id=chat_id,
                                   user_id=botmessage.reply_to_message.message_id)

    async def send_message(self, **kwargs):
        botmessage = await super().send_message(**kwargs)
        await self.add_message_dict(botmessage)
        return botmessage

    async def send_dice(self, **kwargs):
        botmessage = await super().send_dice(**kwargs)
        await self.add_message_dict(botmessage, dice=True)
        return botmessage



if __name__ == '__main__':
    # 面板数据库连接
    Db.connect()
    if os.path.exists('bot.db'):
        res = BotDb.connect()
    else:
        res = BotDb.connect()
        BotDb.create_tables([BotUser])
    bot = Mybot(token=TOKEN)
    application = Application.builder().bot(bot).build()
    job_queue = application.job_queue
    first = get_next_first()
    # job_queue.run_once(open_number, when=when)
    job_queue.run_repeating(open_number, interval=300, first=first)
    CommandList = [
        CommandHandler("start", start),
        CommandHandler("myid", myid),
        CommandHandler("checkin", command_checkin),  # 处理签到命令
        CommandHandler('bind', command_bind),  # 处理绑定命令
        CommandHandler('unbind', command_unbind),  # 处理解绑命令
        CommandHandler('lucky', command_lucky),  # 处理幸运抽奖命令
        CommandHandler('wallet', command_wallet),  # 处理查看钱包命令
        CommandHandler('traffic', command_traffic),  # 处理查看流量命令
        CallbackQueryHandler(betting_slots, pattern="^betting_slots"),
        CallbackQueryHandler(start_over, pattern="^start_over$"),
        MessageHandler(filters.Text(['不玩了', '退出', 'quit']), quit_game),
        MessageHandler(filters.Dice(), gambling),
        MessageHandler(filters.Text(['设置为开奖群']), set_open_group)
    ]
    conv_handler = ConversationHandler(
        entry_points=CommandList,
        states={
            START_ROUTES: [
                CallbackQueryHandler(bot_settings, pattern="^bot_settings"),
                CallbackQueryHandler(setting_reload, pattern="^setting_reload"),
                CallbackQueryHandler(game_settings, pattern="^game_settings"),
                CallbackQueryHandler(start_game, pattern="^start_game"),
                CallbackQueryHandler(select_flow, pattern="^[1-9]|10GB|xGB$"),
                CallbackQueryHandler(v2board_settings, pattern="^v2board_settings"),
                CallbackQueryHandler(menu_wallet, pattern="^wallet"),
                CallbackQueryHandler(menu_checkin, pattern="^checkin$"),
                CallbackQueryHandler(menu_sub, pattern="^sub$"),
                CallbackQueryHandler(menu_mysub, pattern="^mysub"),
                CallbackQueryHandler(menu_traffic, pattern="^traffic$"),
                CallbackQueryHandler(menu_lucky, pattern="^lucky"),
                CallbackQueryHandler(menu_node, pattern="^node"),
                CallbackQueryHandler(end, pattern="^end$"),
            ],
            'addtime': [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input_text)
            ],
            'bot_settings': [
                CallbackQueryHandler(settings, pattern="^settings"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, settings)
            ],
            'game_settings': [
                CallbackQueryHandler(game_switch, pattern="^game_switch"),
                CallbackQueryHandler(select_game, pattern="^select_game"),
                CallbackQueryHandler(game_rate, pattern="^game_rate"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, game_rate)
            ],
            'v2board_settings': [
                CallbackQueryHandler(select_setting, pattern="^v2board_settings"),
            ],
            'input_betting': [
                MessageHandler(filters.TEXT & ~filters.COMMAND, select_flow),
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
