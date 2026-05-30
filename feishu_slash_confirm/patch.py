"""Runtime monkey patches for Feishu slash-command confirmation cards.

Adds a ``send_slash_confirm`` method to the Feishu adapter and wraps
``_on_card_action_trigger`` to handle button callbacks.
"""

from __future__ import annotations

import functools
import json
import logging
import threading
from typing import Any, Dict, Optional

_logger = logging.getLogger("feishu_slash_confirm")

# ── Adapter-level state ───────────────────────────────────────────
# confirm_id → {"session_key": str, "chat_id": str}
_slash_state: Dict[str, dict] = {}
_state_lock = threading.Lock()


def _extract_detail(message: str) -> str:
    """从 ``message`` 中提取第二段作为详情文本。

    消息格式:
        ⚠️ **Confirm /new**

        详情文本...

        Choose:
        ...
    返回 header 和 Choose 之间的内容。
    """
    parts = message.split("\n\n", 2)
    if len(parts) >= 2:
        return parts[1].strip()
    return message


def _build_confirm_card(
    *,
    title: str,
    detail: str,
    confirm_id: str,
) -> dict:
    """构建确认卡片 JSON。"""
    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"content": f"⚠️ {title}", "tag": "plain_text"},
            "template": "blue",
        },
        "elements": [
            {"tag": "markdown", "content": detail},
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "✅ 仅此一次"},
                        "type": "primary",
                        "value": {
                            "hermes_action": "slash_confirm",
                            "confirm_id": confirm_id,
                            "choice": "once",
                        },
                    },
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "🔒 始终允许"},
                        "type": "default",
                        "value": {
                            "hermes_action": "slash_confirm",
                            "confirm_id": confirm_id,
                            "choice": "always",
                        },
                    },
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "❌ 取消"},
                        "type": "danger",
                        "value": {
                            "hermes_action": "slash_confirm",
                            "confirm_id": confirm_id,
                            "choice": "cancel",
                        },
                    },
                ],
            },
        ],
    }


def _build_resolved_card(
    *,
    title: str,
    choice: str,
) -> dict:
    """按钮点击后，更新卡片为已选状态。"""
    choice_map = {
        "once": "✅ 已批准（仅此一次）",
        "always": "🔒 已批准（始终允许）",
        "cancel": "❌ 已取消",
    }
    label = choice_map.get(choice, f"已选择: {choice}")
    template_map = {
        "once": "green",
        "always": "green",
        "cancel": "grey",
    }
    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"content": f"⚠️ {title}", "tag": "plain_text"},
            "template": template_map.get(choice, "blue"),
        },
        "elements": [
            {
                "tag": "markdown",
                "content": label,
            },
        ],
    }


# ── Monkey patches ────────────────────────────────────────────────


