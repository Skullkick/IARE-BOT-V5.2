"""
IARE-BOT Model Context Protocol (MCP) Server.

Provides an isolated, deterministic tool interface for autonomous agents
(e.g., Hermes Agent, Claude, or custom MCP clients) to inspect bot health,
diagnose college portal status, query reports, and execute non-conversational
one-shot ticket resolutions.

Architecture:
- Standalone process: completely decoupled from Pyrogram bot event loop to avoid
  RAM bloat and garbage collection pauses on constrained dynos.
- Direct Telegram Bot API integration: send_reply uses non-blocking HTTP requests
  to dispatch messages without needing the Pyrogram client instance.
- Concurrency protection: verifies ticket pending state before dispatching
  to prevent duplicate responses when maintainers resolve tickets in parallel.
"""

import os
import sys
import time
import asyncio
import sqlite3
import logging
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv
load_dotenv()

import httpx
import psutil

try:
    from mcp.server.mcpserver import MCPServer
except ImportError:
    from mcp.server.fastmcp import FastMCP as MCPServer

from DATABASE import tdatabase, pgdatabase, managers_handler, user_settings

logger = logging.getLogger("iare_mcp_server")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Initialize MCP Server
mcp = MCPServer("IARE-BOT-MCP-Server")

DEFAULT_SAMVIDHA_URL = "https://samvidha.iare.ac.in/index"
DEFAULT_ERRORS_LOG = "bot_errors.log"


@mcp.tool()
async def check_portal_status(portal_url: str = DEFAULT_SAMVIDHA_URL) -> Dict[str, Any]:
    """
    Deterministic health check for the college Samvidha portal.
    Measures HTTP status, latency, and detects server downtime or gateway timeouts.
    """
    start_time = time.perf_counter()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0, connect=3.0), follow_redirects=True) as client:
            resp = await client.get(portal_url, headers=headers)
            latency = int((time.perf_counter() - start_time) * 1000)
            is_online = resp.status_code == 200
            return {
                "online": is_online,
                "status_code": resp.status_code,
                "latency_ms": latency,
                "error": None if is_online else f"HTTP {resp.status_code}"
            }
    except httpx.TimeoutException:
        latency = int((time.perf_counter() - start_time) * 1000)
        return {
            "online": False,
            "status_code": 504,
            "latency_ms": latency,
            "error": "Portal timed out (server overload or maintenance)"
        }
    except Exception as exc:
        latency = int((time.perf_counter() - start_time) * 1000)
        return {
            "online": False,
            "status_code": 0,
            "latency_ms": latency,
            "error": f"Connection failed: {str(exc)}"
        }


