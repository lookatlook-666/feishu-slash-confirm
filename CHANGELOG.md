# 更新日志 / Changelog

## v1.0.0 (2026-05-29)

初始版本。从 `hermes-lark-streaming` 独立出来的飞书斜杠命令确认卡片插件。

| # | 类型 | 功能 | 说明 |
|---|------|------|------|
| 1 | Feature | 交互式确认卡片 | 将 `/new`、`/reset`、`/undo`、`/reload-mcp` 的确认提示替换为含三个按钮的 CardKit 交互卡片 |
| 2 | Feature | 三按钮卡片 | 「仅此一次」（✅） « **始终允许**（🔒） « **取消**（❌） |
| 3 | Feature | 按钮回调处理 | 包装 `_on_card_action_trigger` 处理按钮点击，调用 `tools.slash_confirm.resolve()` |
