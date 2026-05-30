# feishu-slash-confirm

Hermes Agent 飞书斜杠命令交互式确认卡片插件（`/new`、`/reset`、`/undo`、`/reload-mcp`）。

传统确认是纯文本提示，本插件将其替换为含三个按钮的交互卡片：

- ✅ **仅此一次** — 临时允许
- 🔒 **始终允许** — 记住偏好，以后再执行相同命令不再确认
- ❌ **取消** — 取消命令

## 安装

```bash
hermes plugins install https://github.com/lookatlook-666/feishu-slash-confirm
hermes gateway restart
```

### 卸载

```bash
hermes plugins uninstall feishu-slash-confirm
hermes gateway restart
```

## 原理

插件通过 monkey-patch 飞书适配器：

1. 添加 `send_slash_confirm` 方法 — 发送含三个按钮的 CardKit 交互卡片
2. 包装 `_on_card_action_trigger` — 处理按钮点击，通过 `tools.slash_confirm.resolve()` 解析斜杠命令

## 支持的命令

- `/new` — 新对话
- `/reset` — 重置会话
- `/undo` — 撤回上条消息
- `/reload-mcp` — 重载 MCP 工具

## 许可证

MIT
