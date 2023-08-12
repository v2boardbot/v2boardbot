from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from Config import config
from Utils import START_ROUTES
from games.utils import get_traffic, edit_traffic
from keyboard import return_keyboard
from models import V2User, BotUser


# 判断是否转发消息
async def is_forward(update: Update, context: ContextTypes.DEFAULT_TYPE, v2_user, bot_user):
    if update.message.forward_from or update.message.forward_sender_name:
        result = f'由于你想投机取巧，因此没收你的下注流量!\n不和没有诚信的人玩，游戏结束!\n当前账户流量：{await edit_traffic(v2_user, bot_user.betting)}GB'
        return result
    else:
        return False


# 判断能否流量是否够玩游戏
async def can_games(v2_user, bot_user):
    traffic = await get_traffic(v2_user)
    if traffic < bot_user.betting:
        return f'你的流量已不足{bot_user.betting}GB，无法进行游戏'
    else:
        return True


async def tiger(update: Update, context: ContextTypes.DEFAULT_TYPE, v2_user, bot_user):
    # 开关
    if config.TIGER.switch != True:
        return '当前老虎机游戏关闭，不可进行游戏', START_ROUTES

    # 判断能否玩游戏
    can_game = await can_games(v2_user, bot_user)
    if can_game != True:
        return can_game, ConversationHandler.END

    # 判断是否转发
    forward = await is_forward(update, context, v2_user, bot_user)
    if forward == False:
        # 扣下注流量
        traffic = await edit_traffic(v2_user, -bot_user.betting)
        rate = config.TIGER.rate * bot_user.betting
        if update.message.dice.value in [1, 22, 43, 64]:
            # 中奖
            result = f'恭喜你中奖了，获得{rate}GB流量已经存入你的账户\n当前账户流量：{await edit_traffic(v2_user, rate)}GB'
        else:
            # 没中奖
            result = f'很遗憾你没有中奖，流量已从你账户扣除{bot_user.betting}GB\n当前账户流量：{traffic}GB'
        return result, START_ROUTES
    else:
        return forward, ConversationHandler.END


async def dice_(update: Update, context: ContextTypes.DEFAULT_TYPE, v2_user, bot_user):
    # 开关
    if config.DICE.switch != True:
        return '当前骰子游戏关闭，不可进行游戏', START_ROUTES

    # 判断能否玩游戏
    can_game = await can_games(v2_user, bot_user)
    if can_game != True:
        return can_game, ConversationHandler.END

    # 判断是否转发
    forward = await is_forward(update, context, v2_user, bot_user)
    if forward == False:
        # 扣下注流量
        traffic = await edit_traffic(v2_user, -bot_user.betting)
        # 如果中奖获得的流量
        rate = config.DICE.rate * bot_user.betting

        user = update.message.dice.value
        bot_message = await update.message.reply_dice(emoji='🎲')
        bot = bot_message.dice.value
        if user > bot:
            # 中奖
            result = f'恭喜你中奖了，获得{rate}GB流量已经存入你的账户\n当前账户流量：{await edit_traffic(v2_user, rate)}GB'
        elif user == bot:
            # 平局
            traffic = await edit_traffic(v2_user, bot_user.betting)
            result = f'平局，已返还下注流量\n当前账户流量：{traffic}GB'
        else:
            # 没中奖
            result = f'很遗憾你没有中奖，流量已从你账户扣除{bot_user.betting}GB\n当前账户流量：{traffic}GB'
        return result, START_ROUTES
    else:
        return forward, ConversationHandler.END


async def basketball(update: Update, context: ContextTypes.DEFAULT_TYPE, v2_user, bot_user):
    # 开关
    if config.BASKETBALL.switch != True:
        return '当前篮球游戏关闭，不可进行游戏', START_ROUTES

    # 判断能否玩游戏
    can_game = await can_games(v2_user, bot_user)
    if can_game != True:
        return can_game, ConversationHandler.END

    # 判断是否转发
    forward = await is_forward(update, context, v2_user, bot_user)
    if forward == False:
        # 扣下注流量
        traffic = await edit_traffic(v2_user, -bot_user.betting)
        if update.message.dice.value in [4, 5]:
            add_rate = (update.message.dice.value - 4) * 0.5
            rate = (add_rate + config.BASKETBALL.rate) * bot_user.betting
            # 中奖
            result = f'恭喜你中奖了，获得{rate}GB流量已经存入你的账户\n当前账户流量：{await edit_traffic(v2_user, rate)}GB'
        else:
            # 没中奖
            result = f'很遗憾你没有中奖，流量已从你账户扣除{bot_user.betting}GB\n当前账户流量：{traffic}GB'
        return result, START_ROUTES
    else:
        return forward, ConversationHandler.END


