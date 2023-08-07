from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)
from keyboard import return_keyboard
from v2board import _bind, _checkin, _traffic, _lucky, _unbind, _wallet
from config import START_ROUTES, END_ROUTES


# 签到
async def command_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = _checkin(update.effective_user.id)
    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=text, reply_markup=reply_markup)
    return START_ROUTES


# 绑定
async def command_bind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # http://172.16.1.14/api/v1/client/subscribe?token=b9bc3bee61de39f04047dbf8dca12e97
    text = '参数错误'
    if update.message.chat.type == 'group':
        text = '绑定用户仅限私聊使用，请私聊机器人'
    else:
        try:
            token = context.args[0].split('token=')[-1]
            text = _bind(token, update.effective_user.id)
        except:
            pass
    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=text, reply_markup=reply_markup)
    return START_ROUTES


# 解绑
async def command_unbind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    text = _unbind(telegram_id)
    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=text, reply_markup=reply_markup)
    return START_ROUTES

# 抽奖
async def command_lucky(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    text = _lucky(telegram_id)
    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=text, reply_markup=reply_markup)
    return START_ROUTES

# 查看钱包
async def command_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    text = _wallet(telegram_id)
    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=text, reply_markup=reply_markup)
    return START_ROUTES

# 流量查询
async def command_traffic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    text = _traffic(telegram_id)
    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=text, reply_markup=reply_markup)
    return START_ROUTES