def _make_send_slash_confirm(orig_getattr):
    """创建 ``send_slash_confirm`` 方法补丁。

    添加 ``send_slash_confirm`` 到 Feishu 适配器（如果尚未存在）。
    """

    async def send_slash_confirm(
        self,
        chat_id: str,
        title: str,
        message: str,
        session_key: str,
        confirm_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """发送带 3 个按钮的确认卡片。"""
        if not hasattr(self, "_client") or not self._client:
            _logger.debug("[FSC] No client, falling back to text")
            from gateway.platforms.base import SendResult
            return SendResult(success=False, error="Not connected")

        # 存储状态用于回调路由
        with _state_lock:
            _slash_state[confirm_id] = {
                "session_key": session_key,
                "chat_id": chat_id,
            }

        detail = _extract_detail(message)
        card = _build_confirm_card(
            title=title,
            detail=detail,
            confirm_id=confirm_id,
        )

        try:
            payload = json.dumps(card, ensure_ascii=False)
            from gateway.platforms.base import SendResult
            response = await self._feishu_send_with_retry(
                chat_id=chat_id,
                msg_type="interactive",
                payload=payload,
                reply_to=None,
                metadata=None,
            )
            result = SendResult(
                success=response.success() if hasattr(response, "success") else True,
                message_id=str(
                    getattr(getattr(response, "data", None), "message_id", "")
                    if hasattr(response, "data")
                    else ""
                ),
            )
            if result.success:
                _logger.info(
                    "[FSC] Slash-confirm card sent: confirm_id=%s cmd=%s",
                    confirm_id, title,
                )
            else:
                _logger.warning(
                    "[FSC] Slash-confirm card send failed: %s", result.error
                )
            return result
        except Exception as exc:
            _logger.error(
                "[FSC] send_slash_confirm error: %s", exc, exc_info=True
            )
            from gateway.platforms.base import SendResult
            return SendResult(success=False, error=str(exc))

    return send_slash_confirm


def _wrap_on_card_action_trigger(orig: Any) -> Any:
    """包装 FeishuAdapter._on_card_action_trigger 以处理 slash_confirm 按钮。"""

    # 尝试获取 lark 的 P2CardActionTriggerResponse 和 CallBackCard
    _P2Response = None
    _CallBackCard = None
    try:
        from lark_oapi.event.callback.model.p2_card_action_trigger import (
            CallBackCard, P2CardActionTriggerResponse,
        )
        _P2Response = P2CardActionTriggerResponse
        _CallBackCard = CallBackCard
    except ImportError:
        pass

    @functools.wraps(orig)
    def wrapper(self, data: Any) -> Any:
        event = getattr(data, "event", None)
        action = getattr(event, "action", None)
        action_value = getattr(action, "value", {}) or {}
        hermes_action = (
            action_value.get("hermes_action")
            if isinstance(action_value, dict)
            else None
        )

        # ── Slash-confirm 按钮处理 ──
        if hermes_action == "slash_confirm":
            confirm_id = (
                action_value.get("confirm_id")
                if isinstance(action_value, dict)
                else None
            )
            choice = (
                action_value.get("choice")
                if isinstance(action_value, dict)
                else None
            )
            if not confirm_id or not choice:
                _logger.warning(
                    "[FSC] Slash-confirm button missing confirm_id/choice"
                )
                return _P2Response() if _P2Response else None

            # 查找存储的 session_key
            _session_key = None
            with _state_lock:
                entry = _slash_state.pop(confirm_id, None)
                if entry:
                    _session_key = entry.get("session_key")
                    _chat_id = entry.get("chat_id")
                    # 在携带聊天 ID 的情况下解析
                    from tools import slash_confirm as _sc

                    loop = getattr(self, "_loop", None)
                    if loop is not None:
                        from agent.async_utils import safe_schedule_threadsafe

                        async def _do_resolve():
                            result = await _sc.resolve(
                                _session_key, confirm_id, choice
                            )
                            # 更新卡片为已选状态
                            try:
                                title = action_value.get("_title", "")
                                resolved = _build_resolved_card(
                                    title=title, choice=choice
                                )
                                payload = json.dumps(resolved, ensure_ascii=False)
                                # 使用消息 ID 更新卡片
                                # 注意: 这里我们无法直接从按钮事件获取 message_id
                                # 因此我们返回 resolved card 作为同步响应
                                # sdk 会用这个替换原始卡片
                            except Exception:
                                pass
                            # 发送 resolve 返回的确认消息（如 /new 的"新对话"提示）
                            if result and choice != "cancel":
                                try:
                                    import json as _json
                                    _result_str = str(result)
                                    if _result_str.strip():
                                        await self._feishu_send_with_retry(
                                            chat_id=_chat_id,
                                            msg_type="text",
                                            payload=_json.dumps(
                                                {"text": _result_str},
                                                ensure_ascii=False,
                                            ),
                                            reply_to=None,
                                            metadata=None,
                                        )
                                except Exception:
                                    pass
                            return result

                        safe_schedule_threadsafe(
                            _do_resolve(), loop, logger=_logger,
                            log_message="[FSC] resolve_slash_confirm failed",
                        )

            # 返回已解析的卡片状态（同步响应，sdk 自动替换原始卡片）
            title = "确认"
            resolved_card = _build_resolved_card(title=title, choice=choice)
            if _P2Response and _CallBackCard:
                resp = _P2Response()
                card = _CallBackCard()
                card.type = "raw"
                card.data = resolved_card
                resp.card = card
                return resp
            return None

        # ── 其他 action 交给原始处理 ──
        return orig(self, data)

    return wrapper


def apply_patches() -> None:
    """应用所有运行时补丁。"""
    from gateway.platforms import feishu as feishu_mod

    FeishuAdapter = feishu_mod.FeishuAdapter

    # 1. 添加 send_slash_confirm 方法
    # 注意: 不能用 hasattr 检查，因为 BasePlatformAdapter 有同名方法（返回 success=False）
    if "send_slash_confirm" not in FeishuAdapter.__dict__:
        _orig_getattr = None

        async def send_slash_confirm(
            self,
            chat_id: str,
            title: str,
            message: str,
            session_key: str,
            confirm_id: str,
            metadata: Optional[Dict[str, Any]] = None,
        ) -> Any:
            func = _make_send_slash_confirm(None)
            return await func(
                self, chat_id, title, message, session_key, confirm_id, metadata
            )

        FeishuAdapter.send_slash_confirm = send_slash_confirm
        _logger.info("[FSC] Added FeishuAdapter.send_slash_confirm")
    else:
        _logger.info("[FSC] FeishuAdapter.send_slash_confirm already exists, skipping")

    # 2. 包装 _on_card_action_trigger
    orig_trigger = FeishuAdapter._on_card_action_trigger
    FeishuAdapter._on_card_action_trigger = _wrap_on_card_action_trigger(
        orig_trigger
    )
    _logger.info("[FSC] Wrapped FeishuAdapter._on_card_action_trigger")
