from telegram import InlineKeyboardButton

start_keyboard = [
    [
        InlineKeyboardButton(text='💰我的钱包', callback_data='wallet'),
        InlineKeyboardButton(text='📃流量查询', callback_data='traffic'),
    ],
    [
        InlineKeyboardButton(text='✨幸运抽奖', callback_data='lucky'),
        InlineKeyboardButton(text='📒我的订阅', callback_data='sub'),
    ],
    [
        InlineKeyboardButton(text='📅签 到', callback_data='checkin'),
        InlineKeyboardButton(text='🌐节点状态', callback_data='node'),
    ],
    [
        InlineKeyboardButton(text='🔗订阅链接', callback_data='mysub'),
        InlineKeyboardButton(text='🎰赌博模式🎲', callback_data='start_game'),
    ],
    [
        InlineKeyboardButton(text='v2boardbot Ver:20230812.1 main',
                             url='https://github.com/v2boardbot/v2boardbot/tree/dev')
    ]
]
keyboard_admin = [
    [
        InlineKeyboardButton(text='⚙Bot设置', callback_data='bot_settings'),
        InlineKeyboardButton(text='🔄重载配置', callback_data='setting_reload')
    ],
    [
        InlineKeyboardButton(text='🎮游戏设置', callback_data='game_settings'),
        InlineKeyboardButton(text='等待添加', callback_data='resetdata')
    ],
    [
        InlineKeyboardButton(text='⏱添加时长', callback_data='addtime'),
        InlineKeyboardButton(text='🔁重置流量', callback_data='resetdata')
    ]
]
start_keyboard_admin = keyboard_admin + start_keyboard
return_keyboard = [InlineKeyboardButton('返回菜单', callback_data='start_over')]
