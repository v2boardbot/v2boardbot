from init import init
from admin import *
from games import *
from betting import *
import logging
import os
from telegram import ChatMember, ChatMemberUpdated, Bot, ChatPermissions
from telegram.ext import (
    ChatMemberHandler,
    MessageHandler,
    filters
)
from MenuHandle import *
from MyCommandHandler import *
from Config import config
from games import gambling
from keyboard import start_keyboard, start_keyboard_admin
from v2board import _bind, _checkin, _traffic, _lucky, _addtime, is_bind
from models import Db, BotDb, BotUser
from Utils import START_ROUTES, END_ROUTES, get_next_first
from typing import Optional, Tuple

# 加载不需要热加载的配置项
TOKEN = config.TELEGRAM.token
HTTP_PROXY = config.TELEGRAM.http_proxy
HTTPS_PROXY = config.TELEGRAM.https_proxy

if HTTP_PROXY.find('未配置') == -1:
    os.environ['HTTP_PROXY'] = HTTP_PROXY
if HTTPS_PROXY.find('未配置') == -1:
    os.environ['HTTPS_PROXY'] = HTTPS_PROXY

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_telegram_id = config.TELEGRAM.admin_telegram_id
    if type(admin_telegram_id) == str:
        config.TELEGRAM.admin_telegram_id = update.effective_user.id
        admin_telegram_id = config.TELEGRAM.admin_telegram_id
        config.save()
    if update.effective_user.id == admin_telegram_id and update.effective_message.chat.type == 'private':
        reply_markup = InlineKeyboardMarkup(start_keyboard_admin)
    else:
        reply_markup = InlineKeyboardMarkup(start_keyboard)
    # await context.bot.send_message(chat_id=update.effective_chat.id, text='my Bot', reply_markup=reply_markup)
    await update.message.reply_text(config.TELEGRAM.title, reply_markup=reply_markup, disable_web_page_preview=True)
    # await update.message.reply_photo(photo=open('1.jpeg', 'rb'), caption=config.TELEGRAM.title, reply_markup=reply_markup)
    return START_ROUTES


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    admin_telegram_id = config.TELEGRAM.admin_telegram_id
    if update.effective_user.id == admin_telegram_id and update.effective_message.chat.type == 'private':
        reply_markup = InlineKeyboardMarkup(start_keyboard_admin)
    else:
        reply_markup = InlineKeyboardMarkup(start_keyboard)
    # await context.bot.send_message(chat_id=update.effective_chat.id, text='my Bot', reply_markup=reply_markup)
    await query.edit_message_text(config.TELEGRAM.title, reply_markup=reply_markup, disable_web_page_preview=True)
    return START_ROUTES


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="欢迎下次光临！")
    return ConversationHandler.END


# 获取电报id
async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_user.id, text=update.effective_chat.id)


async def handle_input_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    try:
        text = _addtime(int(user_input))
    except:
        text = '输入有误，请输入整数'
    await update.message.reply_text(text)
    return ConversationHandler.END


