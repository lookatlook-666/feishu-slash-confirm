# hermes-lark-streaming

为 [Hermes Agent](https://github.com/NousResearch/hermes-agent) 提供的飞书流式卡片插件。将 AI 回复以 CardKit v2.0 交互式卡片实时渲染，替代默认的纯文本输出。

与上游 [Aowen-Nowor/hermes-lark-streaming](https://github.com/Aowen-Nowor/hermes-lark-streaming) 为互补关系，本版本额外支持**将 `/` 斜杠命令（如 `/stop`、`/reset`）的响应也以卡片形式展示**。

## 特性

- **流式卡片** — AI 回复实时渲染为交互式卡片
- **斜杠命令卡片化** — `/stop` 等命令的响应以卡片展示（中断状态、自动开启新会话）
- **线性模式** — 单卡动态渲染，元素超限自动拆卡
- **CardKit v2.0** — 优先流式 API，自动降级到 IM PATCH
- **完成统计** — 卡片页脚显示耗时、模型、token 用量等

## 安装

```bash
hermes plugins install https://github.com/lookatlook-666/hermes-lark-streaming
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

```yaml
streaming:
  enabled: true
  linear: true               # 单卡动态渲染（推荐）
  panel_expanded: false
  card_ttl_sec: 600
  inject_time: false
  footer:
    fields:
      - [status, elapsed, model, api_calls]
      - [tokens, context, history_offset, compression_exhausted]
    show_label: true
```

## 关键修复（v0.11.0）

| 问题 | 修复 |
|------|------|
| 卡片元素超限后卡死不更新 | 自动拆卡 |
| 拆卡失败后再超限 = 死局 | 超限拆卡不受 `split_disabled` 限制 |
| 每秒多次读磁盘 | 5 秒 TTL 配置缓存 |
| 并发消息漏判中断 | `_started_msg_ids` 加线程锁 |

[完整更新日志 →](CHANGELOG.md)
