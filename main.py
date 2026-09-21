"""
IARE-BOT main entrypoint.

This module wires Pyrogram command and callback handlers, initializes
databases, and starts the bot. It also configures basic error logging.

Environment variables required:
- BOT_TOKEN: Telegram bot token
- API_ID: Telegram API ID
- API_HASH: Telegram API hash

Run: Executed directly, it schedules `main()` and calls `bot.run()`.
"""

import asyncio, os, sys, subprocess, atexit, time, logging
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

from pyrogram import Client, filters, errors
from pyrogram.errors import FloodWait
from DATABASE import tdatabase, pgdatabase, user_settings, managers_handler
from METHODS import labs_handler, operations, manager_operations, lab_operations, pdf_compressor
from Buttons import buttons, manager_buttons

def _clean_env(val):
    if val is None:
        return None
    cleaned = str(val).strip().strip('"').strip("'")
    return cleaned if cleaned else None

BOT_TOKEN = _clean_env(os.environ.get("BOT_TOKEN"))
API_ID_RAW = _clean_env(os.environ.get("API_ID"))
API_HASH = _clean_env(os.environ.get("API_HASH"))
API_ID = int(API_ID_RAW) if (API_ID_RAW and API_ID_RAW.isdigit()) else API_ID_RAW

bot = Client(
    "IARE BOT",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_errors.log"),
        logging.StreamHandler()
    ]
)
@bot.on_message(filters.command(commands=['start']))
async def _start(bot,message):
    """Handle /start command.

    Sends a random greeting and initial help to the user.

    Args:
        bot: Pyrogram client instance.
        message: Incoming message carrying chat/user context.
    """
    try:
        await operations.get_random_greeting(bot, message)
    except Exception as e:
        logging.error("Error in 'start' command: %s", e)

@bot.on_message(filters.command(commands=['login']))
async def _login(bot,message):
    """Handle /login command.

    Triggers the login flow handled in `operations.login`.

    Args:
        bot: Pyrogram client instance.
        message: Incoming message with user context.
    """
    try:
        await operations.login(bot, message)
    except Exception as e:
        logging.error("Error in 'login' command: %s", e)
@bot.on_message(filters.command(commands=['logout']))
async def _logout(bot,message):
    """Handle /logout command to clear current session."""
    try:
        await operations.logout(bot, message)
    except Exception as e:
        logging.error("Error in 'logout' command: %s", e)

@bot.on_message(filters.command(commands=['report']))
async def _report(bot,message):
    """Handle /report command to submit a report/request."""
    try:
        await operations.report(bot, message)
    except Exception as e:
        logging.error("Error in 'report' command: %s", e)
@bot.on_message(filters.command(commands=['help', 'guide']))
async def _help(bot,message):
    """Handle /help and /guide commands to show interactive protected user guide."""
    try:
        await operations.help_command(bot, message)
    except Exception as e:
        logging.error("Error in 'help' command: %s", e)
@bot.on_message(filters.command(commands="settings"))
async def settings_buttons(bot,message):
    """Handle /settings command.

    Ensures user settings exist, then shows interactive settings buttons.
    """
    # Initializes settings for the user
    chat_id = message.chat.id
    try:
        if await user_settings.fetch_user_settings(chat_id) is None:
            await user_settings.set_user_default_settings(chat_id)
        await buttons.start_user_settings(bot, message)
    except Exception as e:
        logging.error("Error in 'settings' command: %s", e)

# @bot.on_message(filters.command(commands=['attendance']))
async def _attendance(bot,message):
    await operations.attendance(bot,message)
    await buttons.start_user_buttons(bot,message)
# @bot.on_message(filters.command(commands=['biometric']))
async def _biometric(bot,message):
    await operations.biometric(bot,message)
    await buttons.start_user_buttons(bot,message)
# @bot.on_message(filters.command(commands=['bunk']))
async def _bunk(bot,message):
    await operations.bunk(bot,message)
    await buttons.start_user_buttons(bot,message)