async def delete_message(context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.deleteMessage(chat_id=context.job.chat_id, message_id=context.job.user_id, pool_timeout=30)
    except Exception as e:
        # text = f'delete message error report:\nchat_id: {context.job.chat_id}\nmessage_id:{context.job.user_id}\nError: {e}'
        # await context.bot.send_message(chat_id=config.TELEGRAM.admin_telegram_id, text=text)
        pass


async def set_commands(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.set_my_commands(commands=[
        ("start", "展开管理面板"),
        ("bind", "绑定账号(仅限私聊)"),
        ("unbind", "解除绑定"),
        ("checkin", "每日签到"),
        ("lucky", "幸运抽奖"),
        ("wallet", "查看钱包"),
        ("traffic", "查看流量"),
    ])


async def keyword_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    content = update.message.text
    if type(config.TELEGRAM.keyword_reply) != dict:
        return
    for key in config.TELEGRAM.keyword_reply:
        if content.find(key) != -1:
            text = config.TELEGRAM.keyword_reply[key]
            await update.message.reply_text(text=text)
            break


def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
    """Takes a ChatMemberUpdated instance and extracts whether the 'old_chat_member' was a member
    of the chat and whether the 'new_chat_member' is a member of the chat. Returns None, if
    the status didn't change.
    """
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member


async def greet_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greets new users in chats and announces when someone leaves"""

    result = extract_status_change(update.chat_member)
    if result is None:
        return

    was_member, is_member = result
    user_id = update.chat_member.from_user.id
    chat_id = update.chat_member.chat.id
    cause_name = update.chat_member.from_user.mention_html()
    member_name = update.chat_member.new_chat_member.user.mention_html()

    if not was_member and is_member:
        context.user_data['user_id'] = user_id
        context.user_data['chat_id'] = chat_id
        if not is_bind(user_id):
            if config.TELEGRAM.new_members == 'prohibition':
                context.user_data['verify_type'] = 'prohibition'
                permissions = ChatPermissions(can_send_messages=False, can_send_media_messages=False,
                                              can_send_other_messages=False)
                await context.bot.restrict_chat_member(chat_id=chat_id, user_id=user_id, permissions=permissions)
                keyboard = [[
                    InlineKeyboardButton("🔗前往绑定", url=f'{context.bot.link}?bind=bind'),
                ]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.effective_chat.send_message(
                    f"{member_name} 绑定账号后解除禁言！",
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup
                )
            elif config.TELEGRAM.new_members == 'out':
                context.user_data['verify_type'] = 'out'
                await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id, until_date=60)
            elif config.TELEGRAM.new_members == 'verify':
                permissions = ChatPermissions(can_send_messages=False, can_send_media_messages=False,
                                              can_send_other_messages=False)
                await context.bot.restrict_chat_member(chat_id=chat_id, user_id=user_id, permissions=permissions)
                verify_dict = {
                    '苹果': '🍎',
                    '香蕉': '🍌',
                    '葡萄': '🍇',
                    '草莓': '🍓',
                    '橙子': '🍊',
                    '樱桃': '🍒',
                    '椰子': '🥥',
                    '菠萝': '🍍',
                    '桃子': '🍑',
                    '芒果': '🥭',
                }
                import random
                verify_value = random.choice(list(verify_dict.keys()))
                buttons_per_row = 4
                keyboard = [
                    [InlineKeyboardButton(j, callback_data=f'verify{j}') for j in
                     list(verify_dict.keys())[i:i + buttons_per_row]]
                    for i in range(0, len(verify_dict), buttons_per_row)
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.effective_chat.send_message(
                    f"{member_name} 欢迎你加入本群！\n请点击下方的 {verify_value} 解除禁言",
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup
                )
                context.user_data['verify_value'] = verify_value


async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data == {}:
        return
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    verify_value = query.data.replace('verify', '')
    if context.user_data['user_id'] == user_id and context.user_data['verify_value'] == verify_value:
        permissions = ChatPermissions(can_send_messages=True, can_send_media_messages=True,
                                      can_send_other_messages=True)
        await context.bot.restrict_chat_member(chat_id=chat_id, user_id=user_id, permissions=permissions)
        message_id = update.effective_message.id
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)


class Mybot(Bot):
    async def add_message_dict(self, botmessage, dice=False):
        when = config.TELEGRAM.delete_message
        if type(when) == str:
            return
        if botmessage.reply_to_message:
            chat_id = botmessage.chat.id
            if dice:
                job_queue.run_once(delete_message, when, chat_id=chat_id, user_id=botmessage.id)
            else:
                job_queue.run_once(delete_message, when, chat_id=chat_id, user_id=botmessage.id)
                job_queue.run_once(delete_message, when, chat_id=chat_id,
                                   user_id=botmessage.reply_to_message.message_id)

    async def send_message(self, **kwargs):
        botmessage = await super().send_message(**kwargs)
        await self.add_message_dict(botmessage)
        return botmessage

    async def send_dice(self, **kwargs):
        botmessage = await super().send_dice(**kwargs)
        await self.add_message_dict(botmessage, dice=True)
        return botmessage


if __name__ == '__main__':
    # 面板数据库连接
    Db.connect()
    if os.path.exists('bot.db'):
        res = BotDb.connect()
    else:
        res = BotDb.connect()
        BotDb.create_tables([BotUser])
    bot = Mybot(token=TOKEN)
    application = Application.builder().bot(bot).build()
    job_queue = application.job_queue
    first = get_next_first()
    job_queue.run_once(set_commands, 1)
    job_queue.run_repeating(open_number, interval=300, first=first)
    CommandList = [
        CommandHandler("start", start),
        CommandHandler("myid", myid),
        CommandHandler("checkin", command_checkin),  # 处理签到命令
        CommandHandler('bind', command_bind),  # 处理绑定命令
        CommandHandler('unbind', command_unbind),  # 处理解绑命令
        CommandHandler('lucky', command_lucky),  # 处理幸运抽奖命令
        CommandHandler('wallet', command_wallet),  # 处理查看钱包命令
        CommandHandler('traffic', command_traffic),  # 处理查看流量命令
        CallbackQueryHandler(betting_slots, pattern="^betting_slots"),
        CallbackQueryHandler(start_over, pattern="^start_over$"),
        CallbackQueryHandler(verify, pattern="^verify"),
        ChatMemberHandler(greet_chat_members, ChatMemberHandler.CHAT_MEMBER),
        MessageHandler(filters.Text(['不玩了', '退出', 'quit']), quit_game),
        MessageHandler(filters.Dice(), gambling),
        MessageHandler(filters.Text(['设置为开奖群']), set_open_group),
        MessageHandler(filters.TEXT & ~filters.COMMAND, keyword_reply),

    ]
    conv_handler = ConversationHandler(
        entry_points=CommandList,
        states={
            START_ROUTES: [
                CallbackQueryHandler(bot_settings, pattern="^bot_settings"),
                CallbackQueryHandler(setting_reload, pattern="^setting_reload"),
                CallbackQueryHandler(game_settings, pattern="^game_settings"),
                CallbackQueryHandler(start_game, pattern="^start_game"),
                CallbackQueryHandler(select_flow, pattern="^[1-9]|10GB|xGB$"),
                CallbackQueryHandler(v2board_settings, pattern="^v2board_settings"),
                CallbackQueryHandler(menu_wallet, pattern="^wallet"),
                CallbackQueryHandler(menu_checkin, pattern="^checkin$"),
                CallbackQueryHandler(menu_sub, pattern="^sub$"),
                CallbackQueryHandler(menu_mysub, pattern="^mysub"),
                CallbackQueryHandler(menu_traffic, pattern="^traffic$"),
                CallbackQueryHandler(menu_lucky, pattern="^lucky"),
                CallbackQueryHandler(menu_node, pattern="^node"),
                CallbackQueryHandler(end, pattern="^end$"),
            ],
            'addtime': [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input_text)
            ],
            'bot_settings': [
                CallbackQueryHandler(settings, pattern="^settings"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, settings)
            ],
            'game_settings': [
                CallbackQueryHandler(game_switch, pattern="^game_switch"),
                CallbackQueryHandler(select_game, pattern="^select_game"),
                CallbackQueryHandler(game_rate, pattern="^game_rate"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, game_rate)
            ],
            'v2board_settings': [
                CallbackQueryHandler(select_setting, pattern="^v2board_settings"),
            ],
            'input_betting': [
                MessageHandler(filters.TEXT & ~filters.COMMAND, select_flow),
            ]
        },
        fallbacks=CommandList,
    )

    application.add_handler(conv_handler)

    # 异步运行
    application.run_polling()

    # 关闭数据库
    Db.close()
    BotDb.close()
