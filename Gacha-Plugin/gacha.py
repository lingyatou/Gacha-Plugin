import json
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from gsuid_core.bot import Bot
from gsuid_core.data_store import get_res_path
from gsuid_core.models import Event
from gsuid_core.segment import MessageSegment
from gsuid_core.sv import SV
from .get_help import get_help
from gsuid_core.help.utils import register_help
from .gacha_core import gacha_core

wuwa_sv = SV(
    "鸣潮模拟抽卡", pm=6, priority=9, enabled=True, black_list=[], area="GROUP"
)

path = get_res_path("Gacha-Plugin")

USER_DATA_PATH = get_res_path("Gacha-Plugin") / "user.json"


# 读取配置文件
def load_config() -> Dict:
    """读取配置文件"""
    # 通过get_res_path获取Gacha-Plugin路径，然后导航到正确的目录
    base_path = get_res_path("Gacha-Plugin")
    config_path = (
        base_path.parent.parent
        / "gsuid_core"
        / "plugins"
        / "Gacha-Plugin"
        / "Gacha-Plugin"
        / "config.json"
    )
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# 读取抽卡池数据
def load_gacha_pool() -> Dict:
    """读取抽卡池数据"""
    # 通过get_res_path获取Gacha-Plugin路径，然后导航到正确的目录
    base_path = get_res_path("Gacha-Plugin")
    pool_path = (
        base_path.parent.parent
        / "gsuid_core"
        / "plugins"
        / "Gacha-Plugin"
        / "Gacha-Plugin"
        / "gacha_pool.json"
    )
    if pool_path.exists():
        with open(pool_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"characters": {}, "weapons": {}}


# 读取用户数据
def load_user_data() -> Dict:
    """读取用户抽卡数据"""
    if USER_DATA_PATH.exists():
        with open(USER_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# 保存用户数据
def save_user_data(user_data: Dict):
    """保存用户抽卡数据"""
    USER_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(USER_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)


@wuwa_sv.on_fullmatch("十连")
async def ten(Bot: Bot, Event: Event):
    user_id = Event.user_id
    group_id = Event.group_id

    # 读取配置和数据
    config = load_config()
    gacha_pool = load_gacha_pool()
    user_data = load_user_data()

    # 检查是否启用
    if not config.get("wuwa", {}).get("enable", True):
        await Bot.send("鸣潮抽卡功能已禁用")
        return

    # 检查黑名单
    block_users = config.get("wuwa", {}).get("block_users", [])
    block_groups = config.get("wuwa", {}).get("block_groups", [])

    if user_id in block_users:
        await Bot.send("您已被禁止使用抽卡功能")
        return

    if group_id in block_groups:
        await Bot.send("该群组已被禁止使用抽卡功能")
        return

    # 获取用户抽卡次数
    current_count = gacha_core.get_user_gacha_info(
        user_data, user_id, "characters"
    )["pull_count"]

    # 执行十连抽卡
    results, updated_user_data = gacha_core.gacha_ten(
        config, gacha_pool, user_data, user_id, is_character=True
    )

    # 保存更新后的用户数据
    save_user_data(updated_user_data)

    # 格式化结果
    result_text = gacha_core.format_gacha_result(results)
    result_text += f"\n📊 当前抽卡次数: {current_count + 10}"

    await Bot.send(result_text)


@wuwa_sv.on_fullmatch("武器十连")
async def weapon_ten(Bot: Bot, Event: Event):
    user_id = Event.user_id
    group_id = Event.group_id

    # 读取配置和数据
    config = load_config()
    gacha_pool = load_gacha_pool()
    user_data = load_user_data()

    # 检查是否启用
    if not config.get("wuwa", {}).get("enable", True):
        await Bot.send("鸣潮抽卡功能已禁用")
        return

    # 检查黑名单
    block_users = config.get("wuwa", {}).get("block_users", [])
    block_groups = config.get("wuwa", {}).get("block_groups", [])

    if user_id in block_users:
        await Bot.send("您已被禁止使用抽卡功能")
        return

    if group_id in block_groups:
        await Bot.send("该群组已被禁止使用抽卡功能")
        return

    # 获取用户抽卡次数
    current_count = gacha_core.get_user_gacha_info(
        user_data, user_id, "weapons"
    )["pull_count"]

    # 执行武器十连抽卡
    results, updated_user_data = gacha_core.gacha_ten(
        config, gacha_pool, user_data, user_id, is_character=False
    )

    # 保存更新后的用户数据
    save_user_data(updated_user_data)

    # 格式化结果
    result_text = gacha_core.format_gacha_result(results)
    result_text += f"\n📊 当前抽卡次数: {current_count + 10}"

    await Bot.send(result_text)


@wuwa_sv.on_fullmatch("抽卡统计")
async def gacha_stats(Bot: Bot, Event: Event):
    user_id = Event.user_id

    # 读取用户数据
    user_data = load_user_data()

    # 获取角色池和武器池的抽卡次数和保底计数
    info_char = gacha_core.get_user_gacha_info(
        user_data, user_id, "characters"
    )
    info_weap = gacha_core.get_user_gacha_info(user_data, user_id, "weapons")

    stats_text = f"📊 抽卡统计\n\n"
    stats_text += f"【角色池】\n"
    stats_text += f"总抽卡次数: {info_char['pull_count']}\n"
    stats_text += f"距离5星保底: {80 - info_char['five_pity']} 抽\n"
    stats_text += f"距离4星保底: {10 - info_char['four_pity']} 抽\n"
    if info_char.get("five_star_history"):
        stats_text += "五星历史: "
        stats_text += (
            ", ".join(
                [
                    f"{h['item']}({h['at_pull']})"
                    for h in info_char["five_star_history"]
                ]
            )
            + "\n"
        )
    stats_text += "\n"
    stats_text += f"【武器池】\n"
    stats_text += f"总抽卡次数: {info_weap['pull_count']}\n"
    stats_text += f"距离5星保底: {80 - info_weap['five_pity']} 抽\n"
    stats_text += f"距离4星保底: {10 - info_weap['four_pity']} 抽\n"
    if info_weap.get("five_star_history"):
        stats_text += "五星历史: "
        stats_text += (
            ", ".join(
                [
                    f"{h['item']}({h['at_pull']})"
                    for h in info_weap["five_star_history"]
                ]
            )
            + "\n"
        )

    await Bot.send(stats_text)


@wuwa_sv.on_fullmatch("帮助")
async def send_gacha_help(Bot: Bot, Event: Event):
    await Bot.send(await get_help())


# 注册到全局帮助（无图标时可省略icon参数）
register_help("Gacha-Plugin", "帮助")
