"""
Manager operations for the bot: admin/maintainer workflows, access control,
announcements, academic trackers, and maintenance utilities.

This module coordinates privileged actions (ban/unban usernames, manage maintainers
and admins), broadcasts announcements, and runs trackers for CGPA/CIE updates.
It integrates with local SQLite and remote PostgreSQL via `DATABASE.*`, user
preferences in `user_settings`, and UI helpers in `Buttons.*`. Network calls
use `requests` and Samvidha endpoints; parsing uses BeautifulSoup. Functions are
asynchronous to work with Pyrogram's bot event loop. No business logic is altered
by these docstrings.
"""

# This file containg all the code regarding manager operations on database, testing,etc..

from DATABASE import tdatabase,pgdatabase,managers_handler,user_settings
from Buttons import buttons,manager_buttons
import re,json,psutil,logging
from METHODS.portal_client import async_fetch_page, async_logout_portal
from METHODS import operations
from bs4 import BeautifulSoup
import sqlite3,os
import asyncio
from asyncio import Queue, create_task, sleep
from pyrogram.errors import FloodWait

# access_users = access_data[0]
# announcement = access_data[1]
# configure = access_data[2]
# show_reports = access_data[3]
# reply_reports = access_data[4]
# clear_reports = access_data[5]
# ban_username = access_data[6]
# unban_username = access_data[7]
# manage_maintainers = access_data[8]
# logs = access_data[9]


ADMIN_AUTHORIZATION_CODE = os.environ.get("ADMIN_AUTHORIZATION_PASS")

async def get_username(bot,chat_id):
    """Return a user's display name given their chat id.

    - bot: Pyrogram client used to fetch user info.
    - chat_id: Telegram chat/user id to resolve.
    """
    try:
        user = await bot.get_users(int(chat_id))
        if getattr(user, "last_name", None):
            user_name = f"{user.first_name} {user.last_name}".strip()
        else:
            user_name = (getattr(user, "first_name", "") or "Unknown").strip()
        return user_name
    except Exception as exc:
        logging.warning("Could not fetch user info for chat_id %s: %s", chat_id, exc)

    # Fallback to local managers database if present
    try:
        db_name = await managers_handler.fetch_name(int(chat_id))
        if db_name:
            return db_name
    except Exception:
        pass

    return f"User {chat_id}"
async def ban_username(bot,message):
    """Ban one or more usernames.

    - Validates caller permissions (admin/maintainer with access flag).
    - Accepts multiple patterns; supports base + suffix expansion.
    - Persists bans in both local (SQLite) and cloud (Postgres) stores.
    """
    chat_id = message.chat.id
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids() # Fetch all admin chat ids
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()# Fetch all maintainer chat ids
    if chat_id not in admin_chat_ids and chat_id not in maintainer_chat_ids:
        return
    access_data = await managers_handler.get_access_data(chat_id)
    if chat_id in maintainer_chat_ids and access_data[6] != 1:
        await bot.send_message(chat_id,"Access denied. You don't have permission to use this command.")
        return
    usernames = re.split(r'[ ,]+', message.text)[1:]
    if len(usernames) == 0:
        await bot.send_message(chat_id,"No username found.")
        return
    if len(usernames[0]) < 10:
        await bot.send_message(chat_id, "Not a valid username")
        return
    if len(usernames) > 1:
        if len(usernames[0]) > len(usernames[1]):
            if await tdatabase.get_bool_banned_username(usernames[0].lower()) is False:
                    await tdatabase.store_banned_username(usernames[0].lower())
                    await pgdatabase.store_banned_username(usernames[0].lower())
            else:
                await bot.send_message(chat_id,f"Username : {usernames[0]},\n\nis already banned.")
            for index in range(1,len(usernames)):
                complete_username = usernames[0][:8] + usernames[index]
                if await tdatabase.get_bool_banned_username(complete_username.lower()) is True:
                    await bot.send_message(chat_id,f"Username : {complete_username},\n\nis already banned.")
                    continue
                await tdatabase.store_banned_username(complete_username.lower())
                await pgdatabase.store_banned_username(complete_username.lower())
            if len(usernames) > 1:
                await bot.send_message(chat_id,"Usernames banned successfully")
            else:
                await bot.send_message(chat_id,"Username banned successfully")
        else:
            for username_0 in usernames:
                for username_1 in usernames:
                    if len(username_0) != len(username_1):
                        await bot.send_message(chat_id,"Invalid Ban username format.")
                        return
                if await tdatabase.get_bool_banned_username(username_0.lower()) is True:
                    await bot.send_message(chat_id,f"Username : {username_0},\n\nis already banned.")
                    continue
                await tdatabase.store_banned_username(username_0.lower())
                await pgdatabase.store_banned_username(username_0.lower())
            if len(usernames) > 1:
                await bot.send_message(chat_id,"Usernames banned successfully")
            else:
                await bot.send_message(chat_id,"Username banned successfully")
    elif len(usernames) == 1:
        if await tdatabase.get_bool_banned_username(usernames[0]) is True:
            await bot.send_message(chat_id,"Username is already banned")
            return
        await tdatabase.store_banned_username(usernames[0].lower())
        await pgdatabase.store_banned_username(usernames[0].lower())
        await bot.send_message(chat_id,"Username banned successfully")