# @bot.on_message(filters.command(commands=['profile']))
async def _profile_details(bot,message):
    await operations.profile_details(bot,message)
# @bot.on_message(filters.command(commands=['del_save']))
async def delete_login_details_pgdatabase(bot,message):
    chat_id = message.chat.id
    await pgdatabase.remove_saved_credentials(bot,chat_id)
@bot.on_message(filters.command(commands=["cancel", "abort"]))
async def _cancel_command(bot, message):
    """Handle /cancel or /abort command to cancel any pending lab upload or operation."""
    chat_id = message.chat.id
    await labs_handler.remove_pdf_file(bot, chat_id)
    try:
        await tdatabase.delete_lab_upload_data(chat_id)
        await tdatabase.delete_pdf_status_info(chat_id)
        await tdatabase.delete_title_status_info(chat_id)
        pdf_compressor.clear_compression_metrics(chat_id)
    except Exception:
        pass
    await bot.send_message(chat_id, "🚫 **Operation Cancelled**\n\nAny pending upload was aborted and temporary files have been deleted.")
    await buttons.start_user_buttons(bot, message)

@bot.on_message(filters.command(commands=["deletepdf", "delpdf"]))
async def delete_pdf(bot, message):
    chat_id = message.chat.id
    if await labs_handler.remove_pdf_file(bot, chat_id) is True:
        try:
            await tdatabase.delete_pdf_status_info(chat_id)
            await tdatabase.delete_title_status_info(chat_id)
            pdf_compressor.clear_compression_metrics(chat_id)
        except Exception:
            pass
        await bot.send_message(chat_id, "Deleted Successfully")
    else:
        await bot.send_message(chat_id, "Failed")
@bot.on_message(filters.command(commands=['reply']))
async def _reply(bot,message):
    """Handle /reply command for maintainers/admins to reply to reports."""
    try:
        await operations.reply_to_user(bot, message)
    except Exception as e:
        logging.error("Error in 'reply' command: %s", e)
@bot.on_message(filters.command(commands=['rshow']))
async def _show_requests(bot,message):
    """Handle /rshow command to list pending user reports."""
    try:
        await operations.show_reports(bot, message)
    except Exception as e:
        logging.error("Error in 'rshow' command: %s", e)

@bot.on_message(filters.command(commands=['announce']))
async def _announce(bot,message):
    """Handle /announce command to broadcast a message to all users."""
    try:
        await manager_operations.announcement_to_all_users(bot, message)
    except Exception as e:
        logging.error("Error in 'announce' command: %s", e)

@bot.on_message(filters.command(commands=['lusers']))
async def _users_list(bot,message):
    """Handle /lusers command to list logged-in users for this chat."""
    try:
        await operations.list_users(bot, message.chat.id)
    except Exception as e:
        logging.error("Error in 'lusers' command: %s", e)
@bot.on_message(filters.command(commands=['tusers']))
async def _total_users(bot,message):
    """Handle /tusers command to show total users stats."""
    try:
        await operations.total_users(bot, message)
    except Exception as e:
        logging.error("Error in 'tusers' command: %s", e)
@bot.on_message(filters.command(commands=['rclear']))
async def _clear_requests(bot,message):
    """Handle /rclear command to purge pending reports queue."""
    try:
        await operations.clean_pending_reports(bot, message)
    except Exception as e:
        logging.error("Error in 'rclear' command: %s", e)
@bot.on_message(filters.command(commands=['reset']))
async def _reset_sqlite(bot,message):
    """Handle /reset command to reset user sessions database."""
    try:
        await operations.reset_user_sessions_database(bot, message)
    except Exception as e:
        logging.error("Error in 'reset' command: %s", e)
# @bot.on_message(filters.command(commands=["pgtusers"]))
async def _total_users_pg_database(bot,message):
    chat_id = message.chat.id
    await pgdatabase.total_users_pg_database(bot,chat_id)