async def football(update: Update, context: ContextTypes.DEFAULT_TYPE, v2_user, bot_user):
    # 开关
    if config.FOOTBALL.switch != True:
        return '当前足球游戏关闭，不可进行游戏', START_ROUTES

    # 判断能否玩游戏
    can_game = await can_games(v2_user, bot_user)
    if can_game != True:
        return can_game, ConversationHandler.END

    # 判断是否转发
    forward = await is_forward(update, context, v2_user, bot_user)
    if forward == False:
        # 扣下注流量
        traffic = await edit_traffic(v2_user, -bot_user.betting)
        if update.message.dice.value in [4, 5]:
            add_rate = (update.message.dice.value - 4) * 0.5
            rate = (add_rate + config.FOOTBALL.rate) * bot_user.betting
            # 中奖
            result = f'恭喜你中奖了，获得{rate}GB流量已经存入你的账户\n当前账户流量：{await edit_traffic(v2_user, rate)}GB'
        else:
            # 没中奖
            result = f'很遗憾你没有中奖，流量已从你账户扣除{bot_user.betting}GB\n当前账户流量：{traffic}GB'
        return result, START_ROUTES
    else:
        return forward, ConversationHandler.END


async def bullseye(update: Update, context: ContextTypes.DEFAULT_TYPE, v2_user, bot_user):
    # 开关
    if config.BULLSEYE.switch != True:
        return '当前飞镖游戏关闭，不可进行游戏', START_ROUTES

    # 判断能否玩游戏
    can_game = await can_games(v2_user, bot_user)
    if can_game != True:
        return can_game, ConversationHandler.END

    # 判断是否转发
    forward = await is_forward(update, context, v2_user, bot_user)
    if forward == False:
        # 扣下注流量
        traffic = await edit_traffic(v2_user, -bot_user.betting)
        if update.message.dice.value != 1:
            add_rate = (update.message.dice.value - 2) * 0.1
            rate = (add_rate + config.BULLSEYE.rate) * bot_user.betting
            # 中奖
            result = f'恭喜你中奖了，获得{round(rate, 2)}GB流量已经存入你的账户\n当前账户流量：{await edit_traffic(v2_user, rate)}GB'
        else:
            # 没中奖
            result = f'很遗憾你没有中奖，流量已从你账户扣除{bot_user.betting}GB\n当前账户流量：{traffic}GB'
        return result, START_ROUTES
    else:
        return forward, ConversationHandler.END

async def bowling(update: Update, context: ContextTypes.DEFAULT_TYPE, v2_user, bot_user):
    # 开关
    if config.BOWLING.switch != True:
        return '当前保龄球游戏关闭，不可进行游戏', START_ROUTES

    # 判断能否玩游戏
    can_game = await can_games(v2_user, bot_user)
    if can_game != True:
        return can_game, ConversationHandler.END

    # 判断是否转发
    forward = await is_forward(update, context, v2_user, bot_user)
    if forward == False:
        # 扣下注流量
        traffic = await edit_traffic(v2_user, -bot_user.betting)
        if update.message.dice.value != 1:
            add_rate = (update.message.dice.value - 2) * 0.1
            rate = (add_rate + config.BOWLING.rate) * bot_user.betting
            # 中奖
            result = f'恭喜你中奖了，获得{round(rate, 2)}GB流量已经存入你的账户\n当前账户流量：{await edit_traffic(v2_user, rate)}GB'
        else:
            # 没中奖
            result = f'很遗憾你没有中奖，流量已从你账户扣除{bot_user.betting}GB\n当前账户流量：{traffic}GB'
        return result, START_ROUTES
    else:
        return forward, ConversationHandler.END

