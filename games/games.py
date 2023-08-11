from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from Config import config
from Utils import WAITING_INPUT
from games.utils import get_traffic, edit_traffic
from models import V2User


# 判断是否转发消息
async def is_forward(update: Update, context: ContextTypes.DEFAULT_TYPE, v2_user):
    if update.message.forward_from or update.message.forward_sender_name:
        result = f'由于你想投机取巧，因此没收你的下注流量!\n不和没有诚信的人玩，游戏结束!\n当前账户流量：{await edit_traffic(v2_user, -1)}GB'
        return result
    else:
        return False

# 判断能否流量是否够玩游戏
async def can_games(v2_user):
    traffic = await get_traffic(v2_user)
    if traffic < 1:
        return '你的流量已不足，无法进行游戏'
    else:
        return True


async def tiger(update: Update, context: ContextTypes.DEFAULT_TYPE, v2_user):
    # 开关
    if config.TIGER.switch != True:
        return '当前老虎机游戏关闭，不可进行游戏'

    # 判断能否玩游戏
    can_game = await can_games(v2_user)
    if can_game != True:
        return can_game, ConversationHandler.END

    # 判断是否转发
    forward = await is_forward(update, context, v2_user)
    if forward == False:
        traffic = await edit_traffic(v2_user, -1)
        rate = config.TIGER.rate
        if update.message.dice.value in [1, 22, 43, 64]:
            # 中奖
            result = f'恭喜你中奖了，获得{rate}GB流量已经存入你的账户\n当前账户流量：{await edit_traffic(v2_user, rate)}GB'
        else:
            # 没中奖
            result = f'很遗憾你没有中奖，流量已从你账户扣除1GB\n当前账户流量：{traffic}GB'
        return result, WAITING_INPUT
    else:
        return forward, ConversationHandler.END


async def dice_(update: Update, context: ContextTypes.DEFAULT_TYPE, v2_user):
    # 开关
    if config.DICE.switch != True:
        return '当前骰子游戏关闭，不可进行游戏'

    # 判断能否玩游戏
    can_game = await can_games(v2_user)
    if can_game != True:
        return can_game, ConversationHandler.END

    # 判断是否转发
    forward = await is_forward(update, context, v2_user)
    if forward == False:
        traffic = await edit_traffic(v2_user, -1)
        rate = config.DICE.rate
        user = update.message.dice.value
        bot_message = await update.message.reply_dice(emoji='🎲')
        bot = bot_message.dice.value
        if user > bot:
            # 中奖
            result = f'恭喜你中奖了，获得{rate}GB流量已经存入你的账户\n当前账户流量：{await edit_traffic(v2_user, rate)}GB'
        elif user == bot:
            # 平局
            traffic = await edit_traffic(v2_user, 1)
            result = f'平局，已返还下注流量\n当前账户流量：{traffic}GB'
        else:
            # 没中奖
            result = f'很遗憾你没有中奖，流量已从你账户扣除1GB\n当前账户流量：{traffic}GB'
        return result, WAITING_INPUT
    else:
        return forward, ConversationHandler.END


async def gambling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = f'暂不支持{update.message.dice.emoji}玩法。'
    STATUS = WAITING_INPUT

    # 总开关
    if config.GAME.switch != True:
        await update.message.reply_text(text='当前赌博模式关闭，请联系管理员！')
        return WAITING_INPUT

    v2_user = V2User.select().where(V2User.telegram_id == update.effective_user.id).first()
    # 分流
    if update.message.dice.emoji == '🎰':
        result, STATUS = await tiger(update, context, v2_user)

    if update.message.dice.emoji == '🎲':
        result, STATUS = await dice_(update, context, v2_user)

    await update.message.reply_text(text=result)
    return STATUS
