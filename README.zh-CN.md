# hermes-lark-streaming

为 [Hermes Agent](https://github.com/NousResearch/hermes-agent) 提供的飞书流式卡片插件。将 AI 回复以 CardKit v2.0 交互式卡片实时渲染，替代默认的纯文本输出。

> **注意：此版本与上游 [Aowen-Nowor/hermes-lark-streaming](https://github.com/Aowen-Nowor/hermes-lark-streaming) 不兼容。** 两者从同一早期代码分叉后独立演进，实现方式不同，无法互相合并。

## 安装

```bash
hermes plugins install https://github.com/lookatlook-666/hermes-lark-streaming
```

提示启用后重启网关：

```bash
hermes gateway restart
```

### 卸载

```bash
HERMES_PYTHON=~/.hermes/hermes-agent/venv/bin/python3
$HERMES_PYTHON -m hermes_lark_streaming cleanup
hermes plugins uninstall hermes-lark-streaming
hermes gateway restart
```

## 配置

安装后自动在 `~/.hermes/config.yaml` 注入默认配置：

```yaml
streaming:
  enabled: true
  linear: true               # 单卡动态渲染（推荐）
  panel_expanded: false
  card_ttl_sec: 600
  inject_time: false         # 用户消息前注入 <time>HH:MM:SS</time>
  footer:
    fields:
      - [status, elapsed, model, api_calls]
      - [tokens, context, history_offset, compression_exhausted]
    show_label: true
```

## 关键修复（v0.11.0）

| 问题 | 修复 |
|------|------|
| 卡片元素超限后卡死不更新 | 自动拆卡，设置 `element_limit_hit` 标志后开新卡继续 |
| 拆卡失败后再超限 = 死局 | 超限拆卡不受 `split_disabled` 限制 |
| 配置读取每次访问都读磁盘 | 5 秒 TTL 缓存，高频场景不再反复 IO |
| 并发消息漏判中断 | `_started_msg_ids` 加 `threading.Lock` |

[完整更新日志 →](CHANGELOG.md)

## 已知限制

- 飞书平台下部分 Hermes 工具（terminal、file、code_execution）不可用，工具调用面板仅展示 Hermes 侧透传的状态
- 与上游版本不兼容，不能同时安装
