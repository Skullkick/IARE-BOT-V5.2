# IARE-BOT Model Context Protocol (MCP) Specification

This document specifies the architecture, integration protocol, tool schemas, and operational guidelines for the **IARE-BOT Model Context Protocol (MCP) Server** (`iare_mcp_server.py`).

---

## 1. Architectural Overview & Design Rationale

### The Challenge of In-Process AI in Telegram Bots
Running autonomous LLM agents or long-running triage loops directly inside the Telegram bot process (e.g. via `asyncio.create_task` closures) presents severe drawbacks in production:
1. **Memory Bloat & Leaks:** Agent execution stacks, token buffers, and HTTP client sessions remain pinned in process memory, risking Out-Of-Memory (OOM) termination on resource-constrained dynos (e.g. Heroku 512MB RAM cap).
2. **Event Loop Contention:** Heavy network I/O or token parsing inside the main event loop introduces latency and drops polling/webhook responsiveness for thousands of students.
3. **Task Loss on Dyno Restarts:** In-memory asynchronous tasks are lost if the bot container cycles or redeploys while an agent is investigating a ticket.

### The Decoupled MCP Solution
The IARE-BOT MCP Server runs as a **fully isolated child process or standalone daemon**. It communicates over standard stdio / SSE transport using the official Model Context Protocol standard (`mcp>=1.3.0`).

```
┌────────────────────────────────────────────────────────┐
│               IARE Telegram Bot (main.py)              │
│  - Ultra-lightweight event loop (< 50MB RAM)           │
│  - Receives /report -> Persists to reports.db / Postgres│
│  - Forwards immediately to Maintainers / Admins        │
└──────────────────────────┬─────────────────────────────┘
                           │ Shared Databases (SQLite / Postgres)
                           ▼
┌────────────────────────────────────────────────────────┐
│             Hermes Agent / MCP Client Runner           │
│  - Autonomous persistent agent runner                  │
│  - Configured via ~/.hermes/config.yaml                │
└──────────────────────────┬─────────────────────────────┘
                           │ Stdio / SSE Transport (JSON-RPC)
                           ▼
┌────────────────────────────────────────────────────────┐
│            IARE MCP Server (iare_mcp_server.py)        │
│  - Deterministic Python tools only                     │
│  - Direct Telegram HTTP API for one-shot resolution    │
│  - Concurrency guards prevent duplicate replies        │
└────────────────────────────────────────────────────────┘
```

---

## 2. Hermes Agent Configuration

Hermes Agent (from Nous Research) features native MCP support. To connect Hermes Agent to `iare_mcp_server.py`, add the server definition to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  iare_bot:
    command: "python"
    args:
      - "d:/IARE-BOT-V5.2/iare_mcp_server.py"
    env:
      BOT_TOKEN: "YOUR_TELEGRAM_BOT_TOKEN"
      DATABASE_URL: "postgres://user:pass@host:5432/dbname"
```

### Claude Desktop Configuration (Alternative)
To connect Claude Desktop for maintainer triage, add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "iare-bot": {
      "command": "python",
      "args": ["d:/IARE-BOT-V5.2/iare_mcp_server.py"],
      "env": {
        "BOT_TOKEN": "YOUR_TELEGRAM_BOT_TOKEN"
      }
    }
  }
}
```

---

## 3. Tool Specifications

### 1. `check_portal_status`
- **Description:** Performs a deterministic network health check against the college Samvidha portal.
- **Parameters:**
  - `portal_url` (string, optional, default: `"https://samvidha.iare.ac.in/index"`): The endpoint to probe.
- **Returns:**
  ```json
  {
    "online": true,
    "status_code": 200,
    "latency_ms": 284,
    "error": null
  }
  ```
- **Error States:** Returns `status_code: 504` on gateway timeout, or `status_code: 0` on DNS/network connection drops.

---

### 2. `get_pending_reports`
- **Description:** Fetches unhandled student reports from `reports.db`.
- **Parameters:**
  - `limit` (integer, optional, default: `10`): Maximum number of reports to retrieve.
- **Returns:**
  ```json
  [
    {
      "report_id": "rep_9a7b2c",
      "username": "21951A0501",
      "report_text": "Attendance is showing 0% after login",
      "chat_id": 987654321,
      "reply_status": 0
    }
  ]
  ```

---

### 3. `send_reply`
- **Description:** Non-conversational, one-shot ticket resolution action. Sends the verified resolution to the student via the Telegram Bot HTTP API, marks the ticket resolved in SQLite and PostgreSQL, and notifies maintainers.
- **Parameters:**
  - `report_id` (string, required): The unique ticket identifier.
  - `resolution_text` (string, required): Factual explanation or troubleshooting guidance.
- **Concurrency Guard:**
  - Checks whether `reply_status == 1` before dispatching.
  - If a human maintainer already replied, returns:
    ```json
    {
      "success": false,
      "status": "already_resolved",
      "reason": "Report 'rep_9a7b2c' has already been resolved."
    }
    ```
- **Success Return:**
  ```json
  {
    "success": true,
    "report_id": "rep_9a7b2c",
    "status": "resolved",
    "sent_to_chat_id": 987654321
  }
  ```

---

