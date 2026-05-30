# feishu-slash-confirm

Interactive confirmation cards for Hermes Agent Feishu slash commands (`/new`, `/reset`, `/undo`, `/reload-mcp`).

When you type a slash command, instead of a plain text confirmation prompt, this plugin displays an interactive card with three buttons:

- ✅ **Once** — Allow this one time
- 🔒 **Always** — Always allow (remember preference)
- ❌ **Cancel** — Cancel the command

## Installation

```bash
hermes plugins install https://github.com/lookatlook-666/feishu-slash-confirm
hermes gateway restart
```

### Uninstall

```bash
hermes plugins uninstall feishu-slash-confirm
hermes gateway restart
```

## How It Works

The plugin monkey-patches the Feishu adapter to:

1. Add `send_slash_confirm` — sends an interactive CardKit card with confirm/always/cancel buttons
2. Wrap `_on_card_action_trigger` — handles button clicks and resolves the slash command via `tools.slash_confirm.resolve()`

## Supported Commands

- `/new` — New conversation
- `/reset` — Reset session
- `/undo` — Undo last message
- `/reload-mcp` — Reload MCP tools

## License

MIT
