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
    v2_user.transfer_enable += size
    v2_user.save()
    return await get_traffic(v2_user)
