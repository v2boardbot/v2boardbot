from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from admin import v2board_dict, statDay, statMonth
from keyboard import return_keyboard
from Config import config


async def select_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    STATUS = 'v2board_settings'
    text = '这里啥也没有。'
    query = update.callback_query
    await query.answer()
    callback = update.callback_query.data
    name = callback.replace('v2board_settings', '')
    if name == '⏱添加时长':
        text = '请输入发送需要添加的时长，单位：天'
        STATUS = 'addtime'
    elif name == '🥇昨日排行':
        text = statDay()
    elif name == '🏆本月排行':
        text = statMonth()
    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text, reply_markup=reply_markup
    )
    return STATUS


async def v2board_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    buttons_per_row = 2
    keyboard = [
        [InlineKeyboardButton(j, callback_data=f'v2board_settings{j}') for j in
         list(v2board_dict.keys())[i:i + buttons_per_row]]
        for i in range(0, len(v2board_dict), buttons_per_row)
    ]
    keyboard.append(return_keyboard)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=config.TELEGRAM.title, reply_markup=reply_markup
    )
    return 'v2board_settings'