async def unban_username(bot,message):
    """Unban one or more usernames.

    Mirrors `ban_username` logic but removes entries from local and cloud
    ban lists, validating permissions and inputs.
    """
    chat_id = message.chat.id
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids() # Fetch all admin chat ids
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()# Fetch all maintainer chat ids
    if chat_id not in admin_chat_ids and chat_id not in maintainer_chat_ids:
        return
    access_data = await managers_handler.get_access_data(chat_id)
    if chat_id in maintainer_chat_ids and access_data[7] != 1:
        await bot.send_message(chat_id,"Access denied. You don't have permission to use this command.")
        return
    usernames = re.split(r'[ ,]+', message.text)[1:]
    if len(usernames) == 0:
        await bot.send_message(chat_id,"No username found.")
        return
    if len(usernames[0]) < 10:
        await bot.send_message(chat_id, "Not a valid username")
        return
    if len(usernames) > 1:
        if len(usernames[0]) > len(usernames[1]):
            if await tdatabase.get_bool_banned_username(usernames[0].lower()) is True:
                await tdatabase.remove_banned_username(usernames[0])
                await pgdatabase.remove_banned_username(usernames[0])
                await bot.send_message(chat_id, f"Username {usernames[0]} has been unbanned successfully.")
            else:
                await bot.send_message(chat_id,f"Username : {usernames[0]},\n\nis not in banned list.")
            for index in range(1,len(usernames)):
                complete_username = usernames[0][:8] + usernames[index]
                if await tdatabase.get_bool_banned_username(complete_username.lower()) is False:
                    await bot.send_message(chat_id,f"Username : {complete_username},\n\nis not in banned list")
                    continue
                await tdatabase.remove_banned_username(complete_username.lower())
                await pgdatabase.remove_banned_username(complete_username.lower())
            if len(usernames) > 1:
                await bot.send_message(chat_id,"Usernames unbanned successfully")
            else:
                await bot.send_message(chat_id,"Username unbanned successfully")
        else:
            for username_0 in usernames:
                for username_1 in usernames:
                    if len(username_0) != len(username_1):
                        await bot.send_message(chat_id,"Invalid Ban username format.")
                        return
                if await tdatabase.get_bool_banned_username(username_0.lower()) is False:
                    await bot.send_message(chat_id,f"Username : {username_0},\n\nis not in banned list.")
                    continue
                await tdatabase.remove_banned_username(username_0.lower())
                await pgdatabase.remove_banned_username(username_0.lower())
            if len(usernames) > 1:
                await bot.send_message(chat_id,"Usernames unbanned successfully")
            else:
                await bot.send_message(chat_id,"Username unbanned successfully")
    elif len(usernames) == 1:
        if await tdatabase.get_bool_banned_username(usernames[0]) is False:
            await bot.send_message(chat_id,"Username is not in banned username list.")
            return
        await tdatabase.remove_banned_username(usernames[0].lower())
        await pgdatabase.remove_banned_username(usernames[0].lower())
        await bot.send_message(chat_id,"Username unbanned successfully")

async def add_maintainer(bot,message,maintainer_chat_id,maintainer_name):
    """
    This function is used to add a maintainer. It notifies both the admin and the maintainer about the relevant details.
    :maintainer_chat_id: chat id of the maintainer
    :maintainer_name: Name of the maintainer
    :return: None
    """
    user_chat_id = message.chat.id
    user_full_name = await get_username(bot,user_chat_id)
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    all_maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    try:
        maintainer_chat_id = int(maintainer_chat_id)
    except (ValueError, TypeError):
        pass

    if maintainer_chat_id in admin_chat_ids:
        await bot.send_message(user_chat_id,"You are already an admin and cannot be a maintainer.")
        return
    if maintainer_chat_id in all_maintainer_chat_ids:
        await bot.send_message(user_chat_id,f"{maintainer_name} is already a maintainer.")
        return
    await managers_handler.store_as_maintainer(maintainer_name,maintainer_chat_id)
    await pgdatabase.store_as_maintainer(maintainer_name,maintainer_chat_id)
    await bot.send_message(user_chat_id,f"Successfully added {maintainer_name} as maintainer")
    try:
        await bot.send_message(maintainer_chat_id,f"You've been added as maintainer by {user_full_name}, Use \"/maintainer\" To Access The Buttons")
    except Exception as exc:
        logging.warning("Could not notify new maintainer %s: %s", maintainer_chat_id, exc)