@bot.on_message(filters.command(commands="admin"))
async def admin_buttons(bot,message):
    """Handle /admin command.

    Shows admin control panel if the user is an admin.
    """
    chat_id = message.chat.id
    try:
        admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
        if chat_id in admin_chat_ids:
            await manager_buttons.start_admin_buttons(bot, message)
    except Exception as e:
        logging.error("Error in 'admin' command: %s", e)

@bot.on_message(filters.command(commands="maintainer"))
async def maintainer_buttons(bot,message):
    """Handle /maintainer command to show maintainer options."""
    try:
        await manager_buttons.start_maintainer_button(bot, message)
    except Exception as e:
        logging.error("Error in 'maintainer' command: %s", e)

@bot.on_message(filters.command(commands=["stats", "server_stats", "serverstats"]))
async def server_stats_command(bot, message):
    """Handle /stats and /server_stats commands for admins and maintainers."""
    chat_id = message.chat.id
    try:
        admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
        maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
        if chat_id in admin_chat_ids or chat_id in maintainer_chat_ids:
            ui_mode = await user_settings.fetch_ui_bool(chat_id)
            is_traditional = bool(ui_mode and ui_mode[0] == 1)
            stats_text = await manager_operations.get_server_stats(traditional_ui=is_traditional)
            await message.reply_text(stats_text)
    except Exception as e:
        logging.error("Error in 'stats' command: %s", e)
@bot.on_message(filters.command(commands="ban"))
async def ban_username(bot,message):
    """Handle /ban command to ban a username/user id."""
    try:
        await manager_operations.ban_username(bot, message)
    except Exception as e:
        logging.error("Error in 'ban' command: %s", e)

@bot.on_message(filters.command(commands="unban"))
async def unban_username(bot,message):
    """Handle /unban command to remove a ban for a user."""
    try:
        await manager_operations.unban_username(bot, message)
    except Exception as e:
        logging.error("Error in 'unban' command: %s", e)

@bot.on_message(filters.command(commands="authorize"))
async def authorize_and_add_admin(bot,message):
    """Handle /authorize command to add an admin after verification."""
    try:
        await manager_operations.add_admin_by_authorization(bot, message)
    except Exception as e:
        logging.error("Error in 'authorize' command: %s", e)
@bot.on_message(filters.command(commands="add_maintainer"))
async def add_maintainer(bot, message):
    try:
        # Trigger verification flow to add maintainer
        await manager_operations.verification_to_add_maintainer(bot, message)
    except Exception as e:
        logging.error("Error in 'add_maintainer' command: %s", e)

@bot.on_message(filters.private & (filters.forwarded | filters.contact) & ~filters.command(commands="add_maintainer"))
async def forwarded_message_from_admin(bot, message):
    """Handle forwarded messages and contacts sent by an admin/maintainer in private chat to initiate maintainer verification."""
    try:
        chat_id = message.chat.id
        caller_id = chat_id
        if getattr(message, "from_user", None) and getattr(message.from_user, "id", None) and isinstance(message.from_user.id, int):
            caller_id = message.from_user.id

        admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
        maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()

        is_admin = (chat_id in admin_chat_ids) or (caller_id in admin_chat_ids)
        is_authorized_maintainer = False
        for mid in (caller_id, chat_id):
            if mid in maintainer_chat_ids:
                access_data = await managers_handler.get_access_data(mid)
                if access_data and len(access_data) > 8 and access_data[8] == 1:
                    is_authorized_maintainer = True
                    break

        if is_admin or is_authorized_maintainer:
            # If admin is in the middle of a lab upload flow, let lab title handler take precedence
            try:
                status = await tdatabase.fetch_title_status(message.chat.id)
                if status is not None and int(status) == 1 and message.text and "TITLE" in message.text.upper():
                    return
            except Exception:
                pass
            await manager_operations.verification_to_add_maintainer(bot, message)
    except Exception as e:
        logging.error("Error in 'forwarded_message_from_admin' handler: %s", e)

