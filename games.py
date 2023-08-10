from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from Config import config
from Utils import WAITING_INPUT
from models import V2User


async def slot_machine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    SLOT_MACHINE = config.TIGER.rate
    DICE_RATE = config.DICE.rate
    # 开关
    if update.message.dice.emoji == '🎰' and config.TIGER.switch != True:
        await update.message.reply_text(text='当前老虎机游戏关闭，不可进行游戏')
        return WAITING_INPUT

    if update.message.dice.emoji == '🎲' and config.DICE.switch != True:
        await update.message.reply_text(text='当前骰子游戏关闭，不可进行游戏')
        return WAITING_INPUT

    if not update.message.dice.emoji in ['🎰', '🎲']:
        await update.message.reply_text(text=f'暂不支持{update.message.dice.emoji}玩法')
        return WAITING_INPUT
    v2_user = V2User.select().where(V2User.telegram_id == update.effective_user.id).first()
    if not v2_user:
        await update.message.reply_text(text='未绑定,请先绑定')
        return ConversationHandler.END

    traffic = v2_user.transfer_enable / 1024 ** 3
    if not update.message.dice:
        await update.message.reply_text(text='你发送的不是🎰表情，此局无效')
        return ConversationHandler.END
    if traffic < 1:
        await update.message.reply_text(text='你的流量已不足1GB，无法进行游戏')
        return ConversationHandler.END

    if update.message.forward_from or update.message.forward_sender_name:
        v2_user.transfer_enable -= 1024 ** 3
        v2_user.save()
        await update.message.reply_text(
            text=f'由于你想投机取巧，因此没收你的下注流量!\n不和没有诚信的人玩，游戏结束!\n当前账户流量：{round(v2_user.transfer_enable / 1024 ** 3, 2)}GB')
        return ConversationHandler.END
    elif update.message.dice.emoji == '🎰' and update.message.dice.value in [1, 22, 43, 64]:
        v2_user.transfer_enable += (SLOT_MACHINE - 1) * 1024 ** 3
        v2_user.save()
        await update.message.reply_text(
            text=f'恭喜你中奖了，获得{SLOT_MACHINE}GB流量已经存入你的账户\n当前账户流量：{round(v2_user.transfer_enable / 1024 ** 3, 2)}GB')
    elif update.message.dice.emoji == '🎲':
        user = update.message.dice.value
        bot_message = await update.message.reply_dice(emoji='🎲')
        bot = bot_message.dice.value
        if bot > user:
            v2_user.transfer_enable -= 1024 ** 3
            v2_user.save()
            await update.message.reply_text(
                text=f'很遗憾你没有中奖，流量已从你账户扣除1GB\n当前账户流量：{round(v2_user.transfer_enable / 1024 ** 3, 2)}GB')
        elif bot == user:
            await update.message.reply_text(
                text=f'平局，已返还下注流量\n当前账户流量：{round(v2_user.transfer_enable / 1024 ** 3, 2)}GB')
        else:
            v2_user.transfer_enable += (DICE_RATE - 1) * 1024 ** 3
            v2_user.save()
            await update.message.reply_text(
                text=f'恭喜你中奖了，获得{DICE_RATE}GB流量已经存入你的账户\n当前账户流量：{round(v2_user.transfer_enable / 1024 ** 3, 2)}GB')
    else:
        v2_user.transfer_enable -= 1024 ** 3
        v2_user.save()
        await update.message.reply_text(
            text=f'很遗憾你没有中奖，流量已从你账户扣除1GB\n当前账户流量：{round(v2_user.transfer_enable / 1024 ** 3, 2)}GB')
    return WAITING_INPUT
