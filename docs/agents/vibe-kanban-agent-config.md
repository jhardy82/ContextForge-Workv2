# Vibe Kanban – Multi‑Agent Configuration Guide

This playbook documents how to bring the locally installed `vibe-kanban` binary online inside the ContextForge workspace and wire it into the three AI coding agents we rely on day‑to‑day (Codex/OpenCode, GitHub Copilot CLI, Claude Code). All steps were validated from WSL inside `PowerShell Projects`.

> **Reminder:** `cf_cli.py` stays the authoritative workflow orchestrator. Use it (or Codex tasks that shell out through it) when you want to script against these setup commands.

---

## 1. Bootstrap the Linux Binary

Running `npx vibe-kanban` inside WSL currently fails (EPERM while touching the Windows cache path). Instead of fighting that, download the Linux build once and re‑use it:

```bash
# From /mnt/c/Users/james.e.hardy/Documents/PowerShell Projects
npm pack vibe-kanban                              # produces vibe-kanban-0.0.120.tgz (183 MB)
mkdir -p .cache/vibe-kanban/linux-x64
tar -xzf vibe-kanban-0.0.120.tgz -C .cache/vibe-kanban/linux-x64 --strip-components=1
python3 - <<'PY'
import pathlib, zipfile
pkg = pathlib.Path(".cache/vibe-kanban/linux-x64/dist/linux-x64/vibe-kanban.zip")
out = pathlib.Path(".cache/vibe-kanban/bin")
out.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(pkg) as z:
    z.extractall(out)
bin_path = out / "vibe-kanban"
bin_path.chmod(0o755)
print(bin_path)
PY
```

Create a tiny wrapper so Codex, Copilot, or Claude shells can launch it identically:

```bash
cat <<'SH' > tools/vibe-kanban/run.sh
#!/usr/bin/env bash
set -euo pipefail
BIN="$(dirname "${BASH_SOURCE[0]}")/../../.cache/vibe-kanban/bin/vibe-kanban"
if [[ ! -x "$BIN" ]]; then
  echo "vibe-kanban binary not found – re-run npm pack instructions." >&2
  exit 1
fi
exec "$BIN" "$@"
SH
chmod +x tools/vibe-kanban/run.sh
```

Launching:

```bash
tools/vibe-kanban/run.sh &
```

The binary will log a URL (typically `http://127.0.0.1:<port>`); open it in Windows Edge/Chrome to finish onboarding.

---

## 2. Configuration Storage & Structure

`vibe-kanban` uses the standard directories exposed by `dirs`/`dirs-sys`, so after the first launch you get:

- **WSL/Linux**: `$XDG_CONFIG_HOME/vibe-kanban/config.json` (falls back to `~/.config/vibe-kanban/config.json`)
- **Windows**: `%APPDATA%\vibe-kanban\config.json`

The schema (visible in the binary’s error messages) includes:

```jsonc
{
  "config_version": 8,
  "theme": "SYSTEM",
  "profile": {
    "display_name": "Codex Lab",
    "providers": [
      "CLAUDE_CODE",
      "CODEX",
      "COPILOT"
    ]
  },
  "editor": {
    "editor_type": "VS_CODE",
    "custom_command": "",
    "remote_ssh_host": "",
    "remote_ssh_user": ""
  },
  "github": {
    "pat": "",
    "oauth_token": "",
    "primary_email": "",
    "default_pr_base": "main",
    "analytics_enabled": false
  },
  "notifications": {
    "sound_enabled": true,
    "push_enabled": false,
    "sound_file": ""
  },
  "workspace_dir": "/mnt/c/Users/james.e.hardy/Documents/PowerShell Projects"
}
```

📌 **Editing tip:** keep changes minimal and valid JSON. If you break the file, the binary prints `struct Config with 15 elements` errors on startup.

---

## 3. Agent‑Specific Integration

Vibe shells out to different CLIs per agent. The strings embedded in the binary make those commands explicit; we just need to ensure each CLI works independently before vibe orchestrates it.

### 3.1 Codex / OpenCode

- **CLI invoked:** `npx -y opencode-ai@1.0.68 run --print-logs …`
- **Where config lives:** `%APPDATA%\opencode` on Windows, `~/.config/opencode` on Linux.
- **What to do:**

```bash
# Install dependencies once (WSL)
npm install -g opencode-ai@1.0.68
opencode --version

# Log in (browser prompt) and create the config/opencode.json file
opencode login

# Sanity check the agent tools
opencode doctor
```

