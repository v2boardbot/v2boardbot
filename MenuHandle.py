from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

from keyboard import return_keyboard
from v2board import _bind, _checkin, _traffic, _lucky, _sub, _node
from config import START_ROUTES, END_ROUTES

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

# 节点状态
async def menu_node(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = _node(update.effective_user.id)
    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text, reply_markup=reply_markup
    )
    return START_ROUTES