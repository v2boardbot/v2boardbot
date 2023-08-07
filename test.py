import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters

from config import HTTP_PROXY, HTTPS_PROXY, TOKEN

if HTTP_PROXY:
    os.environ['HTTP_PROXY'] = HTTP_PROXY
if HTTPS_PROXY:
    os.environ['HTTPS_PROXY'] = HTTPS_PROXY

# 定义状态
WAITING_INPUT = 1

# 处理/start命令
def start(update, context):
    keyboard = [[InlineKeyboardButton("点击这里输入信息", callback_data='input_data')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('请点击按钮输入信息：', reply_markup=reply_markup)

    return WAITING_INPUT

# 处理用户点击按钮的回调
def button_click(update, context):
    query = update.callback_query
    query.answer()  # 确认接收了回调，可以不写

    # 获取用户ID和按钮上输入的信息
    user_id = query.from_user.id
    input_text = query.data

    # 此处可以对输入的信息进行处理
    # ...

    # 回复用户输入的信息
    query.edit_message_text(text=f'您输入的信息是：{input_text}')

    # 进入等待用户输入信息的状态
    return WAITING_INPUT

# 处理用户输入信息
def handle_input_text(update, context):
    user_input = update.message.text

    # 可以在这里对用户输入的信息进行处理
    # ...

    update.message.reply_text(f'您输入的信息是：{user_input}')

    # 结束等待状态
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN,update_queue=False)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING_INPUT: [CallbackQueryHandler(button_click)],
        },
        fallbacks=[MessageHandler(filters.text & ~filters.command, handle_input_text)]
    )

    updater.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