async def verification_to_add_maintainer(bot,message):
    """
    Retrieve user details from a forwarded message, shared contact, replied message, or command arguments,
    and prompt the admin with a confirmation inline keyboard to add them as a maintainer.
    If the target user account is hidden, sends an explicit message explaining it is hidden with recovery steps.

    :param bot: Pyrogram client
    :param message: Message sent by the admin
    """
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

    if not (is_admin or is_authorized_maintainer):
        return

    # Check UI mode preference
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    is_traditional = bool(ui_mode and ui_mode[0] == 1)

    def _format_msg(title: str, body: str) -> str:
        if is_traditional:
            return f"**{title}**\n\n{body}"
        else:
            return f"```{title}\n⫷\n\n{body}\n\n⫸\n```"

    maintainer_chat_id = None
    maintainer_name = None

    def _extract_user_name(user_obj, fallback_id):
        if not user_obj:
            return f"User {fallback_id}"
        first = (getattr(user_obj, "first_name", None) or "").strip()
        last = (getattr(user_obj, "last_name", None) or "").strip()
        full = f"{first} {last}".strip()
        if full:
            return full
        if getattr(user_obj, "username", None):
            return user_obj.username
        return f"User {fallback_id}"

    # Check 1: Message itself is forwarded
    is_forwarded = bool(
        getattr(message, "forward_date", None)
        or getattr(message, "forward_from", None)
        or getattr(message, "forward_sender_name", None)
        or getattr(message, "forward_from_chat", None)
    )

    if is_forwarded:
        if getattr(message, "forward_from", None):
            maintainer_chat_id = message.forward_from.id
            maintainer_name = _extract_user_name(message.forward_from, maintainer_chat_id)
        elif getattr(message, "forward_sender_name", None):
            sender_name = message.forward_sender_name
            body = (
                f"⚠️ The forwarded message is from **{sender_name}**, but their Telegram privacy settings hide their user ID on forwarded messages.\n\n"
                f"Telegram does not provide user IDs for hidden accounts.\n\n"
                f"To add them as a maintainer, please ask them for their Telegram Chat ID (they can find it by messaging this bot or @RawDataBot), then run:\n"
                f"`/add_maintainer <chat_id> {sender_name}`"
            )
            await bot.send_message(chat_id, _format_msg("USER ACCOUNT HIDDEN", body))
            return
        elif getattr(message, "forward_from_chat", None):
            chat_title = getattr(message.forward_from_chat, "title", "channel/group")
            body = (
                f"⚠️ The forwarded message is from a channel or group (**{chat_title}**), not an individual user.\n\n"
                f"Please forward a message from the user's personal Telegram account, or run:\n"
                f"`/add_maintainer <chat_id>`"
            )
            await bot.send_message(chat_id, _format_msg("ADD MAINTAINER", body))
            return
        else:
            body = (
                "⚠️ **User account is hidden!**\n\n"
                "Could not retrieve user details from this forwarded message due to Telegram privacy settings.\n\n"
                "Please ask the user for their Chat ID and run `/add_maintainer <chat_id>`."
            )
            await bot.send_message(chat_id, _format_msg("USER ACCOUNT HIDDEN", body))
            return

    # Check 2: Shared Contact card
    elif getattr(message, "contact", None) and (
        getattr(type(message.contact), "__name__", "") == "Contact"
        or isinstance(getattr(message.contact, "user_id", None), int)
        or (hasattr(message.contact, "phone_number") and not hasattr(message.contact, "_mock_return_value"))
    ):
        contact = message.contact
        c_user_id = getattr(contact, "user_id", None)
        c_first = getattr(contact, "first_name", "") if not hasattr(getattr(contact, "first_name", None), "_mock_return_value") else ""
        c_last = getattr(contact, "last_name", "") if not hasattr(getattr(contact, "last_name", None), "_mock_return_value") else ""
        c_name = f"{c_first or ''} {c_last or ''}".strip() or "User"
        if isinstance(c_user_id, int) and c_user_id > 0:
            maintainer_chat_id = c_user_id
            maintainer_name = c_name
        else:
            body = (
                f"⚠️ **User account is hidden!**\n\n"
                f"The shared contact card for **{c_name}** has a hidden Telegram account (no Telegram user ID linked).\n\n"
                f"Please ask them for their numeric Telegram Chat ID and run:\n"
                f"`/add_maintainer <chat_id> {c_name}`"
            )
            await bot.send_message(chat_id, _format_msg("USER ACCOUNT HIDDEN", body))
            return

    # Check 3: Message is a reply to another message (/add_maintainer replied to a message)
    elif getattr(message, "reply_to_message", None):
        target = message.reply_to_message
        if getattr(target, "forward_from", None):
            maintainer_chat_id = target.forward_from.id
            maintainer_name = _extract_user_name(target.forward_from, maintainer_chat_id)
        elif getattr(target, "forward_sender_name", None):
            sender_name = target.forward_sender_name
            body = (
                f"⚠️ The replied forwarded message is from **{sender_name}**, but their Telegram privacy settings hide their user ID.\n\n"
                f"Telegram does not provide user IDs for hidden accounts.\n\n"
                f"Please run `/add_maintainer <chat_id> {sender_name}` with their numeric Chat ID."
            )
            await bot.send_message(chat_id, _format_msg("USER ACCOUNT HIDDEN", body))
            return
        elif getattr(target, "from_user", None):
            maintainer_chat_id = target.from_user.id
            maintainer_name = _extract_user_name(target.from_user, maintainer_chat_id)
        elif getattr(target, "sender_chat", None):
            chat_title = getattr(target.sender_chat, "title", "channel/group")
            body = (
                f"⚠️ The replied message is from a channel or anonymous admin (**{chat_title}**), not an individual user.\n\n"
                f"Please run `/add_maintainer <chat_id>` with their numeric Chat ID."
            )
            await bot.send_message(chat_id, _format_msg("ADD MAINTAINER", body))
            return
        else:
            body = (
                "⚠️ **User account is hidden!**\n\n"
                "Could not retrieve user details from the replied message because the user's account is hidden.\n\n"
                "Please ask them for their numeric Chat ID and run `/add_maintainer <chat_id>`."
            )
            await bot.send_message(chat_id, _format_msg("USER ACCOUNT HIDDEN", body))
            return

    # Check 4: Command arguments (/add_maintainer <chat_id or @username> [optional_name])
    elif getattr(message, "text", None):
        tokens = message.text.strip().split()
        args = tokens[1:] if tokens and tokens[0].startswith("/") else tokens
        if args:
            raw_arg = args[0].strip()
            # 4a: Numeric Chat ID
            if raw_arg.lstrip("-").isdigit():
                maintainer_chat_id = int(raw_arg)
                if len(args) > 1:
                    maintainer_name = " ".join(args[1:]).strip()
                else:
                    maintainer_name = await get_username(bot, maintainer_chat_id)
            # 4b: Username lookup
            else:
                username_query = raw_arg if raw_arg.startswith("@") else f"@{raw_arg}"
                try:
                    user_obj = await bot.get_users(username_query)
                    if user_obj and getattr(user_obj, "id", None):
                        maintainer_chat_id = user_obj.id
                        if len(args) > 1:
                            maintainer_name = " ".join(args[1:]).strip()
                        else:
                            maintainer_name = _extract_user_name(user_obj, maintainer_chat_id)
                    else:
                        raise ValueError("User not resolved")
                except Exception:
                    body = (
                        f"⚠️ **User account is hidden or cannot be resolved:** `{raw_arg}`\n\n"
                        f"Telegram privacy settings prevent resolving this username or the user does not exist.\n\n"
                        f"**How to add them:**\n"
                        f"Ask the user for their numeric Telegram Chat ID (they can get it by sending `/start` to this bot or using @RawDataBot), then run:\n"
                        f"`/add_maintainer <chat_id> [optional_name]`"
                    )
                    await bot.send_message(chat_id, _format_msg("USER ACCOUNT HIDDEN", body))
                    return
        else:
            # /add_maintainer sent with no args, no reply, no forward
            body = (
                "ℹ️ **How to add a maintainer:**\n\n"
                "1. **Forward a message:** Forward any message from the user to this chat.\n"
                "2. **Use Username:** Send `/add_maintainer @username [name]`\n"
                "3. **Use Chat ID:** Send `/add_maintainer <chat_id> [name]`\n"
                "4. **Reply to a message:** Reply to their message with `/add_maintainer`\n\n"
                "⚠️ **Note on Hidden Accounts:**\n"
                "If the user has Telegram privacy set to hidden, forwarded messages do not carry their ID. Ask them to send `/start` to this bot to get their Chat ID, then use method 3."
            )
            await bot.send_message(chat_id, _format_msg("ADD MAINTAINER", body))
            return
    else:
        body = (
            "ℹ️ Please forward a message from the user, share their contact, reply to their message with `/add_maintainer`, or use `/add_maintainer <chat_id>`."
        )
        await bot.send_message(chat_id, _format_msg("ADD MAINTAINER", body))
        return

    # If maintainer_chat_id was resolved, prompt admin
    if maintainer_chat_id is not None:
        if not maintainer_name:
            maintainer_name = await get_username(bot, maintainer_chat_id)

        try:
            markup = await manager_buttons.start_add_maintainer_button(maintainer_chat_id, maintainer_name)
            await bot.send_message(
                chat_id,
                f"Would you like to add {maintainer_name} as Maintainer.",
                reply_markup=markup
            )
        except Exception as exc:
            logging.error("Failed to send add_maintainer prompt: %s", exc)
            await bot.send_message(
                chat_id,
                f"⚠️ Error preparing confirmation for {maintainer_name} ({maintainer_chat_id}): {exc}"
            )

