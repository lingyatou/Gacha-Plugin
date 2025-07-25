# 鸣潮模拟抽卡插件 v1.0

这是一个基于[早柚核心（gsuid_core）](https://docs.sayu-bot.com/)为鸣潮游戏设计的模拟抽卡插件，支持角色池和武器池的抽卡功能。
**目前处于开发阶段**

## 功能特性

- 🎯 **角色十连抽卡**：模拟鸣潮角色池抽卡
- ⚔️ **武器十连抽卡**：模拟鸣潮武器池抽卡
- 📊 **抽卡统计**：查看个人抽卡次数和保底信息
- 🎲 **真实概率**：基于真实游戏概率设计
- 🛡️ **保底机制**：支持软保底和硬保底
- ⬆️ **UP池系统**：支持UP角色和武器概率提升
- 🚫 **黑名单**：支持用户和群组黑名单

## 命令列表

| 命令       | 功能           | 权限 |
|------------|----------------|------|
| `gc十连`     | 角色十连抽卡   | 群聊 |
| `gc武器十连` | 武器十连抽卡   | 群聊 |
| `gc抽卡统计` | 查看抽卡统计   | 群聊 |

## 项目结构

```
gsuid_core/plugins/Gacha-Plugin/
├── Gacha-Plugin/
│   ├── config.json         # 插件配置文件
│   ├── gacha_pool.json     # 抽卡池数据
│   ├── gacha.py            # 插件主逻辑
│   ├── gacha_core/         # 抽卡核心逻辑
│   ├── help/               # 预留帮助文档目录
│   ├── __init__.py         # 包初始化
│   └── __pycache__/        # Python 缓存
├── README.md               # 插件说明文档
├── pyproject.toml          # PDM/项目元数据
├── pdm.lock                # PDM锁定文件
└── .gitignore              # Git忽略文件
```

## 配置文件说明

### config.json

```json
{
  "wuwa": {
    "enable": true,
    "up_characters_5": ["卡提希娅"],
    "up_characters_4": ["秋水", "白芷", "釉瑚"],
    "up_weapons_5": ["不屈命定之冠"],
    "up_weapons_4": ["永续坍缩", "呼啸重音", "袍泽之固"],
    "block_users": [123456789],
    "block_groups": [987654321],
    "gacha_rates": {
      "character_5": 0.006,
      "character_4": 0.051,
      "character_3": 0.943,
      "weapon_5": 0.007,
      "weapon_4": 0.06,
      "weapon_3": 0.933,
      "up_character_5_rate": 0.5,
      "up_character_4_rate": 0.5,
      "up_weapon_5_rate": 0.75,
      "up_weapon_4_rate": 0.75,
      "pity_5": 80,
      "pity_4": 10,
      "soft_pity_5": 65,
      "soft_pity_4": 8
    }
  }
}
```
- **enable**: 是否启用鸣潮抽卡功能
- **up_characters_5/4**: 5星/4星UP角色列表
- **up_weapons_5/4**: 5星/4星UP武器列表
- **block_users/block_groups**: 黑名单用户/群组ID
- **gacha_rates**: 各类概率与保底设置

### gacha_pool.json

包含所有可抽取的角色和武器数据，按星级分类。例如：

```json
{
  "character_5": ["安可", "鉴心", ...],
  "character_4": ["灯灯", "釉瑚", ...],
  "weapon_5": ["千古洑流", ...],
  "weapon_4": ["异度", ...],
  "weapon_3": ["钧天正音", ...]
}
```

## 数据存储

用户抽卡数据存储在 `gsuid_core/data/Gacha-Plugin/user.json` 文件中，包含每个用户的抽卡次数和历史统计。首次使用时会自动创建。

## 保底机制

- **5星硬保底**：每80抽必定获得5星物品
- **4星硬保底**：每10抽必定获得4星物品
- **5星软保底**：从第65抽开始，每抽概率逐渐提升
- **4星软保底**：从第8抽开始，每抽概率逐渐提升

## 注意事项

1. 首次使用时会自动创建用户数据文件
2. 配置文件修改后需要重启插件生效
3. 抽卡概率基于真实游戏数据，但仅供参考

## 刨坑
- gc帮助

## 更新日志

### v1.0.0
- **目前为文字抽卡结果**
- 初始版本发布
- 支持角色和武器十连抽卡
- 实现保底机制
- 支持UP池系统
- 添加黑名单功能
- 提供抽卡统计功能 
