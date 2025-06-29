from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV, Plugins

Plugins(name="Gacha-Plugin", force_prefix=["gc"], allow_empty_prefix=False)

# 导入抽卡功能
from . import gacha
