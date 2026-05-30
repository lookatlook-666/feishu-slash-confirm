# hermes-lark-streaming

Feishu CardKit v2.0 streaming cards plugin for [Hermes Agent](https://github.com/NousResearch/hermes-agent). Replaces plain-text AI replies with real-time interactive cards.

Complementary to the upstream [Aowen-Nowor/hermes-lark-streaming](https://github.com/Aowen-Nowor/hermes-lark-streaming), this version additionally displays **`/` slash command responses** (e.g. `/stop`, `/reset`) as cards.

## Features

- **Streaming cards** — Real-time AI response in interactive cards
- **Slash command cards** — `/stop` and other commands display interrupt status as cards, auto-start new sessions
- **Linear mode** — Single-card dynamic rendering with auto-split on element overflow
- **CardKit v2.0** — Streaming API with IM PATCH fallback
- **Completion stats** — Footer shows duration, model, token usage

## Install

```bash
hermes plugins install https://github.com/lookatlook-666/hermes-lark-streaming
hermes gateway restart
```

### Uninstall

```bash
HERMES_PYTHON=~/.hermes/hermes-agent/venv/bin/python3
$HERMES_PYTHON -m hermes_lark_streaming cleanup
hermes plugins uninstall hermes-lark-streaming
hermes gateway restart
```

## Configuration

```yaml
streaming:
  enabled: true
  linear: true
  panel_expanded: false
  card_ttl_sec: 600
  inject_time: false
  footer:
    fields:
      - [status, elapsed, model, api_calls]
      - [tokens, context, history_offset, compression_exhausted]
    show_label: true
```

## Key Fixes (v0.11.0)

| Issue | Fix |
|-------|-----|
| Card freezes after element overflow | Auto-split |
| Dead end after split failure + re-overflow | Overflow split bypasses `split_disabled` |
| Config re-reads from disk every access | 5s TTL cache |
| Concurrent message interrupt missed | `threading.Lock` on `_started_msg_ids` |

[Full changelog →](CHANGELOG.md)
