from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from Config import config

async def set_open_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != config.TELEGRAM.admin_telegram_id:
        await update.message.reply_text(text='你是管理员吗?你个憨斑鸠')
        return

    if update.effective_chat.type == 'private':
        await update.message.reply_text(text='这是群组吗?你个憨斑鸠')
        return

    config.TELEGRAM.open_group = update.effective_chat.id
    config.save()
    await update.message.reply_text(text='设置成功')