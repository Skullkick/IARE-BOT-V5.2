# IARE UNOFFICIAL BOT

Telegram bot designed for students of the Institute of Aeronautical Engineering (IARE). It interfaces with the college's [Samvidha Portal](https://samvidha.iare.ac.in/index) to scrape, calculate, and format academic attendance, biometric punch logs, examination results, and laboratory record submissions.

> **Looking for the Student Guide?** Refer to the **[Student User Guide](BEGINNERS_GUIDE.md)** for a step-by-step walkthrough of student commands, interactive buttons, settings, and troubleshooting.

---

## Table of Contents

1. [Key Features](#key-features)
2. [Environment Variables](#environment-variables)
3. [Quick Start (Local Deployment)](#quick-start-local-deployment)
4. [Deployment to Heroku](#deployment-to-heroku)
5. [Automated Testing](#automated-testing)
6. [Available Commands & Controls](#available-commands--controls)
   - [Student Commands](#student-commands)
   - [Interactive Menu Buttons](#interactive-menu-buttons)
   - [Admin & Maintainer Operations](#admin--maintainer-operations)
7. [AI Assistant Integration (MCP Server)](#ai-assistant-integration-mcp-server)
8. [Project Architecture](#project-architecture)

---

## Key Features

- **Attendance Tracking:** Real-time subject-wise classes conducted versus attended, individual percentages, and aggregate percentage.
- **Bunk Calculator:** Dynamic safe-miss and catch-up class calculations tailored to your personal attendance threshold (default: 75%).
- **Biometric Logs:** Daily first in-time, latest out-time, total campus hours, and 6-hour gap tracking.
- **Laboratory Records:** In-chat PDF uploads with automatic document optimization and compression for files exceeding 1 MB.
- **Student Profile & Academics:** SGPA/CGPA breakdown, Continuous Internal Evaluation (CIE) mid-term scores, and tuition/transport fee receipts.
- **In-App Protected User Guide:** Interactive `/help` and `/guide` menu equipped with Telegram `protect_content` to prevent copying and unauthorized forwarding.
- **Support Ticketing System:** Inquiries submitted via `/report` are logged with Indian Standard Time (IST) timestamps and can be answered directly by maintainers.
- **Admin & Broadcast Suite:** Intelligent broadcast engine with worker-pool rate limiting (~25 msg/sec) and FloodWait backoff, maintainer appointment via message forwarding, and user session controls.
- **Model Context Protocol (MCP) Server:** Built-in MCP interface (`iare_mcp_server.py`) enabling AI assistants to monitor portal health, inspect reports, and handle administrative replies securely.

---

## Environment Variables

Configure the following variables in your environment or within a `.env` file:

### Core Telegram Credentials (Required)

| Variable | Description | Required | Example |
| :--- | :--- | :--- | :--- |
| `BOT_TOKEN` | Bot API token obtained from [@BotFather](https://t.me/BotFather). | Yes | `1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ` |
| `API_ID` | Telegram API App ID from [my.telegram.org](https://my.telegram.org/auth). | Yes | `12345678` |
| `API_HASH` | Telegram API Hash from [my.telegram.org](https://my.telegram.org/auth). | Yes | `abcdef0123456789abcdef0123456789` |

### Administration & Security

| Variable | Description | Required | Default / Note |
| :--- | :--- | :--- | :--- |
| `ADMIN_AUTHORIZATION_PASS` | Secret passcode used with `/authorize` to verify and register new bot administrators. | Recommended | — |
| `ENCRYPTION_KEY` | 32-byte URL-safe base64-encoded key for Fernet credential encryption. | Recommended | A derived key is used as a fallback if omitted. |
| `DEVELOPER_CHAT_ID` | Telegram Chat ID of the primary bot developer for error alerts. | Optional | — |
| `MAINTAINER_CHAT_ID` | Telegram Chat ID of initial maintainers. | Optional | — |

> **Tip:** Generate a secure `ENCRYPTION_KEY` using Python:
> ```bash
> python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
> ```

### Database Configuration (Optional / Remote PostgreSQL Sync)

The bot operates completely with local SQLite databases out of the box. To persist credentials and synchronized state across cloud container restarts, configure a PostgreSQL database:

| Variable | Description | Required | Default |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | Complete PostgreSQL connection URI (auto-configured on platforms like Heroku/Neon/Supabase). | Optional | — |
| `POSTGRES_USER_ID` | PostgreSQL user identifier (used if `DATABASE_URL` is omitted). | Optional | — |
| `POSTGRES_PASSWORD` | PostgreSQL user password. | Optional | — |
| `POSTGRES_DATABASE` | PostgreSQL database name. | Optional | — |
| `POSTGRES_HOST` | PostgreSQL server hostname or IP address. | Optional | — |
| `POSTGRES_PORT` | PostgreSQL connection port. | Optional | `5432` |

### Model Context Protocol (MCP) Server (Optional)

| Variable | Description | Required | Default |
| :--- | :--- | :--- | :--- |
| `ENABLE_MCP_SERVER` | Set to `true` (or `1`, `yes`, `on`) to start the MCP server as a background process alongside `main.py`. | Optional | `false` |
| `MCP_PASSWORD` | Bearer token / secret password securing HTTP/SSE MCP endpoints against unauthorized access. | Optional | — |
| `MCP_HOST` | Host interface for the MCP server. | Optional | `127.0.0.1` |
| `MCP_PORT` | Port for the MCP server. | Optional | `8000` |
| `MCP_TRANSPORT` | Communication protocol: `stdio` for local AI CLI integration, `sse` for network assistants. | Optional | `stdio` |

---

## Quick Start (Local Deployment)

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/Skullkick/IARE-BOT-V5.2.git
cd IARE-BOT-V5.2
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create a `.env` file in the root directory:
```env
BOT_TOKEN=your_bot_token
API_ID=your_api_id
API_HASH=your_api_hash
ADMIN_AUTHORIZATION_PASS=your_secret_admin_code
ENCRYPTION_KEY=your_fernet_encryption_key

# Optional: Enable MCP server in background
ENABLE_MCP_SERVER=false
MCP_PASSWORD=your_mcp_security_password
```

### 5. Start the Application
```bash
python main.py
```

---

## Deployment to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Skullkick/IARE-BOT-V5.2)

1. Click the **Deploy to Heroku** button above or link your GitHub repository in the Heroku Dashboard.
2. Fill in the required environment variables (`BOT_TOKEN`, `API_ID`, `API_HASH`, `ADMIN_AUTHORIZATION_PASS`).
3. Heroku Postgres will be provisioned automatically according to `app.json`.
4. Enable the `worker` dyno in the Heroku Resources tab:
   ```bash
   heroku ps:scale worker=1
   ```

---

## Automated Testing

The project maintains a test suite covering authentication, cryptography, portal scraping, rate limiting, and MCP tools:

```bash
# Run all test suites
python -m pytest

# Run tests with terminal coverage summary
python -m pytest --cov=. --cov-report=term-missing
```

---

## Available Commands & Controls

### Student Commands

| Command | Description |
| :--- | :--- |
| `/start` | Initializes the session, greets the user, and sends the navigation menu. |
| `/login <roll> <pass>` | Authenticates against Samvidha. Passwords with spaces should be quoted (e.g., `/login 21951A0501 "my secret pass"`). |
| `/logout` | Terminates the current active session and clears temporary cookies. |
| `/report <message>` | Submits a support inquiry or bug report (timestamped in Indian Standard Time). |
| `/settings` | Configures personal thresholds (attendance/biometric), UI layout, and PDF title extraction mode. |
| `/help` or `/guide` | Opens the interactive, anti-forwarding protected user guide directly in chat. |

### Interactive Menu Buttons

- **Attendance:** Displays subject-wise conducted vs. attended classes and aggregate percentage.
- **Bunk:** Calculates safe absences or required attendance based on your configured threshold.
- **Biometric:** Today's check-in/out timestamps and completed campus hours.
- **Labs Records:** Upload laboratory experiment PDFs, view submitted files, and delete records.
- **Student Info:** Academic GPA, Continuous Internal Evaluation (CIE) mid marks, and fee payment receipts.
- **Saved Username:** View saved credentials, delete stored credentials, or remove and log out.
- **User Guide:** 1-tap shortcut to open the interactive help manual.

### Admin & Maintainer Operations

*Accessible exclusively to authorized maintainers and administrators:*

| Command / Action | Description |
| :--- | :--- |
| `/admin` | Displays the graphical administration control panel. |
| `/maintainer` | Displays the maintainer operations panel. |
| *Forward Message* | Admins can forward any message from a student to the bot to trigger the inline maintainer confirmation prompt. |
| `/add_maintainer <chat_id>` | Grants maintainer status to a designated Telegram chat ID. |
| `/announce <message>` | Broadcasts announcements with FloodWait protection and worker-pool throughput throttling (~25 msg/sec). |
| `/rshow` | Lists pending student support reports. |
| `/reply <reply text>` | Replies to a user ticket by quote-replying to the report message. |
| `/rclear` | Purges processed tickets from the pending queue. |
| `/lusers` | Generates a daily active users report with QR verification. |
| `/tusers` | Summarizes registered user counts in the past 24 hours. |
| `/ban <username>` / `/unban <username>` | Manages account restrictions. |
| `/reset` | Flushes transient SQLite session tables. |

---

## AI Assistant Integration (MCP Server)

IARE-BOT features a native **Model Context Protocol (MCP)** implementation (`iare_mcp_server.py`). AI agents (such as Cursor, Claude Desktop, and Antigravity) can connect over Standard I/O or Server-Sent Events (SSE) to act as administrative assistants:

- **Available Tools:** `check_portal_status`, `get_reports_summary`, `send_reply`, `draft_announcement`, `broadcast_announcement`, and `read_recent_errors`.
- **Security:** Protected via `MCP_PASSWORD` Bearer token authentication.

For step-by-step setup instructions, refer to:
- **[How to Connect MCP](Project%20Documents/HOW_TO_CONNECT_MCP.md)**
- **[MCP Specification Document](Project%20Documents/MCP_SPECIFICATION.md)**

---

## Project Architecture

```text
IARE-BOT-V5.2/
├── Buttons/
│   ├── buttons.py              # User inline keyboard layouts, callback router, interactive guide
│   └── manager_buttons.py      # Admin & maintainer interactive panels
├── CONFIGURE/
│   └── extract_index.py        # Table and DOM index parsers for Samvidha HTML pages
├── DATABASE/
│   ├── managers_handler.py     # SQLite manager permissions and tracker persistence
│   ├── pgdatabase.py           # Persistent PostgreSQL datastore and cloud sync
│   ├── tdatabase.py            # Local SQLite session, credential, and report caches
│   └── user_settings.py        # User preferences (thresholds, title mode, UI styles)
├── METHODS/
│   ├── crypto_helper.py        # Fernet AES-256 credential encryption and key derivation
│   ├── lab_operations.py       # Lab record scraping, upload validation, and deletion
│   ├── labs_handler.py         # PDF ingestion and title state management
│   ├── manager_operations.py   # Broadcast engine, report dispatcher, maintainer auth
│   ├── operations.py           # Academic scrapers (attendance, bunk, biometric, marks)
│   ├── pdf_compressor.py       # Smart PDF compression (<1 MB) with multi-tier downsampling
│   └── portal_client.py        # Asynchronous HTTP client, session management, and HTML parser
├── Project Documents/          # Architectural specifications, QA reports, and MCP guides
├── tests/                      # Pytest automated test suite (127 passing tests)
├── BEGINNERS_GUIDE.md          # Comprehensive Student User Guide
├── iare_mcp_server.py          # FastMCP server for AI agent management
├── main.py                     # Application entry point and Pyrogram client dispatcher
└── requirements.txt            # Python dependencies
```

---

## License & Disclaimer

This is an **unofficial** utility developed for educational purposes to assist students of the Institute of Aeronautical Engineering (IARE). It is not officially affiliated with or endorsed by IARE.