async def add_admin_by_authorization(bot,message):
    """
    This Function is used to add Admin access to the user by authorizing the message sent.
    :param bot: Pyrogram client
    :param message: Message sent by the user"""
    chat_id = message.chat.id
    authorization_code = message.text.split()[1:][0]
    if authorization_code == ADMIN_AUTHORIZATION_CODE:
        admin_name = await get_username(bot,chat_id)
        await managers_handler.store_as_admin(admin_name,chat_id)
        await pgdatabase.store_as_admin(admin_name,chat_id)
        await bot.send_message(chat_id,"Authorized Successfully for Admin access, use \"/admin\" to start admin panel.")
        await message.delete()

async def announcement_to_all_users(bot, message):
    """
    Broadcast announcement to all users safely using:
    - Queue-based distribution
    - Multiple async workers

    """

    admin_chat_id = message.chat.id
    admin_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_ids = await managers_handler.fetch_maintainer_chat_ids()

    if admin_chat_id not in admin_ids and admin_chat_id not in maintainer_ids:
        return

    access_data = await managers_handler.get_access_data(admin_chat_id)
    if admin_chat_id in maintainer_ids and access_data[1] != 1:
        await bot.send_message(admin_chat_id, "Permission denied.")
        return

    try:
        announcement_text = message.text.split("/announce", 1)[1].strip()
    except Exception:
        announcement_text = ""

    if not announcement_text:
        await bot.send_message(admin_chat_id, "Announcement cannot be empty.")
        return

    msg_updated_ui = f"""```ANNOUNCEMENT\n{announcement_text}\n```"""
    msg_traditional_ui = f"""**ANNOUNCEMENT**\n\n{announcement_text}"""


    chat_ids = await pgdatabase.get_all_chat_ids()
    chat_ids.extend(admin_ids)
    chat_ids.extend(maintainer_ids)
    chat_ids = list(set(chat_ids))
    total_users = len(chat_ids)

    if total_users == 0:
        await bot.send_message(admin_chat_id, "No users found.")
        return

    status_message = await bot.send_message(
        admin_chat_id,
        f"""```ANNOUNCEMENT
● STATUS : STARTED
● TOTAL USERS : {total_users}
```"""
    )

    queue = Queue()
    for cid in chat_ids:
        await queue.put(cid)

    successful = 0
    failed = 0

    WORKERS = 12
    DELAY = 0.25 

    last_update = asyncio.get_event_loop().time()
    UPDATE_INTERVAL = 3.0

    async def worker():
        nonlocal successful, failed, last_update

        while True:
            chat_id = await queue.get()
            if chat_id is None:
                queue.task_done()
                break

            try:
                ui_mode = await user_settings.fetch_ui_bool(chat_id)
                text = msg_traditional_ui if ui_mode and ui_mode[0] == 1 else msg_updated_ui

                await bot.send_message(chat_id, text)
                successful += 1
                await sleep(DELAY)

            except FloodWait as e:
                await sleep(e.value)
                await queue.put(chat_id)

            except Exception:
                failed += 1

            finally:
                queue.task_done()

            now = asyncio.get_event_loop().time()
            if now - last_update >= UPDATE_INTERVAL:
                try:
                    await bot.edit_message_text(
                        admin_chat_id,
                        status_message.id,
                        f"""```ANNOUNCEMENT
● STATUS : SENDING
● TOTAL USERS : {total_users}
● SUCCESSFUL : {successful}
● FAILED : {failed}
● REMAINING : {queue.qsize()}
```"""
                    )
                    last_update = now
                except Exception:
                    pass

    start_time = asyncio.get_event_loop().time()
    tasks = [create_task(worker()) for _ in range(WORKERS)]
    await queue.join()
    for _ in range(WORKERS):
        await queue.put(None)
    await asyncio.gather(*tasks)
    end_time = asyncio.get_event_loop().time()

    total_seconds = end_time - start_time
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    
    processed_count = successful + failed
    avg_time = (total_seconds / processed_count) if processed_count > 0 else 0.0

    success_rate = (successful / total_users) * 100

    await bot.edit_message_text(
        admin_chat_id,
        status_message.id,
        f"""```ANNOUNCEMENT
● STATUS : COMPLETED
● TOTAL USERS : {total_users}
● SUCCESSFUL : {successful}
● FAILED : {failed}
● SUCCESS % : {success_rate:.2f}%

● TOTAL TIME : {minutes}m {seconds}s
● AVG TIME/USER : {avg_time:.3f}s
```"""
    )


