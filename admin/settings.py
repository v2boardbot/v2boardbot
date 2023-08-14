from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from admin import settings_dict
from keyboard import return_keyboard
from Config import config

edit_setting_name = False

async def bot_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    buttons_per_row = 2
    keyboard = [
        [InlineKeyboardButton(j, callback_data=f'settings{j}') for j in
         list(settings_dict.keys())[i:i + buttons_per_row]]
        for i in range(0, len(settings_dict), buttons_per_row)
    ]
    keyboard.append(return_keyboard)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=config.TELEGRAM.title, reply_markup=reply_markup
    )
    return 'bot_settings'


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global edit_setting_name
    query = update.callback_query
    if query:
        await query.answer()
        set_name = update.callback_query.data.replace('settings', '')
        text = f'请发送你的{set_name}'
        if set_name in ['📅签到设置', '✨抽奖设置']:
            text = f'请发送你的{set_name}信息\n格式:最小值|最大值\n单位:MB\n例:-1024|1024;随机扣1024到加1024MB\nPS:发送关闭可关闭本功能'
        keyboard = [
            return_keyboard,
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=text, reply_markup=reply_markup
        )
        edit_setting_name = set_name
    else:
        set_name = edit_setting_name
        if edit_setting_name == False:
            return 'bot_settings'
        try:
            input_ = update.message.text
            if set_name == '🗑️删除时间':
                input_ = int(input_)
            setattr(config.TELEGRAM, settings_dict[set_name], input_)
            config.save()
            text = f'编辑成功，当前{set_name}为:\n{input_}'
            edit_setting_name = False
        except:
            text = '输入有误，请重新输入整数或小数'
        await update.message.reply_text(text)


    return 'bot_settings'
