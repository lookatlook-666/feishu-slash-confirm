"""feishu-slash-confirm — 飞书交互式确认卡片插件.

桥接模块：Hermes 插件加载器从插件根目录发现此包，
因此将公有 API 从实际的子包中转发出去。
"""

import importlib
import os
import sys

_repo_root = os.path.dirname(os.path.abspath(__file__))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

_bridge_key = "feishu_slash_confirm"
_saved = sys.modules.pop(_bridge_key, None)

try:
    _pkg = importlib.import_module("feishu_slash_confirm")
    register = _pkg.register
    __version__ = _pkg.__version__
finally:
    if _saved is not None:
        sys.modules[_bridge_key] = _saved
    else:
        sys.modules.pop(_bridge_key, None)

__all__ = ["register", "__version__"]