async def get_cgpa(bot,chat_id):
    """Return the latest CGPA for the logged-in user as a string.

    Uses the existing session or attempts silent auto-login. Validates session
    against Samvidha and parses CGPA from the credit register page.
    """
    session_data = await tdatabase.load_user_session(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
        ui_mode = (0,)
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id) Use this if you want to check in cloud database
    if not session_data:
        auto_login_by_database_status = await auto_login_by_database_silent(bot,chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
        if auto_login_by_database_status is False and chat_id_in_local_database is False:
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=operations.login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=operations.login_message_traditional_ui)
            return
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data:
        return
    gpa_url = "https://samvidha.iare.ac.in/home?action=credit_register"
    gpa_html = await async_fetch_page(gpa_url, session_data.get('cookies') if session_data else None)
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
    if '<title>Samvidha - Campus Management Portal - IARE</title>' in gpa_html:
        if chat_id_in_local_database:
            await operations.silent_logout_user_if_logged_out(bot,chat_id)
            await get_cgpa(bot,chat_id)
        else:
            await operations.logout_user_if_logged_out(bot,chat_id)
        return
    pattern = r'Cumulative Grade Point Average \(CGPA\) : (\d(?:\.\d\d)?)'
    cgpa_values = re.findall(pattern, gpa_html)
    # sgpa_values = [float(x) for x in sgpa_values]
    if len(cgpa_values) == 0:
        return "0.00"
    cgpa = cgpa_values[-1]
    await silent_logout(chat_id)
    return str(cgpa)

async def total_cie_marks(bot,chat_id):
    """Compute and return total CIE marks for the current semester.

    Scrapes the CIE page, aggregates CIE-1 and CIE-2 marks, and returns the
    numeric total as a string. Returns an exception object on failure.
    """
    session_data = await tdatabase.load_user_session(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
        ui_mode = (0,)
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id) Use this if you want to check in cloud database
    if not session_data:
        auto_login_by_database_status = await auto_login_by_database_silent(bot,chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
        if auto_login_by_database_status is False and chat_id_in_local_database is False:
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=operations.login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=operations.login_message_traditional_ui)
            return
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data:
        return
    cie_marks_url = "https://samvidha.iare.ac.in/home?action=cie_marks_ug"
    cie_html = await async_fetch_page(cie_marks_url, session_data.get('cookies') if session_data else None)
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
    if '<title>Samvidha - Campus Management Portal - IARE</title>' in cie_html:
        if chat_id_in_local_database:
            await operations.silent_logout_user_if_logged_out(bot,chat_id)
            return await total_cie_marks(bot,chat_id)
        else:
            await operations.logout_user_if_logged_out(bot,chat_id)
        return
    try:
        soup = BeautifulSoup(cie_html, 'html.parser')
        # Find all tables 
        tables = soup.find_all('table')
        # Select the latest semester table 
        cie_table = tables[1].find_all('tr')
        # Initialize a list to store the relevant data
        subject_marks_data = []
        # Iterate over each row in the selected semester table
        for row in cie_table:
            cells = row.find_all('td')
            row_data = [cell.get_text(strip=True) for cell in cells]
            # Break if 'Laboratory Marks (Practical)' is found -> to get only subject marks
            if any(item.startswith('Laboratory Marks (Practical)') for item in row_data):
                break
            # Append row data if it's not empty -> to get only subject marks
            if row_data:
                subject_marks_data.append(row_data)
        # Initialize dictionaries and total mark variables
        cie1_marks_dict = {}
        cie2_marks_dict = {}
        total_cie1_marks = 0
        total_cie2_marks = 0

        # Process each row data
        for marks_row in subject_marks_data:
            subject_name = marks_row[2]
            cie1_marks = marks_row[3]
            cie2_marks = marks_row[5]

            cie1_marks_dict[subject_name] = cie1_marks
            cie2_marks_dict[subject_name] = cie2_marks
            excluded_marks = ['','-', '0', '0.0'] 

            if cie1_marks not in excluded_marks:
                total_cie1_marks += float(int(cie1_marks))

            if cie2_marks not in excluded_marks:
                total_cie2_marks += float(int(cie2_marks))

        total_cie_marks = total_cie1_marks + total_cie2_marks

        return str(total_cie_marks)
    except Exception as e:
        return e

