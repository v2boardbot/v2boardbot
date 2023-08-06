from telegram import InlineKeyboardButton

start_keyboard = [
    [
        InlineKeyboardButton(text='💰我的钱包', callback_data='wallet'),
        InlineKeyboardButton(text='📃流量查询', callback_data='traffic'),
    ],
    [
        InlineKeyboardButton(text='📖订阅链接(仅限私聊)', callback_data='suburl'),
        InlineKeyboardButton(text='📒我的订阅', callback_data='sub'),
    ],
    [
        InlineKeyboardButton(text='✍️签到', callback_data='checkin'),
        InlineKeyboardButton(text='☋节点状态', callback_data='node'),
    ],
]
return_keyboard = [InlineKeyboardButton('返回菜单', callback_data='start_over')]