@mcp.tool()
async def get_pending_reports(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetches unresolved student reports from the reports database.
    Returns structured ticket metadata (unique_id, username, message, chat_id).
    """
    raw_reports = await tdatabase.load_allreports()
    results = []
    for r in (raw_reports or [])[:limit]:
        # pending_reports format: (unique_id, user_id, message, chat_id, replied_message, replied_maintainer, reply_status)
        results.append({
            "report_id": str(r[0]),
            "username": str(r[1]) if r[1] else "Unknown",
            "report_text": str(r[2]) if r[2] else "",
            "chat_id": int(r[3]) if r[3] else 0,
            "reply_status": int(r[6]) if len(r) > 6 and r[6] is not None else 0
        })
    return results


@mcp.tool()
async def send_reply(report_id: str, resolution_text: str) -> Dict[str, Any]:
    """
    Sends an official resolution message to the student who submitted the report.
    Non-conversational: only call this tool when a concrete, verified solution exists.
    Verifies ticket status before sending to prevent duplicate responses if an admin
    has already resolved the ticket.
    """
    if not resolution_text or not resolution_text.strip():
        return {"success": False, "status": "invalid_input", "reason": "Resolution text cannot be empty."}

    # 1. Check if report exists
    report = await tdatabase.load_reports(report_id)
    if not report:
        return {"success": False, "status": "not_found", "reason": f"Report ID '{report_id}' not found."}

    # report: (unique_id, user_id, message, chat_id, replied_message, replied_maintainer, reply_status)
    username = report[1] or "user"
    user_chat_id = report[3]
    reply_status = report[6]

    # 2. Concurrency check: has an admin or another agent already replied?
    if reply_status == 1 or reply_status is True:
        return {
            "success": False,
            "status": "already_resolved",
            "reason": f"Report '{report_id}' has already been resolved."
        }

    # 3. Format clean, formal, non-conversational message
    clean_resolution = resolution_text.strip()
    formatted_message = (
        f"📋 **Report Resolution (ID: {report_id})**\n\n"
        f"{clean_resolution}\n\n"
        f"────────────────────\n"
        f"*(Note: Your ticket is logged with bot developers if further help is needed.)*"
    )

    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token:
        # In testing or staging where BOT_TOKEN may not be provided, return simulation
        logger.warning("BOT_TOKEN environment variable not set. Simulating message dispatch.")
        await tdatabase.store_reports(report_id, None, None, None, clean_resolution, "AI Assistant", 1)
        try:
            await pgdatabase.store_reports(report_id, None, None, None, clean_resolution, "AI Assistant", True)
        except Exception:
            pass
        return {
            "success": True,
            "report_id": report_id,
            "status": "resolved",
            "simulated": True,
            "sent_to_chat_id": user_chat_id
        }

    telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Send resolution to the student
        try:
            resp = await client.post(
                telegram_url,
                json={"chat_id": user_chat_id, "text": formatted_message, "parse_mode": "Markdown"},
                headers=headers
            )
            if resp.status_code != 200:
                logger.error(f"Telegram API error when sending to {user_chat_id}: {resp.text}")
                return {
                    "success": False,
                    "status": "telegram_error",
                    "reason": f"Telegram API returned status {resp.status_code}: {resp.text}"
                }
        except Exception as exc:
            logger.error(f"Network failure calling Telegram API: {exc}")
            return {
                "success": False,
                "status": "network_error",
                "reason": f"Failed to reach Telegram API: {str(exc)}"
            }

        # 4. Mark report resolved in SQLite and Postgres
        await tdatabase.store_reports(report_id, None, None, None, clean_resolution, "AI Assistant", 1)
        try:
            await pgdatabase.store_reports(report_id, None, None, None, clean_resolution, "AI Assistant", True)
        except Exception as pg_err:
            logger.warning(f"Postgres update skipped or failed: {pg_err}")

        # 5. Notify maintainers and admins
        try:
            admin_ids = await managers_handler.fetch_admin_chat_ids() or []
            maintainer_ids = await managers_handler.fetch_maintainer_chat_ids() or []
            all_managers = list(set(admin_ids + maintainer_ids))
            admin_notice = (
                f"🤖 **Report {report_id} Auto-Resolved by AI**\n\n"
                f"**User:** @{username} (`{user_chat_id}`)\n"
                f"**Resolution:**\n{clean_resolution}"
            )
            for m_id in all_managers:
                try:
                    await client.post(
                        telegram_url,
                        json={"chat_id": m_id, "text": admin_notice, "parse_mode": "Markdown"},
                        headers=headers
                    )
                except Exception:
                    pass
        except Exception as notify_err:
            logger.warning(f"Could not notify managers: {notify_err}")

    return {
        "success": True,
        "report_id": report_id,
        "status": "resolved",
        "sent_to_chat_id": user_chat_id
    }


@mcp.tool()
async def read_recent_errors(lines: int = 50, user_chat_id: Optional[int] = None, log_file: str = DEFAULT_ERRORS_LOG) -> List[str]:
    """
    Reads the tail of bot_errors.log, optionally filtering by a specific student's chat_id.
    Enables root-cause diagnosis without loading entire log files into memory.
    """
    if not os.path.exists(log_file):
        return [f"Log file '{log_file}' does not exist."]

    matched_lines = []
    try:
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
            tail_lines = all_lines[-max(1, lines * 3):]
            for line in reversed(tail_lines):
                if user_chat_id is not None:
                    if str(user_chat_id) in line:
                        matched_lines.append(line.rstrip())
                else:
                    matched_lines.append(line.rstrip())
                if len(matched_lines) >= lines:
                    break
        matched_lines.reverse()
        return matched_lines if matched_lines else ["No matching error entries found."]
    except Exception as exc:
        return [f"Error reading log file: {str(exc)}"]


@mcp.tool()
async def get_system_health() -> Dict[str, Any]:
    """
    Returns server CPU, RAM, and disk utilization metrics via psutil.
    Assists in detecting resource starvation or memory pressure.
    """
    try:
        cpu_pct = psutil.cpu_percent(interval=0.2)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        return {
            "cpu_percent": round(cpu_pct, 1),
            "memory_used_mb": round(mem.used / (1024 * 1024), 1),
            "memory_total_mb": round(mem.total / (1024 * 1024), 1),
            "memory_percent": round(mem.percent, 1),
            "disk_percent": round(disk.percent, 1)
        }
    except Exception as exc:
        return {"error": str(exc)}


@mcp.tool()
async def get_user_profile_context(chat_id: int) -> Dict[str, Any]:
    """
    Retrieves student identity, active session status, and account standing
    from the local database to give context to support investigations.
    """
    user_row = await tdatabase.load_username(chat_id)
    session_data = await tdatabase.load_user_session(chat_id)
    username = user_row[2] if user_row and len(user_row) > 2 else None

    is_banned = False
    if username:
        is_banned = await tdatabase.get_bool_banned_username(username.lower())

    return {
        "chat_id": chat_id,
        "username": username or "Not Registered",
        "has_active_session": session_data is not None,
        "is_banned": bool(is_banned)
    }


async def _get_recipient_chat_ids(target: str = "admins") -> List[int]:
    """Fetch unique chat IDs for broadcast targeting."""
    admin_ids = await managers_handler.fetch_admin_chat_ids() or []
    maintainer_ids = await managers_handler.fetch_maintainer_chat_ids() or []
    manager_ids = list(set(admin_ids + maintainer_ids))

    if target == "admins":
        return manager_ids

    # For target == "all", combine Postgres with local SQLite fallback
    all_cids = set(manager_ids)
    try:
        pg_cids = await pgdatabase.get_all_chat_ids()
        if pg_cids:
            all_cids.update(pg_cids)
    except Exception as exc:
        logger.warning(f"Could not fetch chat_ids from Postgres: {exc}")

    # Fallback to local sessions / credentials if SQLite has chat_ids
    try:
        with sqlite3.connect(tdatabase.DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id FROM sessions")
            for row in cursor.fetchall():
                if row[0]:
                    all_cids.add(int(row[0]))
    except Exception:
        pass

    try:
        with sqlite3.connect(tdatabase.CREDENTIALS_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id FROM credentials")
            for row in cursor.fetchall():
                if row[0]:
                    all_cids.add(int(row[0]))
    except Exception:
        pass

    return list(all_cids)


@mcp.tool()
async def draft_announcement(raw_text: str, send_preview: bool = True) -> Dict[str, Any]:
    """
    Formats raw announcement text into Telegram-ready dual-UI templates
    (monospace code block for updated_ui and markdown for traditional_ui).
    Optionally dispatches a test preview to maintainers/admins before any broadcast.
    """
    if not raw_text or not raw_text.strip():
        return {"success": False, "status": "invalid_input", "reason": "Announcement text cannot be empty."}

    text = raw_text.strip()
    msg_updated_ui = f"```ANNOUNCEMENT\n{text}\n```"
    msg_traditional_ui = f"**ANNOUNCEMENT**\n\n{text}"

    preview_sent = False
    admin_ids = await managers_handler.fetch_admin_chat_ids() or []
    maintainer_ids = await managers_handler.fetch_maintainer_chat_ids() or []
    all_managers = list(set(admin_ids + maintainer_ids))

    bot_token = os.environ.get("BOT_TOKEN")
    if send_preview and all_managers:
        if not bot_token:
            logger.info("Simulating announcement preview dispatch (no BOT_TOKEN set).")
            preview_sent = True
        else:
            preview_msg = f"📢 **[ANNOUNCEMENT PREVIEW - NOT SENT TO USERS]**\n\n{msg_traditional_ui}"
            telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            async with httpx.AsyncClient(timeout=10.0) as client:
                for admin_id in all_managers:
                    try:
                        await client.post(
                            telegram_url,
                            json={"chat_id": admin_id, "text": preview_msg, "parse_mode": "Markdown"}
                        )
                    except Exception as e:
                        logger.warning(f"Could not send preview to {admin_id}: {e}")
            preview_sent = True

    return {
        "success": True,
        "formatted_updated_ui": msg_updated_ui,
        "formatted_traditional_ui": msg_traditional_ui,
        "preview_sent_to_managers": preview_sent,
        "manager_recipients_count": len(all_managers)
    }


@mcp.tool()
async def broadcast_announcement(
    announcement_text: str,
    target: str = "admins",
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Broadcasts an announcement to users using an asynchronous queue worker engine.
    - target='admins' (Default/Safe): Broadcasts only to bot admins and maintainers.
    - target='all': Broadcasts to all registered students and managers.
    Adapts the battle-tested worker pool and FloodWait/429 retry architecture from manager_operations.py.
    """
    if not announcement_text or not announcement_text.strip():
        return {"status": "error", "reason": "Announcement text cannot be empty."}

    if target not in ("admins", "all"):
        return {"status": "error", "reason": f"Invalid target '{target}'. Must be 'admins' or 'all'."}

    chat_ids = await _get_recipient_chat_ids(target=target)
    total_users = len(chat_ids)
    if total_users == 0:
        return {"status": "no_recipients", "total_recipients": 0, "successful": 0, "failed": 0}

    text = announcement_text.strip()
    msg_updated_ui = f"```ANNOUNCEMENT\n{text}\n```"
    msg_traditional_ui = f"**ANNOUNCEMENT**\n\n{text}"

    bot_token = os.environ.get("BOT_TOKEN")
    start_time = time.perf_counter()

    # In simulated / test mode (no token set)
    if not bot_token:
        logger.info(f"Simulating broadcast to {total_users} recipients (target={target}).")
        duration = round(time.perf_counter() - start_time, 2)
        return {
            "status": "completed",
            "simulated": True,
            "target": target,
            "total_recipients": total_users,
            "successful": total_users,
            "failed": 0,
            "duration_seconds": duration,
            "reason": reason
        }

    queue: asyncio.Queue = asyncio.Queue()
    for cid in chat_ids:
        await queue.put(cid)

    successful = 0
    failed = 0
    telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    WORKERS = min(12, max(1, total_users))
    DELAY = 0.05  # Controlled pacing between worker sends

    async with httpx.AsyncClient(timeout=10.0) as client:
        async def worker():
            nonlocal successful, failed
            while True:
                cid = await queue.get()
                if cid is None:
                    queue.task_done()
                    break

                try:
                    ui_mode = None
                    try:
                        ui_mode = await user_settings.fetch_ui_bool(cid)
                    except Exception:
                        pass
                    send_text = msg_traditional_ui if ui_mode and ui_mode[0] == 1 else msg_updated_ui

                    resp = await client.post(
                        telegram_url,
                        json={"chat_id": cid, "text": send_text, "parse_mode": "Markdown"}
                    )

                    if resp.status_code == 200:
                        successful += 1
                        await asyncio.sleep(DELAY)
                    elif resp.status_code == 429:
                        # Telegram FloodWait backoff
                        retry_after = 5
                        try:
                            retry_after = int(resp.json().get("parameters", {}).get("retry_after", 5))
                        except Exception:
                            pass
                        logger.warning(f"Telegram FloodWait encountered for chat {cid}. Sleeping {retry_after}s.")
                        await asyncio.sleep(retry_after)
                        await queue.put(cid)  # Put back in queue to retry
                    else:
                        logger.warning(f"Failed sending announcement to {cid}: HTTP {resp.status_code}")
                        failed += 1
                except Exception as exc:
                    logger.error(f"Error sending announcement to {cid}: {exc}")
                    failed += 1
                finally:
                    queue.task_done()

        tasks = [asyncio.create_task(worker()) for _ in range(WORKERS)]
        await queue.join()
        for _ in range(WORKERS):
            await queue.put(None)
        await asyncio.gather(*tasks)

        duration = round(time.perf_counter() - start_time, 2)

        # Notify managers when a full broadcast completes
        if target == "all":
            admin_ids = await managers_handler.fetch_admin_chat_ids() or []
            maintainer_ids = await managers_handler.fetch_maintainer_chat_ids() or []
            all_managers = list(set(admin_ids + maintainer_ids))
            summary_notice = (
                f"📢 **Broadcast Completed by AI**\n\n"
                f"● **Target:** `{target}`\n"
                f"● **Total:** {total_users}\n"
                f"● **Successful:** {successful}\n"
                f"● **Failed:** {failed}\n"
                f"● **Duration:** {duration}s\n"
                f"● **Reason:** {reason or 'Not Specified'}"
            )
            for m_id in all_managers:
                try:
                    await client.post(telegram_url, json={"chat_id": m_id, "text": summary_notice, "parse_mode": "Markdown"})
                except Exception:
                    pass

    return {
        "status": "completed",
        "target": target,
        "total_recipients": total_users,
        "successful": successful,
        "failed": failed,
        "duration_seconds": duration,
        "reason": reason
    }


def main():
    """Main entrypoint when launched as a standalone MCP server."""
    logger.info("Starting IARE-BOT MCP Server over stdio transport...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