@bot.on_message(filters.private & filters.document)
async def _download_pdf(bot,message):
    """Handle private document messages to ingest PDFs for lab uploads."""
    try:
        await labs_handler.download_pdf(bot, message, pdf_compress_scrape=pdf_compressor.use_pdf_compress_scrape)
    except Exception as e:
        logging.error("Error in '_download_pdf' function: %s", e)


@bot.on_message(filters.private & ~filters.service)
async def _get_title_from_user(bot,message):
    """Handle private text messages to capture PDF titles from users."""
    try:
        if message.text:
            await labs_handler.get_title_from_user(bot, message)
    except Exception as e:
        logging.error("Error in '_get_title_from_user' function: %s", e)
            
@bot.on_callback_query()
async def _callback_function(bot,callback_query):
    """Route callback queries to user or manager button handlers.

    If callback data contains "manager", routes to manager buttons; otherwise
    to general user buttons.
    """
    try:
        if "manager" in callback_query.data:
            await manager_buttons.manager_callback_function(bot, callback_query)
        else:
            await buttons.callback_function(bot, callback_query)
    except Exception as e:
        logging.error("Error in '_callback_function': %s", e)

_MCP_PROCESS = None

def start_mcp_server_if_enabled():
    """Start iare_mcp_server as a background subprocess if ENABLE_MCP_SERVER is set to true."""
    global _MCP_PROCESS
    enable_flag = os.environ.get("ENABLE_MCP_SERVER", "").strip().lower()
    if enable_flag not in ("1", "true", "yes", "on"):
        logging.info("MCP server is disabled (ENABLE_MCP_SERVER is not set to true).")
        return None

    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "iare_mcp_server.py")
    try:
        _MCP_PROCESS = subprocess.Popen([sys.executable, script_path], env=os.environ.copy())
        logging.info("Started background MCP server subprocess (PID: %d)", _MCP_PROCESS.pid)
        return _MCP_PROCESS
    except Exception as exc:
        logging.error("Failed to start background MCP server: %s", exc, exc_info=True)
        return None

def stop_mcp_server():
    """Terminate the background MCP server subprocess on bot shutdown."""
    global _MCP_PROCESS
    if _MCP_PROCESS and _MCP_PROCESS.poll() is None:
        logging.info("Shutting down background MCP server (PID: %d)...", _MCP_PROCESS.pid)
        _MCP_PROCESS.terminate()
        try:
            _MCP_PROCESS.wait(timeout=3)
        except subprocess.TimeoutExpired:
            _MCP_PROCESS.kill()
        _MCP_PROCESS = None

_HEALTHCHECK_SERVER = None

async def start_healthcheck_server(port: int = 3000):
    """Start an async HTTP health check server for Docker, Coolify, and container health checks."""
    global _HEALTHCHECK_SERVER

    async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            request_line = await reader.readline()
            while True:
                line = await reader.readline()
                if not line or line in (b"\r\n", b"\n"):
                    break

            body = b'{"status":"healthy","service":"IARE-BOT"}\n'
            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: application/json\r\n"
                b"Content-Length: " + str(len(body)).encode("ascii") + b"\r\n"
                b"Connection: close\r\n"
                b"\r\n" + body
            )
            writer.write(response)
            await writer.drain()
        except Exception:
            pass
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    try:
        _HEALTHCHECK_SERVER = await asyncio.start_server(handle_client, "0.0.0.0", port)
        print(f"[INFO] HTTP Healthcheck server listening on port {port} (status: 200 OK)")
        return _HEALTHCHECK_SERVER
    except Exception as exc:
        logging.warning("Could not start HTTP healthcheck server on port %d: %s", port, exc)
        return None

