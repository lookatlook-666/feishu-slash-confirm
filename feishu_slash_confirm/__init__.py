"""feishu-slash-confirm — 插件注册入口。"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

_logger = logging.getLogger("feishu_slash_confirm")

_PLUGIN_NAME = "feishu-slash-confirm"
_PLUGIN_YAML = Path(__file__).resolve().parent.parent / "plugin.yaml"

# ── 读取版本号 ────────────────────────────────────────────────────
__version__ = "0.0.0"
try:
    raw = yaml.safe_load(_PLUGIN_YAML.read_text(encoding="utf-8")) or {}
    __version__ = str(raw.get("version", "0.0.0"))
except Exception:
    pass


def register(ctx) -> None:
    """注册 feishu-slash-confirm 插件。

    运行时给 FeishuAdapter 打 monkey-patch，添加 send_slash_confirm()
    方法，并包装 _on_card_action_trigger() 以处理按钮回调。
    """
    _logger.info("feishu-slash-confirm v%s: applying patches...", __version__)
    try:
        from .patch import apply_patches

        apply_patches()
        _logger.info("feishu-slash-confirm: patches applied")
    except Exception:
        _logger.exception("feishu-slash-confirm: failed to apply patches")


def unregister(ctx) -> None:
    """注销插件。"""
    _logger.info("feishu-slash-confirm: unregistered")
