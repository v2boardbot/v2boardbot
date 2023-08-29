from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton

from models import BotUser, V2User, BotBetting, BotBettingLog
from Utils import get_next_first, START_ROUTES
from betting.utils import *
from Config import config


async def entertained(context: ContextTypes.DEFAULT_TYPE):
    current_time, up_number, betting_number = get_betting_number()
    text = f'{up_number}期已封盘！！！'
    await context.bot.edit_message_text(text=text, chat_id=context.job.chat_id, message_id=context.job.user_id)


async def open_number(context: ContextTypes.DEFAULT_TYPE):
    context.bot_data['text'] = None
    current_time, up_number, betting_number = get_betting_number()
    # 老虎机开奖
    chat_id = config.TELEGRAM.open_group
    if type(chat_id) != int:
        message = await context.bot.send_message(text='你没有设置开奖群，无法开奖\n发送"设置为开奖群"把某个群设置为开奖群即可开奖', chat_id=config.TELEGRAM.admin_telegram_id, pool_timeout=30)
        chat_id = config.TELEGRAM.admin_telegram_id
    message = await context.bot.send_dice(chat_id=chat_id, emoji='🎰', pool_timeout=30)

    if context.bot_data.get('chat_id'):
        try:
            await context.bot.deleteMessage(chat_id=chat_id, message_id=context.bot_data['message_id'], pool_timeout=30)
        except:
            pass
    context.bot_data['chat_id'] = chat_id
    context.bot_data['message_id'] = message.message_id
    log_value = message.dice.value
    log_content = '|'.join(slot_machine_value[log_value])
    text = f'{up_number}期开奖结果: {log_content}\n'


    # 删除上一条消息

    if context.job.chat_id:
        await context.bot.deleteMessage(chat_id=context.job.chat_id, message_id=context.job.user_id, pool_timeout=30)
    BotBettingLog.create(log_type='slots', log_content=log_content, log_number=up_number,
                         log_date=datetime.datetime.now())

    # 骰子开奖

    # 更新下注
    results = (
        BotBetting
            .select()
            .where(BotBetting.betting_number == up_number)
            .where(BotBetting.betting_type == 'slots')
    )
    if len(results) == 0:
        text += f'\n{up_number}期无人下注\n'
    else:
        text += f'\n{up_number}期中奖用户:\n'
    for result in results:
        v2_user = V2User.select().where(V2User.telegram_id == result.telegram_id).first()
        win = False
        if result.betting_content in log_content:
            # 中奖
            win = True
        elif result.betting_content == '💣':
            if log_value in [1, 22, 43, 64]:
                # 炸弹中奖
                win = True
            # 没有中奖
        reward = 0
        if win == True:
            if result.betting_content in ['®️®️®️', '🍇🍇🍇', '🍋🍋🍋', '7️⃣7️⃣7️⃣']:
                reward = result.betting_money * 50
            elif result.betting_content in ['®️®️', '🍇🍇', '🍋🍋', '7️⃣7️⃣']:
                reward = result.betting_money * 10
            elif result.betting_content in ['®️', '🍇', '🍋', '7️⃣']:
                reward = result.betting_money * 2
            elif result.betting_content == '💣':
                reward = result.betting_money * 15
            await edit_traffic(v2_user, reward)
            text += f'@{result.telegram_name} 下注【{result.betting_content}】中奖{reward}GB流量\n'
        result.result = log_content
        result.bonus = reward
        result.save()
    text += f'\n{betting_number}期开始下注：\n'
    keyboard = [
        [
            InlineKeyboardButton("®️®️®️", callback_data=f'betting_slots®️®️®️'),
            InlineKeyboardButton("🍇🍇🍇", callback_data=f'betting_slots🍇🍇🍇'),
            InlineKeyboardButton("🍋🍋🍋", callback_data=f'betting_slots🍋🍋🍋'),
            InlineKeyboardButton("7️⃣7️⃣7️⃣", callback_data=f'betting_slots7️⃣7️⃣7️⃣'),
        ],
        [
            InlineKeyboardButton("®️®️", callback_data=f'betting_slots®️®️'),
            InlineKeyboardButton("🍇🍇", callback_data=f'betting_slots🍇🍇'),
            InlineKeyboardButton("🍋🍋", callback_data=f'betting_slots🍋🍋'),
            InlineKeyboardButton("7️⃣7️⃣", callback_data=f'betting_slots7️⃣7️⃣'),
        ],
        [
            InlineKeyboardButton("®️", callback_data=f'betting_slots®️'),
            InlineKeyboardButton("🍇", callback_data=f'betting_slots🍇'),
            InlineKeyboardButton("🍋", callback_data=f'betting_slots🍋'),
            InlineKeyboardButton("7️⃣", callback_data=f'betting_slots7️⃣'),
        ],
        [
            InlineKeyboardButton("特殊奖:炸弹💣", callback_data=f'betting_slots💣'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot_message = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup
    )
    when = get_next_first()
    context.job_queue.run_once(open_number, when=when, chat_id=chat_id, user_id=bot_message.message_id)
    when = when - datetime.timedelta(minutes=1)
    context.job_queue.run_once(entertained, when=when, chat_id=chat_id, user_id=bot_message.message_id)
    return START_ROUTES
