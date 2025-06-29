#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# 抽卡核心逻辑，不依赖gsuid_core框架


def load_config(config_path: str) -> Dict:
    """读取配置文件"""
    config_file = Path(config_path)
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_gacha_pool(pool_path: str) -> Dict:
    """读取抽卡池数据"""
    pool_file = Path(pool_path)
    if pool_file.exists():
        with open(pool_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"characters": {}, "weapons": {}}


def load_user_data(user_data_path: str) -> Dict:
    """读取用户抽卡数据"""
    user_file = Path(user_data_path)
    if user_file.exists():
        with open(user_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_user_data(user_data: Dict, user_data_path: str):
    """保存用户抽卡数据"""
    user_file = Path(user_data_path)
    user_file.parent.mkdir(parents=True, exist_ok=True)
    with open(user_file, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)


def get_user_gacha_info(user_data: Dict, user_id: str, pool_type: str):
    """获取用户抽卡次数和保底计数（分池）"""
    info = user_data.get(str(user_id), {}).get(pool_type, {})
    return {
        "pull_count": info.get("pull_count", 0),
        "five_pity": info.get("five_pity", 0),
        "four_pity": info.get("four_pity", 0),
        "five_star_history": info.get("five_star_history", []),
    }


def update_user_gacha_info(
    user_data: Dict,
    user_id: str,
    pool_type: str,
    pull_count: int,
    five_pity: int,
    four_pity: int,
    five_star_history=None,
):
    """更新用户抽卡次数和保底计数（分池）"""
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {}
    if pool_type not in user_data[str(user_id)]:
        user_data[str(user_id)][pool_type] = {}
    user_data[str(user_id)][pool_type]["pull_count"] = pull_count
    user_data[str(user_id)][pool_type]["five_pity"] = five_pity
    user_data[str(user_id)][pool_type]["four_pity"] = four_pity
    if five_star_history is not None:
        user_data[str(user_id)][pool_type][
            "five_star_history"
        ] = five_star_history


# 角色池抽卡函数
def gacha_single_character(
    config: Dict, gacha_pool: Dict, user_data: Dict, user_id: str
) -> Tuple[str, int, int, int, int, list, Dict]:
    """角色池单次抽卡"""
    pool_type = "characters"
    info = get_user_gacha_info(user_data, user_id, pool_type)
    pull_count = info["pull_count"]
    five_pity = info["five_pity"]
    four_pity = info["four_pity"]
    five_star_history = info.get("five_star_history", [])

    rates = config.get("wuwa", {}).get("gacha_rates", {})
    pity_5 = rates.get("pity_5", 80)
    pity_4 = rates.get("pity_4", 10)
    soft_pity_5 = rates.get("soft_pity_5", 73)
    soft_pity_4 = rates.get("soft_pity_4", 8)

    if five_pity >= pity_5 - 1:
        rarity = 5
    elif four_pity >= pity_4 - 1:
        rarity = 4
    else:
        base_5_rate = rates.get("character_5", 0.006)
        base_4_rate = rates.get("character_4", 0.051)

        if five_pity >= soft_pity_5:
            base_5_rate = min(
                1.0, base_5_rate + (five_pity - soft_pity_5 + 1) * 0.1
            )
        if four_pity >= soft_pity_4:
            base_4_rate = min(
                1.0, base_4_rate + (four_pity - soft_pity_4 + 1) * 0.1
            )

        rand = random.random()
        if rand < base_5_rate:
            rarity = 5
        elif rand < base_5_rate + base_4_rate:
            rarity = 4
        else:
            rarity = 3

    if rarity == 5:
        pool_key = "character_5"
        up_items = config.get("wuwa", {}).get("up_characters_5", [])
        up_rate = rates.get("up_character_5_rate", 0.5)
    elif rarity == 4:
        # 四星时，角色池和武器池都能抽出角色或武器
        if random.random() < 0.5:  # 50%概率抽角色
            pool_key = "character_4"
            up_items = config.get("wuwa", {}).get("up_characters_4", [])
            up_rate = rates.get("up_character_4_rate", 0.5)
        else:  # 50%概率抽武器
            pool_key = "weapon_4"
            up_items = config.get("wuwa", {}).get("up_weapons_4", [])
            up_rate = rates.get("up_weapon_4_rate", 0.5)
    else:
        pool_key = "weapon_3"
        up_items = []
        up_rate = 0.0

    pool = gacha_pool.get(pool_key, []) if pool_key else []

    if rarity == 5:
        if up_items and random.random() < up_rate:
            item_name = random.choice(up_items)
        else:
            item_name = random.choice(pool) if pool else "未知"
    elif rarity == 4:
        item_name = random.choice(pool) if pool else "未知"
    else:
        item_name = random.choice(pool) if pool else "未知"

    pull_count += 1
    five_pity += 1
    four_pity += 1
    if rarity == 5:
        five_pity = 0
        four_pity = 0
        five_star_history = five_star_history + [
            {"item": item_name, "at_pull": pull_count}
        ]
    elif rarity == 4:
        four_pity = 0

    update_user_gacha_info(
        user_data,
        user_id,
        pool_type,
        pull_count,
        five_pity,
        four_pity,
        five_star_history,
    )

    return (
        item_name,
        rarity,
        pull_count,
        five_pity,
        four_pity,
        five_star_history,
        user_data,
    )


# 武器池抽卡函数
def gacha_single_weapon(
    config: Dict, gacha_pool: Dict, user_data: Dict, user_id: str
) -> Tuple[str, int, int, int, int, list, Dict]:
    """武器池单次抽卡"""
    pool_type = "weapons"
    info = get_user_gacha_info(user_data, user_id, pool_type)
    pull_count = info["pull_count"]
    five_pity = info["five_pity"]
    four_pity = info["four_pity"]
    five_star_history = info.get("five_star_history", [])

    rates = config.get("wuwa", {}).get("gacha_rates", {})
    pity_5 = rates.get("pity_5", 80)
    pity_4 = rates.get("pity_4", 10)
    soft_pity_5 = rates.get("soft_pity_5", 73)
    soft_pity_4 = rates.get("soft_pity_4", 8)

    if five_pity >= pity_5 - 1:
        rarity = 5
    elif four_pity >= pity_4 - 1:
        rarity = 4
    else:
        base_5_rate = rates.get("weapon_5", 0.007)
        base_4_rate = rates.get("weapon_4", 0.06)

        if five_pity >= soft_pity_5:
            base_5_rate = min(
                1.0, base_5_rate + (five_pity - soft_pity_5 + 1) * 0.1
            )
        if four_pity >= soft_pity_4:
            base_4_rate = min(
                1.0, base_4_rate + (four_pity - soft_pity_4 + 1) * 0.1
            )

        rand = random.random()
        if rand < base_5_rate:
            rarity = 5
        elif rand < base_5_rate + base_4_rate:
            rarity = 4
        else:
            rarity = 3

    if rarity == 5:
        pool_key = "weapon_5"
        up_items = config.get("wuwa", {}).get("up_weapons_5", [])
        up_rate = rates.get("up_weapon_5_rate", 0.75)
    elif rarity == 4:
        # 四星时，角色池和武器池都能抽出角色或武器
        if random.random() < 0.5:  # 50%概率抽角色
            pool_key = "character_4"
            up_items = config.get("wuwa", {}).get("up_characters_4", [])
            up_rate = rates.get("up_character_4_rate", 0.5)
        else:  # 50%概率抽武器
            pool_key = "weapon_4"
            up_items = config.get("wuwa", {}).get("up_weapons_4", [])
            up_rate = rates.get("up_weapon_4_rate", 0.5)
    else:
        pool_key = "weapon_3"
        up_items = []
        up_rate = 0.0

    pool = gacha_pool.get(pool_key, []) if pool_key else []

    if rarity == 5:
        if up_items and random.random() < up_rate:
            item_name = random.choice(up_items)
        else:
            item_name = random.choice(pool) if pool else "未知"
    elif rarity == 4:
        item_name = random.choice(pool) if pool else "未知"
    else:
        item_name = random.choice(pool) if pool else "未知"

    pull_count += 1
    five_pity += 1
    four_pity += 1
    if rarity == 5:
        five_pity = 0
        four_pity = 0
        five_star_history = five_star_history + [
            {"item": item_name, "at_pull": pull_count}
        ]
    elif rarity == 4:
        four_pity = 0

    update_user_gacha_info(
        user_data,
        user_id,
        pool_type,
        pull_count,
        five_pity,
        four_pity,
        five_star_history,
    )

    return (
        item_name,
        rarity,
        pull_count,
        five_pity,
        four_pity,
        five_star_history,
        user_data,
    )


# 抽卡函数
def gacha_single(
    config: Dict,
    gacha_pool: Dict,
    user_data: Dict,
    user_id: str,
    is_character: bool = True,
) -> Tuple[str, int, int, int, int, list, Dict]:
    """单次抽卡"""
    if is_character:
        return gacha_single_character(config, gacha_pool, user_data, user_id)
    else:
        return gacha_single_weapon(config, gacha_pool, user_data, user_id)


# 十连抽卡
def gacha_ten(
    config: Dict,
    gacha_pool: Dict,
    user_data: Dict,
    user_id: str,
    is_character: bool = True,
    count: int = 10,
) -> Tuple[list, Dict]:
    """抽卡函数，支持自定义次数"""
    results = []
    for i in range(count):
        (
            item_name,
            rarity,
            pull_count,
            five_pity,
            four_pity,
            five_star_history,
            user_data,
        ) = gacha_single(config, gacha_pool, user_data, user_id, is_character)
        results.append((item_name, rarity))
    return results, user_data


# 格式化抽卡结果
def format_gacha_result(results: List[Tuple[str, int]]) -> str:
    """格式化抽卡结果"""
    if not results:
        return "抽卡失败，请重试"
    names = [item_name for item_name, _ in results]
    return ", ".join(names)
