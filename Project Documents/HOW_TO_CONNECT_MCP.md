# How to Connect IARE-BOT MCP to Any AI Agent

A beginner-friendly guide to connecting the **IARE-BOT Model Context Protocol (MCP) Server** (`iare_mcp_server.py`) to **Hermes Agent**, **Claude Desktop**, **Cursor / Windsurf**, or **custom Python scripts**.

---

## What is this MCP Server?

The **IARE-BOT MCP Server** gives your AI agent superpowers to interact directly with the IARE-BOT infrastructure without touching the Telegram bot's memory:

- 🩺 **`check_portal_status`**: Pings Samvidha college portal to see if it's down or timing out.
- 📋 **`get_pending_reports`**: Pulls unhandled student tickets.
- ✉️ **`send_reply`**: Sends a formal, verified resolution to a student and alerts maintainers.
- 📜 **`read_recent_errors`**: Scans `bot_errors.log` to see what broke for a specific student.
- 💻 **`get_system_health`**: Checks server RAM, CPU, and disk stats.
- 👤 **`get_user_profile_context`**: Looks up student roll number, active session, and ban status.
- 📢 **`draft_announcement`**: Previews announcements in codeblock and markdown formats.
- 🚀 **`broadcast_announcement`**: Broadcasts announcements to students safely with flood protection.

---

## Step 1: Prerequisites

1. **Python Environment:** Make sure you have Python 3.10+ installed with `mcp` package:
   ```bash
   pip install "mcp>=1.3.0" httpx psutil python-dotenv
   ```

