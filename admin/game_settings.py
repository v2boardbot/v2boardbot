from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from admin import game_dict
from keyboard import return_keyboard
from Config import config

edit_game_name = False


async def game_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    game_switch = '🚫赌博模式:关' if config.GAME.switch == True else '🔛赌博模式:开'
    buttons_per_row = 4
    keyboard = [
        [InlineKeyboardButton(j, callback_data=f'select_game{j}') for j in
         list(game_dict.keys())[i:i + buttons_per_row]]
        for i in range(0, len(game_dict), buttons_per_row)
    ]
    keyboard.insert(0, [InlineKeyboardButton(game_switch, callback_data='game_switch')])
    keyboard.append(return_keyboard)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=config.TELEGRAM.title, reply_markup=reply_markup
    )
    return 'game_settings'


async def game_switch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    callback = update.callback_query.data
    if callback == 'game_switch':
        if config.GAME.switch == True:
            config.GAME.switch = False
        else:
            config.GAME.switch = True
        config.save()
        await game_settings(update, context)
    else:
        game_name = callback.replace('game_switch', '')
        game_config = game_dict[game_name]
        if game_config.switch == True:
            game_config.switch = False
        else:
            game_config.switch = True
        config.save()
        await select_game(update, context, game_name)
    return 'game_settings'


async def game_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    global edit_game_name
    if query:
        await query.answer()
        keyboard = [
            return_keyboard,
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        game_name = update.callback_query.data.replace('game_rate', '')
        game_config = game_dict[game_name]

        await query.edit_message_text(
            text=f'请发送{game_name}赔率0\n当前倍率：{game_config.rate}', reply_markup=reply_markup
        )
        edit_game_name = game_name
    else:
        if edit_game_name == False:
            return 'game_settings'
        game_name = edit_game_name
        game_config = game_dict[game_name]
        try:
            rate = float(update.message.text)
            game_config.rate = rate
            config.save()
            text = f'编辑成功，当前{game_name}赔率为{rate}'
            edit_game_name = False
        except:
            text = '输入有误，请重新输入，请输入整数或者小数'
        await update.message.reply_text(text)
    return 'game_settings'


async def select_game(update: Update, context: ContextTypes.DEFAULT_TYPE, game_name=None):
    query = update.callback_query
    await query.answer()
    if not game_name:
        game_name = update.callback_query.data.replace('select_game', '')  # 点击的按钮
    game_config = game_dict[game_name]
    switch = '🚫关闭' if game_config.switch == True else '🔛开启'
    keyboard = [
        [
            InlineKeyboardButton(switch, callback_data=f'game_switch{game_name}'),
            InlineKeyboardButton(f'📈赔率:{game_config.rate}', callback_data=f'game_rate{game_name}'),
        ],
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f'{game_name}配置', reply_markup=reply_markup
    )
    return 'game_settings'

# 已废弃
# async def game_tiger(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()
#
#     switch = '🚫关闭' if config.TIGER.switch == True else '🔛开启'
#     keyboard = [
#         [
#             InlineKeyboardButton(switch, callback_data='tiger_switch'),
#             InlineKeyboardButton(f'📈赔率:{config.TIGER.rate}', callback_data='tiger_rate'),
#         ],
#         return_keyboard,
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await query.edit_message_text(
#         text='老虎机配置', reply_markup=reply_markup
#     )
#     return 'game_settings'
#
#
# async def edit_tiger_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     try:
#         config.TIGER.rate = float(update.message.text)
#         config.save()
#         text = '编辑成功'
#     except:
#         text = '发送信息错误，必须是数字'
#
#     await update.message.reply_text(text=text)
#     return 'game_settings'
#
#
# async def tiger_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()
#     keyboard = [
#         return_keyboard,
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await query.edit_message_text(
#         text=f'请发送赔率，发送10则1赔10\n当前倍率：{config.TIGER.rate}', reply_markup=reply_markup
#     )
#     return 'tiger_rate'
#
#
# async def tiger_switch(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()
#     if config.TIGER.switch == True:
#         config.TIGER.switch = False
#     else:
#         config.TIGER.switch = True
#     config.save()
#     await game_tiger(update, context)
#     return 'game_settings'