async def main(bot):
    """Application bootstrap.

    Creates required tables across storage backends and synchronizes state
    between them on startup.
    """
    try:
        # 1. Initialize all local SQLite databases first
        await tdatabase.create_all_tdatabase_tables()
        await user_settings.create_user_settings_tables()
        await managers_handler.create_required_bot_manager_tables()

        # 2. Connect to PostgreSQL and synchronize if available
        pg_pool = await pgdatabase.init_pg_pool()
        if pg_pool is not None:
            await pgdatabase.create_all_pgdatabase_tables()
            await operations.sync_databases(bot)
        else:
            logging.warning("PostgreSQL connection pool unavailable. Bot will operate using local SQLite storage.")
            print("[INFO] PostgreSQL unreachable. Operating with local SQLite storage.")

        # 3. Start background services & HTTP healthcheck server
        start_mcp_server_if_enabled()

        port_val = os.environ.get("PORT") or os.environ.get("HEALTHCHECK_PORT")
        if port_val and port_val.isdigit():
            port_num = int(port_val)
            mcp_enabled = os.environ.get("ENABLE_MCP_SERVER", "").strip().lower() in ("1", "true", "yes", "on")
            mcp_transport = os.environ.get("MCP_TRANSPORT", "").strip().lower()
            mcp_port = int(os.environ.get("MCP_PORT") or os.environ.get("PORT") or "8000")
            if not (mcp_enabled and mcp_transport == "sse" and mcp_port == port_num):
                await start_healthcheck_server(port_num)

        # 4. Clean up any stale PDFs (> 30 mins) and start background janitor loop
        stale_purged = labs_handler.cleanup_stale_pdfs(max_age_seconds=1800)
        if stale_purged > 0:
            logging.info("Startup sweep: purged %d stale PDF(s) older than 30 mins.", stale_purged)
        asyncio.create_task(labs_handler.start_pdf_cleanup_loop(interval_seconds=300, max_age_seconds=1800))

        print("\n" + "=" * 60)
        print(">>> IARE BOT is now ONLINE and ready to receive messages! <<<")
        print("=" * 60 + "\n")
    except Exception as e:
        logging.error("Error in 'main' function: %s", e, exc_info=True)

    # NOTE: The following code is for CGPA and CIE tracking for maintainers and admins only.
    # This feature is still under development.
    # IMPORTANT: Do NOT enable or provide this feature for all users in the future,
    # as it may significantly slow down the campus management portal.
    # while True:
    #     cgpa_tracker_chat_ids = await managers_handler.get_all_cgpa_tracker_chat_ids()
    #     cie_tracker_chat_ids = await managers_handler.get_all_cie_tracker_chat_ids()
    #     if cgpa_tracker_chat_ids:
    #         for chat_id in cgpa_tracker_chat_ids:
    #             await manager_operations.cgpa_tracker(bot, chat_id)
    #     if cie_tracker_chat_ids:
    #         for chat_id in cie_tracker_chat_ids:
    #             await manager_operations.cie_tracker(bot, chat_id)
    #     await asyncio.sleep(300)

if __name__ == "__main__":
    if not BOT_TOKEN or not API_ID or not API_HASH:
        print("\n" + "=" * 70, file=sys.stderr)
        print("CRITICAL CONFIGURATION ERROR: Telegram API credentials missing!", file=sys.stderr)
        print(f"  - BOT_TOKEN: {'SET' if BOT_TOKEN else 'MISSING / EMPTY'}", file=sys.stderr)
        print(f"  - API_ID:    {'SET' if API_ID else 'MISSING / EMPTY'}", file=sys.stderr)
        print(f"  - API_HASH:  {'SET' if API_HASH else 'MISSING / EMPTY'}", file=sys.stderr)
        print("Pyrogram requires BOT_TOKEN, API_ID, and API_HASH to start.", file=sys.stderr)
        print("Please ensure these environment variables are set in Coolify and REDEPLOY.", file=sys.stderr)
        print("=" * 70 + "\n", file=sys.stderr)
        sys.exit(1)

    loop = asyncio.get_event_loop()
    loop.create_task(main(bot))
    bot.run()