# 用户退出游戏
async def quit_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot_user = BotUser.select().where(BotUser.telegram_id == telegram_id).first()
    if not bot_user:
        await update.message.reply_text('未绑定,请先绑定', reply_markup=reply_markup)
        return START_ROUTES
    bot_user.is_game = False
    bot_user.save()
    await update.message.reply_text('已退出赌博模式。', reply_markup=reply_markup)
    return START_ROUTES


# 用户下注并开启游戏
async def select_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    query = update.callback_query
    if query:
        await query.answer()
        betting = update.callback_query.data
    else:
        betting = update.message.text + 'GB'
        query = update

    if betting == 'xGB':
        await query.message.reply_text(text=f'请发送你要下注的流量，单位：GB')
        return 'input_betting'
    bot_user = BotUser.select().where(BotUser.telegram_id == telegram_id).first()
    bot_user.betting = int(betting.replace('GB', ''))
    bot_user.is_game = True
    bot_user.save()
    await query.message.reply_text(text=f'下注成功，你每局游戏将下注{betting}流量')
    return START_ROUTES


# 用户准备开始游戏
async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    query = update.callback_query
    await query.answer()

    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    v2_user = V2User.select().where(V2User.telegram_id == telegram_id).first()
    if not v2_user:
        await query.edit_message_text(
            text=f'未绑定,请先绑定',
            reply_markup=reply_markup
        )
        return START_ROUTES

    keyboard = [[], []]
    for i in range(1, 11):
        if i < 6:
            keyboard[0].append(InlineKeyboardButton(f'{i}GB', callback_data=f'{i}GB'))
        else:
            keyboard[1].append(InlineKeyboardButton(f'{i}GB', callback_data=f'{i}GB'))

    keyboard.append([InlineKeyboardButton(f'自定义下注流量', callback_data=f'xGB')])
    keyboard.append(return_keyboard)
    reply_markup = InlineKeyboardMarkup(keyboard)

    if config.GAME.switch != True:
        await update.message.reply_text(text='当前赌博模式关闭，请联系管理员！')
        return ConversationHandler.END
    await query.edit_message_text(
        text=f'当前赔率:🎰1赔{config.TIGER.rate}   🎲1赔{config.DICE.rate}\n发送"不玩了"退出赌博模式\n请选择下注流量或自定义：',
        reply_markup=reply_markup
    )
    return START_ROUTES


# 用户进行游戏
async def gambling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    keyboard = [
        return_keyboard,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    v2_user = V2User.select().where(V2User.telegram_id == telegram_id).first()
    if not v2_user:
        await update.message.reply_text(
            text=f'未绑定,请先绑定',
            reply_markup=reply_markup
        )
        return START_ROUTES

    if config.GAME.switch != True:
        await update.message.reply_text(text='当前赌博模式关闭，请联系管理员！')
        return ConversationHandler.END

    # 判断该用户有没有开启赌博模式
    bot_user = BotUser.select().where(BotUser.telegram_id == telegram_id).first()
    if bot_user.is_game != True:
        keyboard = [
            [InlineKeyboardButton('开启', callback_data='start_game')],
            return_keyboard,
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text='你没有开启赌博模式，是否开启？', reply_markup=reply_markup)
        return START_ROUTES

    result = f'暂不支持{update.message.dice.emoji}玩法。'
    STATUS = START_ROUTES

    # 开始玩游戏
    v2_user = V2User.select().where(V2User.telegram_id == telegram_id).first()
    # 分流
    if update.message.dice.emoji == '🎰':
        result, STATUS = await tiger(update, context, v2_user, bot_user)

    if update.message.dice.emoji == '🎲':
        result, STATUS = await dice_(update, context, v2_user, bot_user)

    if update.message.dice.emoji == '🏀':
        result, STATUS = await basketball(update, context, v2_user, bot_user)

    if update.message.dice.emoji == '⚽':
        result, STATUS = await football(update, context, v2_user, bot_user)

    if update.message.dice.emoji == '🎯':
        result, STATUS = await bullseye(update, context, v2_user, bot_user)

    if update.message.dice.emoji == '🎳':
        result, STATUS = await bowling(update, context, v2_user, bot_user)

    await update.message.reply_text(text=result)
    return STATUS