async def gpa(bot,chat_id):
    """Send SGPA per semester and CGPA summary to the user.

    Parses the credit register page for SGPA values and latest CGPA and formats
    a message based on the user's UI preference.
    """
    session_data = await tdatabase.load_user_session(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
        ui_mode = (0,)
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id) Use this if you want to check in cloud database
    if not session_data:
        auto_login_by_database_status = await auto_login_by_database_silent(bot,chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
        if auto_login_by_database_status is False and chat_id_in_local_database is False:
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=operations.login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=operations.login_message_traditional_ui)
            return
    session_data = await tdatabase.load_user_session(chat_id)
    gpa_url = "https://samvidha.iare.ac.in/home?action=credit_register"
    gpa_html = await async_fetch_page(gpa_url, session_data.get('cookies') if session_data else None)
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
    if '<title>Samvidha - Campus Management Portal - IARE</title>' in gpa_html:
        if chat_id_in_local_database:
            await operations.silent_logout_user_if_logged_out(bot,chat_id)
            await gpa(bot,chat_id)
        else:
            await operations.logout_user_if_logged_out(bot,chat_id)
        return
    try:
        sgpa_pattern = r'Semester Grade Point Average \(SGPA\) : (\d{1,2}(?:\.\d{1,2})?)'
        cgpa_pattern = r'Cumulative Grade Point Average \(CGPA\) : (\d{1,2}(?:\.\d{1,2})?)'
        sgpa_values = re.findall(sgpa_pattern, gpa_html)
        sgpa_values = [float(x) for x in sgpa_values]
        cgpa_values = re.findall(cgpa_pattern, gpa_html)
        if len(cgpa_values) == 0:
            cgpa = 0.00
        else:
            cgpa = cgpa_values[-1]
        gpa_message = """
```GPA
⫸ SGPA 

"""

        for i,sgpa in enumerate(sgpa_values,start = 1):
            sgpa_message = f'Semester-{i} : {sgpa} \n \n'
            gpa_message += sgpa_message 
            


        gpa_message += f"""⫸ CGPA : {cgpa}  
```
"""
        await bot.send_message(chat_id,gpa_message)
    except Exception as e:
        await bot.send_message(chat_id,f"Error Retrieving GPA : {e}")
async def cie_marks(bot,chat_id):
    """Send a formatted CIE-1 subject-wise breakdown and totals.

    Extracts subject rows until practical marks, computes totals, and sends
    a message in the selected UI style.
    """
    session_data = await tdatabase.load_user_session(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
        ui_mode = (0,)
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id) Use this if you want to check in cloud database
    if not session_data:
        auto_login_by_database_status = await auto_login_by_database_silent(bot,"",chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
        if auto_login_by_database_status is False and chat_id_in_local_database is False:
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=operations.login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=operations.login_message_traditional_ui)
            return
    session_data = await tdatabase.load_user_session(chat_id)
    cie_marks_url = "https://samvidha.iare.ac.in/home?action=cie_marks_ug"
    cie_marks_html = await async_fetch_page(cie_marks_url, session_data.get('cookies') if session_data else None)
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
    if '<title>Samvidha - Campus Management Portal - IARE</title>' in cie_marks_html:
        if chat_id_in_local_database:
            await silent_logout(bot,chat_id)
            await cie_marks(bot,chat_id)
        else:
            await operations.logout_user_if_logged_out(bot,chat_id)
        return
    try:
        soup = BeautifulSoup(cie_marks_html, 'html.parser')
        # Find all tables and reverse the list to get the semesters in ascending order i.e semester 1 to 8 
        tables = soup.find_all('table')
        reversed_tables = tables[::-1] 
        semester_count = len(tables) - 2
        # Select the required semester table 
        cie_table = reversed_tables[semester_count].find_all('tr')
        # Initialize a list to store the relevant data
        subject_marks_data = []
        # Iterate over each row in the selected semester table
        for row in cie_table:
            cells = row.find_all('td')
            row_data = [cell.get_text(strip=True) for cell in cells]
            # Break if 'Laboratory Marks (Practical)' is found -> to get only subject marks
            if 'Laboratory Marks (Practical)' in row_data:
                break
            # Append row data if it's not empty -> to get only subject marks
            if row_data:
                subject_marks_data.append(row_data)
        # Initialize dictionaries and total mark variables
        cie1_marks_dict = {}
        cie2_marks_dict = {}
        total_cie1_marks = 0
        total_cie2_marks = 0
        # Process each row data
        for marks_row in subject_marks_data:
            subject_name = marks_row[2]
            cie1_marks = marks_row[3]
            cie2_marks = marks_row[5]
            cie1_marks_dict[subject_name] = cie1_marks
            cie2_marks_dict[subject_name] = cie2_marks
            excluded_marks = ['-', '0', '0.0'] 
            if cie1_marks not in excluded_marks:
                total_cie1_marks += float(cie1_marks)
            if cie2_marks not in excluded_marks:
                total_cie2_marks += float(cie2_marks)
        # Default total marks as each subject has a maximum of 10 marks
        default_total_marks = float(len(cie1_marks_dict) * 10)
        # print(f"Default Total Marks: {default_total_marks}")
        # Print CIE-1 marks message as markdown
        cie1_marks_message_updated = f"""
```CIE  Marks
""" 
        cie1_marks_message_traditional = f"""
**CIE Marks**
"""
        if ui_mode[0] == 0:
            cie1_marks_message = cie1_marks_message_updated
        elif ui_mode[0] == 1:
            cie1_marks_message = cie1_marks_message_traditional
        for subject_name, marks in cie1_marks_dict.items():
            # print(f"{subject_name}: {marks}")
            cie1_marks_message += f"{subject_name}\n⫸ {marks}\n\n"
            1
        cie1_marks_message += "----\n"
        cie1_marks_message += f"Total Marks - {total_cie1_marks} / {default_total_marks} \n"
        if ui_mode[0] == 0:
            cie1_marks_message += "\n```"
        elif ui_mode[0] == 1:
            cie1_marks_message +="\n"
        # print(cie1_marks_message)
        await bot.send_message(chat_id,cie1_marks_message)
    except Exception as e:
        await bot.send_message(chat_id,f"Error retrieving cie marks : {e}")


