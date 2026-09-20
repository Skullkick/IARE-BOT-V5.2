# 📖 IARE Bot — Complete Beginner's Guide

Welcome to **IARE-BOT**! This guide is designed to help anyone—whether you are a student using the bot for the first time, a maintainer managing the platform, or a developer running the bot locally—easily understand and make the most out of every feature.

---

## 📌 Table of Contents
1. [What is IARE Bot?](#what-is-iare-bot)
2. [Quick Start: For Students](#quick-start-for-students)
   - [Step 1: Start the Bot](#step-1-start-the-bot)
   - [Step 2: Log In to Samvidha](#step-2-log-in-to-samvidha)
   - [Step 3: Handling Passwords with Spaces](#step-3-handling-passwords-with-spaces)
3. [Exploring Bot Features & Buttons](#exploring-bot-features--buttons)
   - [📊 Attendance Tracker](#-attendance-tracker)
   - [🎯 Bunk Calculator (Safe-Miss Planner)](#-bunk-calculator-safe-miss-planner)
   - [🕒 Biometric Log](#-biometric-log)
   - [💼 PAT Attendance](#-pat-attendance)
   - [📑 Lab Records Management](#-lab-records-management)
   - [🎓 Student Information & Academic History](#-student-information--academic-history)
   - [⚙️ User Settings & Customization](#️-user-settings--customization)
   - [🔒 Saved Credentials & Auto-Login](#-saved-credentials--auto-login)
   - [🚪 Logging Out](#-logging-out)
4. [Reporting Issues & Getting Help](#reporting-issues--getting-help)
5. [Guide for Maintainers & Admins](#guide-for-maintainers--admins)
   - [Admin & Maintainer Panels](#admin--maintainer-panels)
   - [Adding New Maintainers (Forward Method)](#adding-new-maintainers-forward-method)
   - [Reviewing & Replying to Reports](#reviewing--replying-to-reports)
   - [Broadcasting Announcements](#broadcasting-announcements)
   - [User Analytics & Access Control](#user-analytics--access-control)
6. [AI Agent Integration (MCP Server)](#ai-agent-integration-mcp-server)
7. [Running the Bot Locally (For Developers)](#running-the-bot-locally-for-developers)
8. [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)

---

## What is IARE Bot?

**IARE-BOT** is an unofficial Telegram automation assistant built for students of the **Institute of Aeronautical Engineering (IARE)**. It securely communicates with the college's [SAMVIDHA Portal](https://samvidha.iare.ac.in/index) to deliver:
- **Instant attendance figures** and safe bunk planning.
- **Daily biometric logs** with in/out timestamps and total campus hours.
- **Lab record uploads** with automatic smart PDF compression (< 1MB).
- **Exam marks, CGPA/SGPA summaries**, and fee payment receipts.
- **Direct support reporting** with IST timestamped responses.

---

## Quick Start: For Students

### Step 1: Start the Bot
Open your Telegram app, search for the bot handle (e.g., `@IARE_Bot`), and press the **Start** button or send:
```text
/start
```
The bot will greet you and present basic navigation instructions.

---

### Step 2: Log In to Samvidha
To fetch your academic data, log in using your college Roll Number and Samvidha password:

```text
/login <ROLL_NUMBER> <PASSWORD>
```

**Example:**
```text
/login 21951A0501 MySecretPassword123
```

> 💡 **Security Guarantee**: Your credentials are encrypted using industry-standard **AES-256 encryption** before being stored. They are solely used to authenticate your session against Samvidha and are never shared.

---

### Step 3: Handling Passwords with Spaces
If your Samvidha password contains one or more spaces, wrap the password in **double quotes (`"..."`)** or **single quotes (`'...'`)**:

**Example:**
```text
/login 21951A0501 "my pass 123"
```
or
```text
/login 21951A0501 'my pass 123'
```

---

## Exploring Bot Features & Buttons

Once you log in, the bot sends you an interactive menu with quick-action buttons:

```text
┌───────────────────────────┐
│        MAIN MENU          │
├─────────────┬─────────────┤
│ Attendance  │    Bunk     │
├─────────────┼─────────────┤
│  Biometric  │   Logout    │
├─────────────┴─────────────┤
│       Labs Records        │
├───────────────────────────┤
│       Student Info        │
├───────────────────────────┤
│      Saved Username       │
└───────────────────────────┘
```

### 📊 Attendance Tracker
- **Button:** `Attendance`
- **What it does:** Fetches your current attendance across all registered courses.
- **What you see:**
  - Course name & code.
  - Number of classes conducted vs number attended.
  - Overall aggregate attendance percentage.

---

### 🎯 Bunk Calculator (Safe-Miss Planner)
- **Button:** `Bunk`
- **What it does:** Helps you plan your schedule safely while staying compliant with the college attendance threshold (default: **75%**, adjustable in `/settings`).
- **How to read the result:**
  - **If your attendance is ABOVE the threshold:**
    > *"You can safely miss up to **X** classes and still remain above 75%."*
  - **If your attendance is BELOW the threshold:**
    > *"You need to attend the next **Y** consecutive classes to restore your attendance to 75%."*

---

### 🕒 Biometric Log
- **Button:** `Biometric`
- **What it does:** Displays your daily RFID/Biometric gate and lab punch records.
- **Details provided:**
  - First In-Time and Last Out-Time.
  - Total duration spent on campus.
  - Minimum required hours progress indicator.

---

### 💼 PAT Attendance
- **Button:** Accessible via secondary menu.
- **What it does:** Shows dedicated attendance percentages for Placement and Training (PAT) sessions and specialized modules.

---

### 📑 Lab Records Management
- **Button:** `Labs Records`
- **What it does:** Enables you to upload, review, and organize laboratory experiment PDFs directly through Telegram.
- **Uploading a Lab PDF:**
  1. Simply send a `.pdf` file in the private chat with the bot.
  2. The bot will prompt you for the experiment title (or extract it automatically depending on your `/settings`).
  3. **Automatic PDF Compression:** If your document exceeds 1MB, the bot automatically optimizes and compresses it so it stays within Samvidha's upload limits without losing readability.
- **Viewing & Deleting:**
  - You can view previously uploaded files per subject and remove outdated files with a single tap.

---

### 🎓 Student Information & Academic History
- **Button:** `Student Info`
- **Sections available:**
  - **Profile:** Full name, branch, semester, section, and mentor details.
  - **CGPA & Semester SGPA:** Historical grade cards and cumulative averages.
  - **CIE Marks:** Continuous Internal Evaluation (Mid-term) performance breakdown.
  - **Fee Payments:** Summary of paid dues, tuition receipts, and pending balances.

---

### ⚙️ User Settings & Customization
Send `/settings` to open the personal preferences menu:

1. **Attendance Threshold:** Set your personal target attendance (e.g., 65%, 75%, 80%, or 85%). The Bunk calculator will calculate safe misses according to this value.
2. **Biometric Threshold:** Adjust the expected minimum campus stay time.
3. **Title Extract Mode:** Toggle between:
   - **Auto Extract:** Automatically detects the experiment title from the first page of uploaded PDFs.
   - **Manual Title:** Prompts you to type the title for each upload.
4. **User Interface (UI):** Switch between:
   - **Traditional UI:** Compact monospace text format.
   - **Updated UI:** Modern, visually enriched layout with emoji badges and dividers.

---

### 🔒 Saved Credentials & Auto-Login
- **Button:** `Saved Username`
- **How it works:** When credentials are saved, you don't need to re-type `/login` each time your session expires.
- **Options:**
  - **Auto-Login:** Tap to immediately refresh your session.
  - **Remove:** Deletes your stored credentials from both local cache and database permanently.

---

### 🚪 Logging Out
- **Command:** `/logout` or press the **Logout** button on the main menu.
- **What it does:** Terminates the active session on Samvidha and clears temporary session cookies.

---

## Reporting Issues & Getting Help

Encountered a bug, incorrect data, or have a suggestion for improvement? Use the built-in ticketing system:

```text
/report <your issue or feedback>
```

**Example:**
```text
/report My attendance for Machine Learning lab is not updating since yesterday.
```

- **Timestamped in IST:** Your report is recorded with the exact submission time in Indian Standard Time (`Asia/Kolkata`).
- **Direct Maintainer Reply:** When an admin or maintainer reviews your ticket, you will receive an instant notification in Telegram containing their response and the resolution timestamp.

---

## Guide for Maintainers & Admins

Privileged roles ensure smooth operation, user assistance, and platform hygiene.

### Admin & Maintainer Panels
- `/admin` — Opens the full administrative dashboard (Developers & Admins).
- `/maintainer` — Opens the operational support dashboard (Maintainers).

---

### Adding New Maintainers (Forward Method)
Admins can appoint new maintainers effortlessly without looking up complex Telegram IDs:
1. Ask the student who is to become a maintainer to send you any message in Telegram.
2. **Forward that message directly to the bot** in your private chat with the bot.
3. The bot inspects the forwarded message, extracts the user's name and ID, and displays an inline confirmation:
   > *"Would you like to add [Student Name] as Maintainer?"*
   > `[ Confirm Add ]` `[ Cancel ]`
4. Tap **Confirm Add**. The user is immediately granted maintainer permissions and receives a welcoming alert.

*(Alternative command: `/add_maintainer <chat_id> [name]`)*

---

### Reviewing & Replying to Reports
- `/rshow` — Displays a queue of unhandled student reports along with unique Report IDs.
- `/reply <reply text>` — Reply directly to a user's report by **replying (quote-replying)** to the report message in Telegram.
  - The student immediately receives the answer in their private chat.
  - The database saves the reply date & maintainer name in IST.
- `/rclear` — Purges processed reports from the pending queue.

---

### Broadcasting Announcements
Need to alert all students about scheduled portal downtime, exam dates, or bot updates?
```text
/announce <Announcement Message>
```
- **FloodWait & Rate-Limit Protection:** Broadcasts are distributed across an intelligent worker pool capped at ~25 messages/second with automated exponential backoff on HTTP 429 to keep the bot token safe from Telegram limits.
- Real-time progress indicators keep the admin updated on total sent, remaining, and failed deliveries.

---

### User Analytics & Access Control
- `/lusers` — Lists currently active logged-in sessions for inspection.
- `/tusers` — Summarizes total registered users in the past 24 hours.
- `/ban <username or chat_id>` — Restricts a malicious or unauthorized user.
- `/unban <username or chat_id>` — Restores bot access for a previously restricted user.
- `/reset` — Flushes local transient SQLite session caches without affecting permanent credentials.

---

## AI Agent Integration (MCP Server)

IARE-Bot includes a native **Model Context Protocol (MCP)** server (`iare_mcp_server.py`). This allows modern AI assistants (such as Cursor, Claude Desktop, or Antigravity) to act as administrative co-pilots:

### Capabilities available to AI Agents:
1. `check_portal_status`: Probes Samvidha portal health and response latency.
2. `get_reports_summary`: Summarizes unresolved student support issues.
3. `send_reply`: Sends maintainer replies to students on behalf of admins.
4. `draft_announcement`: Drafts structured broadcast notices.
5. `broadcast_announcement`: Transmits announcements with confirmation tokens.
6. `read_recent_errors`: Reads and diagnoses recent server exceptions.

To learn how to connect your AI assistant, see [HOW_TO_CONNECT_MCP.md](file:///d:/IARE-BOT-V5.2/Project%20Documents/HOW_TO_CONNECT_MCP.md) and [MCP_SPECIFICATION.md](file:///d:/IARE-BOT-V5.2/Project%20Documents/MCP_SPECIFICATION.md).

---

## Running the Bot Locally (For Developers)

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12
- Telegram API Credentials from [my.telegram.org](https://my.telegram.org)
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- (Optional) PostgreSQL database for persistent cloud sync

### 2. Installation
Clone the repository and install required Python packages:
```bash
git clone https://github.com/Skullkick/IARE-BOT-V5.2
cd IARE-BOT-V5.2
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file or export the required keys:
```env
API_ID=12345678
API_HASH=abcdef0123456789abcdef0123456789
BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ
DEVELOPER_CHAT_ID=1122334455
MAINTAINER_CHAT_ID=1122334455
ADMIN_AUTHORIZATION_PASS=secret_code_here
ENCRYPTION_KEY=your_custom_aes_hex_key_here

# Optional: Background MCP Server
ENABLE_MCP_SERVER=true
MCP_PASSWORD=your_mcp_security_password
```

### 4. Run the Bot
```bash
python main.py
```

### 5. Running Automated Tests
The project features a comprehensive test suite covering security, parsing, rate-limiting, and MCP tools:
```bash
python -m pytest
```

---

## Frequently Asked Questions (FAQ)

#### Q1: Why does `/login` say "Invalid credentials"?
- Double-check that your Samvidha password is correct by trying it on the web portal.
- If your password has spaces, make sure you put it inside double quotes: `/login 21951A0501 "pass with space"`.
- Verify that Samvidha is currently reachable (the college server occasionally undergoes maintenance late at night).

#### Q2: Is my password safe?
- Yes. Credentials stored in the bot are encrypted using AES-256 with key derivation. Passwords are never stored in plain text and are only decrypted in memory when authenticating with Samvidha.

#### Q3: Why is the Bunk calculation different for my friend?
- The bunk calculation depends on your personal **Attendance Threshold** configured in `/settings`. If your threshold is set to 75% and your friend's is set to 80%, the number of classes you can miss will differ.

#### Q4: Why did my uploaded lab PDF say it was compressed?
- Samvidha restricts individual PDF file sizes. When you upload a file larger than 1MB, IARE Bot automatically applies image downsampling and optimization so that your upload succeeds seamlessly without manual editing.

#### Q5: Who can I contact if the bot is down?
- Send `/report <message>` if the bot is responding, or contact the bot maintainers listed in the `/start` greeting.
