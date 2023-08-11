from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

from Config import config
from keyboard import return_keyboard
from models import V2User
from v2board import _bind, _checkin, _traffic, _lucky, _sub, _node, _wallet, _mysub
from Utils import START_ROUTES, END_ROUTES, WAITING_INPUT


# 添加时长 - 管理员命令
async def menu_addtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text='请输入发送需要添加的时长，单位：天', reply_markup=reply_markup
    )
    return 'addtime'


# 赌博模式
async def menu_gambling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    v2_user = V2User.select().where(V2User.telegram_id == update.effective_user.id).first()
    if not v2_user:
        await query.edit_message_text(
            text=f'未绑定,请先绑定',
            reply_markup=reply_markup
        )
        return START_ROUTES
    await query.edit_message_text(
        text=f'请发送🎰或🎲表情，可以连续发送\n当前赔率:🎰1赔{config.TIGER.rate} 🎲1赔{config.DICE.rate}\n发送"不玩了"退出赌博模式',
        reply_markup=reply_markup
    )
    return WAITING_INPUT


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
    if update.effective_message.chat.type != 'private':
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
    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup
    )
    return START_ROUTES
