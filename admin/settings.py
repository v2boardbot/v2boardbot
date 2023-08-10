from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from keyboard import return_keyboard
from Config import config


async def bot_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton('🏷️标题设置', callback_data='set_title'),
        ],
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=config.TELEGRAM.title, reply_markup=reply_markup
    )
    return 'settings'


async def set_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text='请发送你的标题', reply_markup=reply_markup
    )
    return 'settings'


async def edit_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config.TELEGRAM.title = update.message.text
    await update.message.reply_text(text='编辑成功，新标题:\n' + config.TELEGRAM.title)
    config.save()
    return ConversationHandler.END
