import datetime


async def from_bytes(bytes_value, unit='gb'):
    bytes_value = float(bytes_value)
    unit = unit.lower()
    if unit == 'kb':
        size = bytes_value / 1024
    elif unit == 'mb':
        size = bytes_value / (1024 * 1024)
    elif unit == 'gb':
        size = bytes_value / (1024 * 1024 * 1024)
    else:
        size = bytes_value

    return size


async def to_bytes(size, unit='gb'):
    size = float(size)
    unit = unit.lower()

    if unit == 'kb':
        size *= 1024
    elif unit == 'mb':
        size *= 1024 * 1024
    elif unit == 'gb':
        size *= 1024 * 1024 * 1024

    return int(size)


# 获取当前剩余流量
async def get_traffic(v2_user):
    traffic = await from_bytes(v2_user.transfer_enable)  # 总量
    upload = await from_bytes(v2_user.u)  # 已用上行
    download = await from_bytes(v2_user.d)  # 已用下行
    residual = traffic - upload - download  # 剩余流量
    return round(residual, 2)


# 编辑流量
async def edit_traffic(v2_user, size, unit='GB'):
    size = await to_bytes(size, unit)
    v2_user.d += size
    v2_user.save()
    return await get_traffic(v2_user)


# 判断能否流量是否够玩游戏
async def can_games(v2_user, bot_user):
    traffic = await get_traffic(v2_user)
    if traffic < bot_user.betting:
        return f'你的流量已不足{bot_user.betting}GB，无法进行游戏'
    else:
        return True


def get_betting_number(hour=None, minute=None, second=None, microsecond=None):
    start_time = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    current_time = datetime.datetime.now()
    if hour != None:
        current_time = current_time.replace(hour=hour)
    if minute != None:
        current_time = current_time.replace(minute=minute)
    if second != None:
        current_time = current_time.replace(second=second)
    if microsecond != None:
        current_time = current_time.replace(microsecond=microsecond)
    minutes_passed = (current_time - start_time).total_seconds() / 60
    minutes_per_draw = 5
    betting_date = start_time.strftime('%Y%m%d')
    if current_time.minute % 5 == 4:
        betting_number = int(minutes_passed / minutes_per_draw) + 2
    else:
        betting_number = int(minutes_passed / minutes_per_draw) + 1
    if betting_number < 100:
        betting_number = str(betting_number).zfill(3)
    next_num = int(f'{betting_date}{betting_number}')
    if betting_number == '001':
        last_day = start_time - datetime.timedelta(days=1)
        betting_date = last_day.strftime('%Y%m%d')
        up_num = int(f'{betting_date}288')
    else:
        up_num = next_num - 1
    if betting_number == 289:
        next_day = start_time + datetime.timedelta(days=1)
        betting_date = next_day.strftime('%Y%m%d')
        next_num = int(f'{betting_date}001')

    return current_time, up_num, next_num


slot_machine_value = {
    1: ("®️", "®️", "®️"),
    2: ("🍇", "®️", "®️"),
    3: ("🍋", "®️", "®️"),
    4: ("7️⃣", "®️", "®️"),
    5: ("®️", "🍇", "®️"),
    6: ("🍇", "🍇", "®️"),
    7: ("🍋", "🍇", "®️"),
    8: ("7️⃣", "🍇", "®️"),
    9: ("®️", "🍋", "®️"),
    10: ("🍇", "🍋", "®️"),
    11: ("🍋", "🍋", "®️"),
    12: ("7️⃣", "🍋", "®️"),
    13: ("®️", "7️⃣", "®️"),
    14: ("🍇", "7️⃣", "®️"),
    15: ("🍋", "7️⃣", "®️"),
    16: ("7️⃣", "7️⃣", "®️"),
    17: ("®️", "®️", "🍇"),
    18: ("🍇", "®️", "🍇"),
    19: ("🍋", "®️", "🍇"),
    20: ("7️⃣", "®️", "🍇"),
    21: ("®️", "🍇", "🍇"),
    22: ("🍇", "🍇", "🍇"),
    23: ("🍋", "🍇", "🍇"),
    24: ("7️⃣", "🍇", "🍇"),
    25: ("®️", "🍋", "🍇"),
    26: ("🍇", "🍋", "🍇"),
    27: ("🍋", "🍋", "🍇"),
    28: ("7️⃣", "🍋", "🍇"),
    29: ("®️", "7️⃣", "🍇"),
    30: ("🍇", "7️⃣", "🍇"),
    31: ("🍋", "7️⃣", "🍇"),
    32: ("7️⃣", "7️⃣", "🍇"),
    33: ("®️", "®️", "🍋"),
    34: ("🍇", "®️", "🍋"),
    35: ("🍋", "®️", "🍋"),
    36: ("7️⃣", "®️", "🍋"),
    37: ("®️", "🍇", "🍋"),
    38: ("🍇", "🍇", "🍋"),
    39: ("🍋", "🍇", "🍋"),
    40: ("7️⃣", "🍇", "🍋"),
    41: ("®️", "🍋", "🍋"),
    42: ("🍇", "🍋", "🍋"),
    43: ("🍋", "🍋", "🍋"),
    44: ("7️⃣", "🍋", "🍋"),
    45: ("®️", "7️⃣", "🍋"),
    46: ("🍇", "7️⃣", "🍋"),
    47: ("🍋", "7️⃣", "🍋"),
    48: ("7️⃣", "7️⃣", "🍋"),
    49: ("®️", "®️", "7️⃣"),
    50: ("🍇", "®️", "7️⃣"),
    51: ("🍋", "®️", "7️⃣"),
    52: ("7️⃣", "®️", "7️⃣"),
    53: ("®️", "🍇", "7️⃣"),
    54: ("🍇", "🍇", "7️⃣"),
    55: ("🍋", "🍇", "7️⃣"),
    56: ("7️⃣", "🍇", "7️⃣"),
    57: ("®️", "🍋", "7️⃣"),
    58: ("🍇", "🍋", "7️⃣"),
    59: ("🍋", "🍋", "7️⃣"),
    60: ("7️⃣", "🍋", "7️⃣"),
    61: ("®️", "7️⃣", "7️⃣"),
    62: ("🍇", "7️⃣", "7️⃣"),
    63: ("🍋", "7️⃣", "7️⃣"),
    64: ("7️⃣", "7️⃣", "7️⃣"),
}

if __name__ == '__main__':
    print(get_betting_number(hour=23, minute=55, second=0, microsecond=0))
    print(get_betting_number(hour=23, minute=56, second=0, microsecond=0))
    print(get_betting_number(hour=23, minute=57, second=0, microsecond=0))
    print(get_betting_number(hour=23, minute=58, second=0, microsecond=0))
    print(get_betting_number(hour=23, minute=59, second=0, microsecond=0))
    print(get_betting_number(hour=0, minute=0, second=0, microsecond=0))