### 4. `read_recent_errors`
- **Description:** Reads the tail of `bot_errors.log` without loading large files into memory.
- **Parameters:**
  - `lines` (integer, optional, default: `50`): Max lines to return.
  - `user_chat_id` (integer, optional): Filter entries specifically matching the user's chat ID.
- **Returns:** List of matching log lines as strings.

---

### 5. `get_system_health`
- **Description:** Gathers host system metrics via `psutil`.
- **Returns:**
  ```json
  {
    "cpu_percent": 14.2,
    "memory_used_mb": 210.5,
    "memory_total_mb": 1024.0,
    "memory_percent": 20.6,
    "disk_percent": 45.1
  }
  ```

---

### 6. `get_user_profile_context`
- **Description:** Queries student registration, session validity, and ban status.
- **Parameters:**
  - `chat_id` (integer, required): Telegram user chat ID.
- **Returns:**
  ```json
  {
    "chat_id": 987654321,
    "username": "21951A0501",
    "has_active_session": true,
    "is_banned": false
  }
  ```

---

### 7. `draft_announcement`
- **Description:** Formats raw text into Telegram-ready dual-UI templates (`msg_updated_ui` monospace codeblock and `msg_traditional_ui` markdown).
- **Parameters:**
  - `raw_text` (string, required): The announcement body.
  - `send_preview` (boolean, optional, default: `true`): If `true`, dispatches a test preview to admins/maintainers.
- **Returns:**
  ```json
  {
    "success": true,
    "formatted_updated_ui": "```ANNOUNCEMENT\nSystem maintenance...\n```",
    "formatted_traditional_ui": "**ANNOUNCEMENT**\n\nSystem maintenance...",
    "preview_sent_to_managers": true,
    "manager_recipients_count": 2
  }
  ```

---

### 8. `broadcast_announcement`
- **Description:** Broadcasts an announcement using an asynchronous queue worker engine with rate limiting and automatic backoff on HTTP 429 (`retry_after`). Reuses the battle-tested queue distribution pattern from `METHODS/manager_operations.py`.
- **Parameters:**
  - `announcement_text` (string, required): The message to broadcast.
  - `target` (string, optional, default: `"admins"`): Target scope:
    - `"admins"`: Broadcasts only to bot admins and maintainers (safe preview/incident alert).
    - `"all"`: Broadcasts to all registered students and managers.
  - `reason` (string, optional): Incident tag (e.g. `"portal_downtime_recovery"`, `"scheduled_maintenance"`).
- **Returns:**
  ```json
  {
    "status": "completed",
    "target": "all",
    "total_recipients": 1240,
    "successful": 1238,
    "failed": 2,
    "duration_seconds": 46.1,
    "reason": "portal_downtime_recovery"
  }
  ```

---

## 4. Agent Resolution Policy (Non-Conversational Discipline)

When configuring Hermes Agent or any LLM agent for support triage, enforce the following system prompt:

```markdown
You are the IARE-BOT Automated Ticket Resolver.

DIRECTIVES:
1. You are NOT a conversational chatbot. Do not greet, do not apologize, do not engage in pleasantries.
2. Evaluate each pending report using your available tools (check_portal_status, read_recent_errors, get_user_profile_context).
3. If and ONLY IF you identify a factual, verified answer or outage root-cause, call the `send_reply` tool with a concise resolution.
4. If the report describes a code bug, requires maintainer permissions, or lacks clear diagnostics, DO NOT CALL `send_reply`. Simply exit and leave the ticket for maintainers.
```

---

## 5. Security & Verification Rules

1. **Credential Isolation:** Passwords and encrypted session tokens are NEVER returned in tool responses.
2. **Network Decoupling:** `send_reply` uses direct HTTP `POST https://api.telegram.org/bot<TOKEN>/sendMessage`. It does not touch or block the Pyrogram client session.
3. **Database Consistency:** Dual-write to SQLite and Postgres ensures synchronization across local test benches and cloud deployments.
4. **Password Protection:** When `MCP_PASSWORD` is configured, HTTP/SSE transport strictly rejects unauthenticated connections with `401 Unauthorized`.

---

## 6. Lifecycle & Subprocess Management

When running the main Telegram bot (`python main.py`), the MCP server can either remain idle (for client-spawned stdio runners) or be automatically started as an isolated background subprocess.

### Environment Variables
| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `ENABLE_MCP_SERVER` | `false` | When set to `true`, `main.py` automatically spawns `iare_mcp_server.py` as an isolated subprocess. |
| `MCP_PASSWORD` | `""` | Secret password required to access the MCP server (enforced via `Authorization`, `X-MCP-Password`, or `?password=`). |
| `MCP_TRANSPORT` | `stdio` | Transport protocol: `"stdio"` (for local agent pipes) or `"sse"` (for network/remote agents). |
| `MCP_HOST` | `0.0.0.0` | Host interface to bind when running SSE transport. |
| `MCP_PORT` | `8000` | Port to listen on when running SSE transport (`/sse` endpoint). |

### Graceful Shutdown
`main.py` uses `atexit` signal handlers to ensure that whenever the bot process shuts down (e.g., `SIGINT`, `SIGTERM`, or crash), the background MCP server subprocess is cleanly terminated with no zombie processes left running.
