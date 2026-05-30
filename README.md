# hermes-lark-streaming

Feishu CardKit v2.0 streaming cards plugin for [Hermes Agent](https://github.com/NousResearch/hermes-agent). Replaces plain-text AI replies with real-time interactive cards.

> **Note: This version is incompatible with the upstream [Aowen-Nowor/hermes-lark-streaming](https://github.com/Aowen-Nowor/hermes-lark-streaming).** Both diverged from the same early codebase and evolved independently with different implementations.

## Install

```bash
hermes plugins install https://github.com/lookatlook-666/hermes-lark-streaming
```

Enable when prompted, then restart the gateway:

```bash
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

Auto-injected into `~/.hermes/config.yaml` on first install:

```yaml
streaming:
  enabled: true
  linear: true               # Single-card dynamic rendering (recommended)
  panel_expanded: false
  card_ttl_sec: 600
  inject_time: false         # Inject <time>HH:MM:SS</time> before user messages
  footer:
    fields:
      - [status, elapsed, model, api_calls]
      - [tokens, context, history_offset, compression_exhausted]
    show_label: true
```

## Key Fixes (v0.11.0)

| Issue | Fix |
|-------|-----|
| Card freezes after element limit exceeded | Auto-split, `element_limit_hit` flag triggers new card |
| Dead end after split failure + re-overflow | Split bypasses `split_disabled` when element limit hit |
| Config re-reads from disk on every access | 5-second TTL cache for high-frequency scenarios |
| Concurrent messages miss interrupt detection | `threading.Lock` on `_started_msg_ids` |

[Full changelog →](CHANGELOG.md)

## Known Limitations

- Some Hermes tools (terminal, file, code_execution) are unavailable on Feishu platform; tool panels show status forwarded from Hermes side only
- Incompatible with the upstream version; cannot be installed simultaneously
