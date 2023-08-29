from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from betting.utils import *
from Config import config
from Utils import START_ROUTES
from models import BotUser, V2User, BotBetting, BotBettingLog


async def betting_open_log(page_number=1, page_size=10):
    total_records = BotBettingLog.select().count()
    total_pages = (total_records + page_size - 1) // page_size

    results = (BotBettingLog
               .select()
               .where(BotBettingLog.log_type == 'slots')
               .order_by(-BotBettingLog.log_date)
               .paginate(page_number, page_size)
               )

    text = ''
    for result in results:
        text += f'{result.log_number}期: {result.log_content}\n'
    text += f'========================\n'
    text += f'共{total_pages}页，当前第{page_number}页'
    up_page = page_number if page_number - 1 < 1 else page_number - 1
    next_page = total_pages if page_number + 1 > total_pages else page_number + 1
    return up_page, next_page, text


async def betting_slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id  # 下注用户
    telegram_name = update.effective_user.username
    chat_id = update.effective_chat.id
    v2_user = V2User.select().where(V2User.telegram_id == telegram_id).first()
    query = update.callback_query
    await query.answer()
    if not v2_user:
        await context.bot.send_message(chat_id=chat_id, text=f'@{telegram_name} 未绑定,请先绑定')
        return START_ROUTES
    current_time, up_number, betting_number = get_betting_number()
    if query.data == 'betting_slots':
        up_page, next_page, text = await betting_open_log()
        keyboard = [[
            InlineKeyboardButton(text='◀️上一页', callback_data=f'betting_slotspage{up_page}'),
            InlineKeyboardButton(text='▶️下一页', callback_data=f'betting_slotspage{next_page}'),
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    elif query.data.find('page') != -1:
        page_number = int(query.data.replace('betting_slotspage', ''))
        up_page, next_page, text = await betting_open_log(page_number)
        keyboard = [[
            InlineKeyboardButton(text='◀️上一页', callback_data=f'betting_slotspage{up_page}'),
            InlineKeyboardButton(text='▶️下一页', callback_data=f'betting_slotspage{next_page}'),
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        betting_content = query.data.replace('betting_slots', '')  # 下注内容
        bot_user = BotUser.select().where(BotUser.telegram_id == telegram_id).first()
        betting_money = bot_user.betting  # 下注流量
        # 判断用户流量
        can_game = await can_games(v2_user, bot_user)
        if can_game != True:
            await query.message.reply_text(text=can_game)
            return START_ROUTES

        await edit_traffic(v2_user, -betting_money)
        BotBetting.create(telegram_id=telegram_id, telegram_name=telegram_name, chat_id=chat_id, betting_type='slots',
                          betting_content=betting_content, betting_money=betting_money, betting_number=betting_number,
                          betting_date=datetime.datetime.now())

        text = f'下注期号:{betting_number}\n'
        text += f'下注内容:{betting_content}\n'
        text += f'下注流量:{betting_money}GB\n'
        # await query.message.reply_text(text=text)
        await context.bot.send_message(chat_id=telegram_id, text=text)
    return START_ROUTES