- **Update vibe config:** add `"CODEX"` to the `providers` array. If you want Codex to be the default, reorder so it is first.
- **WSL ↔ Windows note:** OpenCode stores session data in Windows AppData. Share it with WSL by exporting `OPENCODE_CONFIG_PATH=/mnt/c/Users/james.e.hardy/AppData/Roaming/opencode/opencode.json` before launching vibe.

### 3.2 GitHub Copilot CLI

- **CLI invoked:** `npx -y @github/copilot@0.0.358 --no-color --log-level debug …`
- **Prerequisites:** GitHub account with Copilot CLI access + `gh` logged in.
- **Setup:**

```bash
npm install -g @github/copilot@0.0.358
copilot --version
copilot login          # Opens GitHub device flow
copilot doctor         # Confirms model + permissions
```

- The Copilot CLI persists credentials in `%APPDATA%\GitHub\Copilot` or `~/.config/github-copilot-cli`. Ensure those paths are readable from WSL (symlink if necessary).
- **Config update:** include `"COPILOT"` in the provider list. Copilot supports tool execution; leave `allow_all_tools` enabled so vibe can request shell/MCP access when tasks need it.

### 3.3 Claude Code

- **Binary invoked:** `claude_code_router` (Anthropic’s local router that Claude Desktop exposes when you enable “Claude Code Integration”).
- **Prerequisites:**
  1. Install the latest Claude desktop app on Windows and enable **Settings → Developer → Claude Code Router**.
  2. Note the router port (default `1616` on Windows). The router writes logs under `%APPDATA%\Claude\router`.
  3. From WSL, forward that port: `socat TCP-LISTEN:1616,fork TCP:localhost:1616 &`.
- **Validation:**

```powershell
# Windows PowerShell
& "C:\Users\james.e.hardy\AppData\Local\Programs\Claude\claude_code_router.exe" --health
```

Expect `{"status":"ok"}`. In WSL, confirm with `curl http://127.0.0.1:1616/health`.

- **Config update:** ensure `"CLAUDE_CODE"` is listed under `profile.providers`. You can also opt into the router’s auto‑approval by exporting `CLAUDE_CODE_ROUTER_AUTO_APPROVE=true` before launching vibe (otherwise the router prompts inside the Claude UI).

---

## 4. Putting It Together

1. **Launch prerequisite daemons**
   - Start Claude Desktop and make sure the router is green.
   - If you use VPN/proxy, authenticate GitHub + OpenCode sessions first (both CLIs reuse existing logins).
2. **Export environment variables (WSL)**

```bash
export OPENCODE_CONFIG_PATH=/mnt/c/Users/james.e.hardy/AppData/Roaming/opencode/opencode.json
export CLAUDE_CODE_ROUTER_URL=http://127.0.0.1:1616
export PATH="$HOME/.npm-global/bin:$PATH"
```

3. **Start Vibe Kanban via the wrapper**

```bash
tools/vibe-kanban/run.sh \
  --port-file .cache/vibe-kanban/.port \
  --log-dir logs/vibe-kanban
```

4. **Verify inside the UI**
   - Open **Settings → Agents**.
   - You should now see `Claude Code`, `Codex`, and `GitHub Copilot` listed with a ✅ badge.
   - Run the built‑in “Test agent” button for each once; it simply proxies the same commands listed above.

---

## 5. Validation Checklist

| Check | Command | Expected |
|-------|---------|----------|
| Codex CLI healthy | `opencode doctor` | All tools ✅ |
| Copilot CLI authenticated | `copilot diagnosis` | status: OK |
| Claude Router reachable | `curl http://127.0.0.1:1616/health` | `{"status":"ok"}` |
| Vibe config valid | `jq empty ~/.config/vibe-kanban/config.json` | exit 0 |
| Providers registered | `"CLAUDE_CODE"`, `"CODEX"`, `"COPILOT"` inside config | present |

If any step fails, fix the CLI directly before involving vibe—otherwise vibe will surface opaque executor errors (the binary includes `map with a single key` / `struct Config with 15 elements` messages when JSON parsing fails).

---

## 6. Next Steps

1. Capture these steps as an SR‑4 evidence artifact (e.g., `.QSE/v2/Evidence/SR-4-20251119/vibe-kanban-agent-config.json`).
2. Automate the bootstrap via a CF_CLI task (`python cf_cli.py task create --title "vibe-kanban agent bootstrap"`).
3. Wire the wrapper (`tools/vibe-kanban/run.sh`) into a VS Code task for one‑click startups if desired.

With these pieces in place we can move between Codex (OpenCode’s MCP stack), Copilot CLI, and Claude Code without leaving the same Kanban view.***
