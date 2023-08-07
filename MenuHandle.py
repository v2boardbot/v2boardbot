from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

from keyboard import return_keyboard
from v2board import _bind, _checkin, _traffic, _lucky, _sub, _node, _wallet,_mysub
from config import START_ROUTES, END_ROUTES


# 钱包
async def menu_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = _wallet(update.effective_user.id)
    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text, reply_markup=reply_markup
    )
    return START_ROUTES


# 菜单签到
async def menu_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = _checkin(update.effective_user.id)
    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text, reply_markup=reply_markup
    )
    return START_ROUTES


async def menu_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = _sub(update.effective_user.id)
    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text, reply_markup=reply_markup
    )
    return START_ROUTES

async def menu_mysub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_message.chat.type == 'group':
        text = '查看订阅仅限私聊使用，请私聊机器人'
    else:
        text = _mysub(update.effective_user.id)
    query = update.callback_query
    await query.answer()
    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text, reply_markup=reply_markup
    )
    return START_ROUTES


# 流量查询
async def menu_traffic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = _traffic(update.effective_user.id)
    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text, reply_markup=reply_markup
    )
    return START_ROUTES


# 幸运抽奖
async def menu_lucky(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = _lucky(update.effective_user.id)
    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text, reply_markup=reply_markup
    )
    return START_ROUTES


# 节点状态
async def menu_node(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = _node(update.effective_user.id)
    table = [
        ["名称", "状态", "在线"],
        ["美国ssr", "未运行", "0人"],
        ["美国v2ray", "未运行", "0"],
        ["🌅期许 | 你要开心^_^", "未运行", "0"],
        ["🇭🇰香港 | HyTron 01 1.0x", "未运行", "0"],
        ["🇭🇰香港 | IPV6 02 1.0x", "未运行", "245人"],
        ["🇭🇰香港 | HyTron 01 1.0x", "未运行", "0"],
        ["🇭🇰香港 | IPV6 03 1.0x", "未运行", "0"],
        ["🇭🇰香港 | HyTron 04 1.0x", "未运行", "0"],
    ]

    # keyboard = []
    # for row in table:
    #     buttons_row = [InlineKeyboardButton(cell, callback_data="ignore") for cell in row]
    #     keyboard.append(buttons_row)
    # keyboard.append(return_keyboard)
    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup
    )
    return START_ROUTES