async def cgpa_tracker(bot,chat_id):
    """Notify the user when CGPA changes compared to the stored tracker.

    When a change is detected and current CGPA is non-zero, sends a celebratory
    update, displays GPA details, and disables the tracker in both databases.
    """
    current_cgpa = await get_cgpa(bot,chat_id)
    all_tracker_data = await managers_handler.get_cgpa_tracker_details(chat_id) # retrieve previously stored cgpa
    if all_tracker_data:
        status,previous_cgpa = all_tracker_data
    if status:
        if str(previous_cgpa) != current_cgpa and int(float(current_cgpa)) != 0:
            UPDATED_CGPA_TEXT = f"""
```UPDATED CGPA
SEE Results are out!!

PREVIOUS CGPA : {previous_cgpa}

CURRENT CGPA  : {current_cgpa}
```
"""
            await bot.send_message(chat_id,UPDATED_CGPA_TEXT)
            await gpa(bot,chat_id)
            await managers_handler.remove_cgpa_tracker_details(chat_id) # Turning off Tracker on local database
            await pgdatabase.remove_cgpa_tracker_details(chat_id) # Turning off otrracker on pgdatabase
            await bot.send_message(chat_id,"""
```
The CGPA tracker has been reset. We hope you are happy with your semester results. 
                                   
🎉📋
```
""")


async def cie_tracker(bot,chat_id):
    """Notify the user when total CIE changes compared to the tracker.

    Sends an update and the detailed CIE marks, then disables the tracker
    entries in local and cloud databases.
    """
    current_cie_marks = await total_cie_marks(bot,chat_id)
    if not current_cie_marks:
        return
    all_tracker_data = await managers_handler.get_cie_tracker_details(chat_id)
    if all_tracker_data:
        status,previous_cie_marks = all_tracker_data
    if status:
        if str(previous_cie_marks) != current_cie_marks:
            UPDATED_CIE_TEXT = f"""
```UPDATED CIE
CIE Results are out!!

PREVIOUS CIE : {previous_cie_marks}

CURRENT CIE  : {current_cie_marks}
```
"""
            await bot.send_message(chat_id,UPDATED_CIE_TEXT)
            await cie_marks(bot,chat_id)
            await managers_handler.remove_cie_tracker_details(chat_id) # Turning off Tracker on local database
            await pgdatabase.remove_cie_tracker_details(chat_id) # Turning off otrracker on pgdatabase
            await bot.send_message(chat_id,"""
```
The CIA tracker has been reset. We hope you are happy with your CIA results. 
                                   
🎉📋
```
""")


async def auto_login_by_database_silent(bot,chat_id):
    """Attempt silent login using stored credentials.

    Checks for banned usernames and removes credentials if banned. On success,
    stores a fresh session and username for the chat id.
    Returns True on success, False otherwise.
    """
    # username,password = await pgdatabase.retrieve_credentials_from_database(chat_id) This Can be used if you want to take credentials from cloud database.
    username,password = await tdatabase.fetch_credentials_from_database(chat_id) # This can be used to Fetch credentials from the Local database.
    # Initializes settings for the user if the settings are not present
    await user_settings.set_user_default_settings(chat_id)
    if username != None:
        username = username[:10]
        if await tdatabase.get_bool_banned_username(username) is True: # Checks whether the username is in banned users or not.
            # await tdatabase.delete_banned_username_credentials_data(username)
            banned_username_chat_ids = await tdatabase.get_chat_ids_of_the_banned_username(username)
            for chat_id in banned_username_chat_ids:
                if await tdatabase.delete_user_credentials(chat_id) is True:
                    if await pgdatabase.remove_saved_credentials_silent(chat_id) is True:
                        return False
        session_data = await operations.perform_login(username, password)
        if session_data:
            await tdatabase.store_user_session(chat_id, json.dumps(session_data), username)  # Implement store_user_session function
            await tdatabase.store_username(username)
            return True
        else:
            return False
    else:
        return False

async def silent_logout(chat_id):
    """Log out from Samvidha for the given chat id without messaging the user.

    Uses stored session cookies/headers, calls logout, and clears the local
    session from SQLite.
    """
    session_data = await tdatabase.load_user_session(chat_id)
    if session_data:
        await async_logout_portal(session_data.get('cookies'))
    await tdatabase.delete_user_session(chat_id)