2. **Environment Variables:** The MCP server needs your bot credentials:
   - `BOT_TOKEN`: Your Telegram Bot API token (from [@BotFather](https://t.me/BotFather)).
   - `DATABASE_URL` *(Optional)*: PostgreSQL connection URI (if using cloud Postgres).
   - `ENCRYPTION_KEY` *(Optional)*: Key for student credential encryption.

You can set these in your system environment or in a `.env` file in the project directory:
```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
```

---

## Step 2: Choose Your Agent

Pick the agent platform you want to use below:

### Option A: Hermes Agent (Nous Research)

Hermes Agent has **native built-in MCP support**.

1. Open your Hermes configuration file:
   - **Linux/macOS:** `~/.hermes/config.yaml`
   - **Windows:** `C:\Users\<YourUsername>\.hermes\config.yaml`

2. Add the `iare_bot` server under `mcp_servers`:
   ```yaml
   mcp_servers:
     iare_bot:
       command: "python"
       args:
         - "D:/IARE-BOT-V5.2/iare_mcp_server.py"
       env:
         BOT_TOKEN: "YOUR_TELEGRAM_BOT_TOKEN_HERE"
   ```
   *(Note: Replace `D:/IARE-BOT-V5.2` with your actual repository folder path. Use forward slashes `/` even on Windows!)*

3. Restart Hermes Agent:
   ```bash
   hermes
   ```
   Hermes will automatically detect and load all 8 tools!

---

### Option B: Claude Desktop

1. Open Claude Desktop configuration:
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

2. Add the server config:
   ```json
   {
     "mcpServers": {
       "iare-bot": {
         "command": "python",
         "args": ["D:/IARE-BOT-V5.2/iare_mcp_server.py"],
         "env": {
           "BOT_TOKEN": "YOUR_TELEGRAM_BOT_TOKEN_HERE"
         }
       }
     }
   }
   ```

3. Restart Claude Desktop. You will see a hammer icon 🔨 in the chat box showing all 8 IARE tools ready to use.

---

### Option C: Cursor / Windsurf / VS Code (Cline or Roo-Code)

1. Open the **MCP Settings** or `mcp_config.json` in your IDE.
2. Add:
   ```json
   {
     "mcpServers": {
       "iare_bot": {
         "command": "python",
         "args": ["D:/IARE-BOT-V5.2/iare_mcp_server.py"],
         "env": {
           "BOT_TOKEN": "YOUR_TELEGRAM_BOT_TOKEN_HERE"
         }
       }
     }
   }
   ```

---

### Option D: Custom Python Script (Using Official `mcp` Client)

If you are building your own AI agent with LangChain, LlamaIndex, or raw Python:

```python
import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Define the server process
server_params = StdioServerParameters(
    command="python",
    args=["D:/IARE-BOT-V5.2/iare_mcp_server.py"],
    env={**os.environ, "BOT_TOKEN": "YOUR_TELEGRAM_BOT_TOKEN"}
)

async def main():
    # Connect over stdio
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. List available tools
            tools = await session.list_tools()
            print("Available Tools:", [t.name for t in tools.tools])

            # 2. Check Samvidha portal health
            health = await session.call_tool("check_portal_status", {})
            print("Portal Status:", health.content[0].text)

            # 3. Fetch pending student reports
            reports = await session.call_tool("get_pending_reports", {"limit": 5})
            print("Pending Reports:", reports.content[0].text)

if __name__ == "__main__":
    asyncio.run(main())
```

---

### Option E: Running Automatically with `main.py` (Remote Agents via SSE)

If you want `python main.py` to automatically launch the MCP server in the background so remote agents can connect over the network/internet:

1. In your `.env` (or environment variables), enable the MCP server, set your password, and configure SSE transport:
   ```env
   ENABLE_MCP_SERVER=true
   MCP_PASSWORD=your_super_secret_password
   MCP_TRANSPORT=sse
   MCP_HOST=0.0.0.0
   MCP_PORT=8000
   ```

2. Run your bot normally:
   ```bash
   python main.py
   ```
   `main.py` will automatically start `iare_mcp_server.py` protected by your password on port `8000`!

3. Now, connect your remote agent securely:

   **Method 1: Query Parameter (Simplest):**
   ```yaml
   # In ~/.hermes/config.yaml on the remote machine
   mcp_servers:
     iare_bot:
       url: "http://YOUR_SERVER_IP:8000/sse?password=your_super_secret_password"
   ```

   **Method 2: Authorization Header:**
   ```yaml
   # In ~/.hermes/config.yaml on the remote machine
   mcp_servers:
     iare_bot:
       url: "http://YOUR_SERVER_IP:8000/sse"
       headers:
         Authorization: "Bearer your_super_secret_password"
   ```

*(Any request without the correct password is automatically blocked with `401 Unauthorized`).*

---

## Step 3: How to Instruct Your Agent (Prompting)

Give your AI agent these system instructions so it acts as an **automated resolution engine**, not a chatty assistant:

```markdown
You are the IARE-BOT Autonomous Support & Ops Agent.
You have access to internal bot tools via MCP.

RULES:
1. NON-CONVERSATIONAL: Never greet, apologize, or chit-chat.
2. TICKET RESOLUTION:
   - Use `get_pending_reports` to check open tickets.
   - Use `check_portal_status` or `read_recent_errors` to diagnose the cause.
   - If you have a verified solution (e.g. portal downtime or user formatting error), invoke `send_reply(report_id, resolution_text)`.
   - If you are unsure or it is a complex code bug, DO NOT call `send_reply`. Leave it for human maintainers.
3. ANNOUNCEMENTS:
   - For draft previews, use `draft_announcement(text, send_preview=True)` to send only to admins.
   - For broad announcements, use `broadcast_announcement(text, target="admins")` by default. Only set `target="all"` when explicitly confirmed.
```

---

## Step 4: Quick 30-Second Test

To verify your server works without launching an agent, run this in your terminal:

```bash
python -c "import asyncio, iare_mcp_server; asyncio.run(iare_mcp_server.mcp.call_tool('get_system_health', {}))"
```

If it prints system stats (`cpu_percent`, `memory_used_mb`), your server is 100% operational!