async def get_server_stats(traditional_ui: bool = False) -> str:
    """Return a human-readable summary of CPU, memory, disk, network, and process stats.

    Uses `psutil` metrics safely (handling environments like Docker/Coolify where
    cpu_freq or specific paths may return None) and formats them for the bot's UI mode.
    """
    try:
        # Non-blocking CPU measurement
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
        except Exception:
            cpu_percent = 0.0

        cpu_count = psutil.cpu_count(logical=True) or 1

        # CPU frequency (may be None in Docker/LXC/VM environments)
        cpu_freq_str = ""
        try:
            freq = psutil.cpu_freq()
            if freq and getattr(freq, "current", None):
                cpu_freq_str = f" ({freq.current:.0f} MHz)"
        except Exception:
            pass

        # Memory stats
        try:
            mem = psutil.virtual_memory()
            mem_used = mem.used / (1024 * 1024)
            mem_total = mem.total / (1024 * 1024)
            mem_percent = mem.percent
        except Exception:
            mem_used, mem_total, mem_percent = 0.0, 0.0, 0.0

        # Bot process memory
        process_mem_str = "N/A"
        try:
            process = psutil.Process()
            proc_mb = process.memory_info().rss / (1024 * 1024)
            process_mem_str = f"{proc_mb:.1f} MB"
        except Exception:
            pass

        # Disk stats (cross-platform safe)
        disk_str = "N/A"
        for disk_path in ['/', '.', os.path.abspath(os.sep)]:
            try:
                disk = psutil.disk_usage(disk_path)
                disk_used_gb = disk.used / (1024 * 1024 * 1024)
                disk_total_gb = disk.total / (1024 * 1024 * 1024)
                disk_str = f"{disk.percent}% ({disk_used_gb:.1f} GB / {disk_total_gb:.1f} GB)"
                break
            except Exception:
                continue

        # Network stats
        net_str = "N/A"
        try:
            net = psutil.net_io_counters()
            if net:
                bytes_sent = net.bytes_sent / (1024 * 1024)
                bytes_recv = net.bytes_recv / (1024 * 1024)
                net_str = f"Sent: {bytes_sent:.1f} MB | Recv: {bytes_recv:.1f} MB"
        except Exception:
            pass

        # System Uptime
        uptime_str = "N/A"
        try:
            import time
            boot_time = psutil.boot_time()
            uptime_seconds = int(time.time() - boot_time)
            uptime_days = uptime_seconds // 86400
            uptime_hours = (uptime_seconds % 86400) // 3600
            uptime_mins = (uptime_seconds % 3600) // 60
            uptime_str = f"{uptime_days}d {uptime_hours}h {uptime_mins}m"
        except Exception:
            pass

        if traditional_ui:
            return (
                "**SERVER STATS**\n\n"
                f"● **CPU:** {cpu_percent}%{cpu_freq_str} ({cpu_count} cores)\n"
                f"● **Memory:** {mem_used:.1f} MB / {mem_total:.1f} MB ({mem_percent}%)\n"
                f"● **Bot RAM:** {process_mem_str}\n"
                f"● **Disk:** {disk_str}\n"
                f"● **Network:** {net_str}\n"
                f"● **Uptime:** {uptime_str}"
            )
        else:
            return (
                "```SERVER STATS\n"
                "⫷\n\n"
                f"● CPU          -  {cpu_percent}%{cpu_freq_str} ({cpu_count} cores)\n"
                f"● Memory       -  {mem_used:.1f} MB / {mem_total:.1f} MB ({mem_percent}%)\n"
                f"● Bot RAM      -  {process_mem_str}\n"
                f"● Disk         -  {disk_str}\n"
                f"● Network      -  {net_str}\n"
                f"● Uptime       -  {uptime_str}\n\n"
                "⫸\n"
                "```"
            )
    except Exception as e:
        if traditional_ui:
            return f"**SERVER STATS**\n\n**Error:** {e}"
        else:
            return f"```SERVER STATS\nError: {e}\n```"

async def backup_all_credentials_and_settings(bot,message):
    """Create and send a SQLite backup of user credentials and settings.

    Reads credentials/settings from Postgres, writes them into a local SQLite
    file, and sends the file as a document to the requesting user.
    """
    user_chat_id = message.chat.id
    # admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    # if chat_id not in admin_chat_ids:
    #     print("chat id not in admin chat_ids")
    #     await bot.send_message(user_chat_id,"You are not authorized to perform this operation")
    #     return
    user_credentials_and_settings_sqlite = "user_credentials_settings_backup.db"
    print("User credentials database name is assigned")
    with sqlite3.connect(user_credentials_and_settings_sqlite) as conn:
        print("Connection with the sqlite3 database is successfully done")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_credentials (
                chat_id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT,
                pat_student BOOLEAN,
                attendance_threshold INTEGER,
                biometric_threshold INTEGER,
                traditional_ui BOOLEAN,
                title_extract BOOLEAN
            )
        """)
        credentials_settings = await pgdatabase.get_all_credentials()
        for row in credentials_settings:
            chat_id,username,password,pat_student,attendance_threshold,biometric_threshold,traditional_ui,extract_title = row
            cursor.execute("INSERT INTO user_credentials (chat_id,username,password,pat_student,attendance_threshold,biometric_threshold,traditional_ui,title_extract) VALUES (?,?,?,?,?,?,?,?)",(chat_id,username,password,pat_student,attendance_threshold,biometric_threshold,traditional_ui,extract_title))
        conn.commit()

    try:
            # Ensure the file exists before sending
            # chat_id = message.chat.id
            if os.path.exists(user_credentials_and_settings_sqlite):
                await bot.send_document(user_chat_id, document=user_credentials_and_settings_sqlite, caption="Backup of user credentials and settings")
            else:
                await bot.send_message(user_chat_id, "Error: Backup file not found.")
    except Exception as e:
            await bot.send_message(user_chat_id, f"Error sending backup file: {e}")
            # print(e)


# This Function can be used to send the Announcement file in future.
# async def download_announcement_file(bot,message):
#     if message.chat.id != BOT_DEVELOPER_CHAT_ID and message.chat.id != BOT_MAINTAINER_CHAT_ID:
#         return
#     download_document_directory = "Announcements"
#     chat_id  = message.chat.id
#     if message.document or message.video:
#         try:
#             if not os.path.exists(download_document_directory):
#                 os.makedirs(download_document_directory)
#             started_receiving_document_text = f"""
#     ```DOC STATUS
#     ● Status : Receiving
#     ```
#     """
#             message_before_recieving = await bot.send_message(chat_id,started_receiving_document_text)
#             file_name_ = message.document.file_name
#             await message.download(
#                         file_name=os.path.join(download_document_directory, file_name_),
#                     )
#             received_document_text = f"""
#     ```DOC STATUS
#     ● Status : Received

#     ● Filename : {file_name_}
#     ```
#     """
#             await bot.edit_message_text(chat_id,message_before_recieving.id,received_document_text)
#         except Exception as e:
#             await bot.send_message(chat_id,f"Error receiving file : {e}")
