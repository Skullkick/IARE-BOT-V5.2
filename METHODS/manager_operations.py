import sqlite3,os

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
    user = await bot.get_users(chat_id)
    user_name = f"{user.first_name} {user.last_name}" 
    return user_name
async def get_all_details(bot,chat_id):
    user = await bot.get_users(5877699254)
    phone_number = user.phone_number if user.phone_number else "Phone number not available"
    name = user.first_name + (" " + user.last_name if user.last_name else "")
    return f"Name: {name} \n\n Phone number : {phone_number}"
async def ban_username(bot,message):
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
    if maintainer_chat_id in admin_chat_ids:
        await bot.send_message(user_chat_id,"You are already an admin and cannot be a maintainer.")
        return
    if maintainer_chat_id in all_maintainer_chat_ids:
        await bot.send_message(user_chat_id,f"{maintainer_name} is already a maintainer.")
        return
    await managers_handler.store_as_maintainer(maintainer_name,maintainer_chat_id)
    await pgdatabase.store_as_maintainer(maintainer_name,maintainer_chat_id)
    await bot.send_message(user_chat_id,f"Successfully added {maintainer_name} as maintainer")
    await bot.send_message(maintainer_chat_id,f"You've been added as maintainer by {user_full_name}, Use \"/maintainer\" To Access The Buttons")
async def verification_to_add_maintainer(bot,message):
    """
    This Function is used to get all the maintainer details and ask admin whether he needs to be added or not.
    :param bot: Pyrogram client
    :param message: Message sent by the user.
    """
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    chat_id = message.chat.id
    if message.chat.id not in admin_chat_ids:
        return
    if message.forward_from and message.text:
        maintainer_chat_id = message.forward_from.id
        maintainer_name = await get_username(bot,maintainer_chat_id)
        await bot.send_message(chat_id,f"Would you like to add {maintainer_name} as Maintainer.",reply_markup = await manager_buttons.start_add_maintainer_button(maintainer_chat_id,maintainer_name))
    if message.forward_from_chat and message.text:
        maintainer_chat_id = message.forward_from_chat.id # Chat id of the message that user forwarded
        maintainer_name = await get_username(bot,maintainer_chat_id) # Name of the maintainer based on the chat_id

    elif message.from_user and message.text and not message.forward_from and not message.forward_from_chat:
        # print(message.text)
        maintainer_chat_id = message.text.split()[1:][0]
        maintainer_name = await get_username(bot,maintainer_chat_id)
        await bot.send_message(chat_id,f"Would you like to add {maintainer_name} as Maintainer.",reply_markup = await manager_buttons.start_add_maintainer_button(maintainer_chat_id,maintainer_name))

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
    This function is used to announce a message to all the users that are present in the 
    Postgres database, this can only be used by BOT_DEVELOPER or BOT_MAINTAINER
    """
    admin_or_maintainer_chat_id = message.chat.id
    # Only allow execution by specified chat IDs
    # if message.chat.id != BOT_DEVELOPER_CHAT_ID and message.chat.id != BOT_MAINTAINER_CHAT_ID:
    #     return
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_id = await managers_handler.fetch_maintainer_chat_ids()
    if admin_or_maintainer_chat_id not in admin_chat_ids and admin_or_maintainer_chat_id not in maintainer_chat_id:
        return
    access_data = await managers_handler.get_access_data(admin_or_maintainer_chat_id)
    maintainer_announcement_status = access_data[1]
    if admin_or_maintainer_chat_id in maintainer_chat_id and maintainer_announcement_status != 1:
        await bot.send_message(admin_or_maintainer_chat_id,"Permission denied. You cannot use this command.")
        return
    # Retrieve all chat IDs from database
    chat_ids = await pgdatabase.get_all_chat_ids()
    # Get the announcement message from the input message
    developer_announcement = message.text.split("/announce", 1)[1].strip()
    
    # Validate announcement message
    if not developer_announcement:
        await bot.send_message(admin_or_maintainer_chat_id, "Announcement cannot be empty.")
        return
    announcement_message_updated_ui = f"""
```ANNOUNCEMENT
{developer_announcement}
```
"""
    announcement_message_traditional_ui = f"""
**ANNOUNCEMENT**

{developer_announcement}
"""
    # Track successful sends
    successful_sends = 0
    announcement_status_dev = f"""
```ANNOUNCEMENT
● STATUS : Started sending.
```
""" 
    message_to_developer = await bot.send_message(admin_or_maintainer_chat_id,announcement_status_dev)
    # Iterate over each chat ID and send the announcement message and documents
    for chat_id in chat_ids:
        total_users = len(chat_ids)
        try:
            ui_mode = await user_settings.fetch_ui_bool(chat_id)
            if ui_mode[0] == 0:
                await bot.send_message(chat_id, announcement_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id, announcement_message_traditional_ui)
            else:
                await bot.send_message(chat_id, announcement_message_updated_ui)
            successful_sends += 1
            announcement_status_dev = f"""
```ANNOUNCEMENT
● STATUS     : Started sending.

● TOTAL USERS  : {total_users}

● SUCCESSFULL SENDS : {successful_sends}
```
""" 
            await bot.edit_message_text(admin_or_maintainer_chat_id,message_to_developer.id, announcement_status_dev)
            
        except Exception as e:
            await bot.send_message(admin_or_maintainer_chat_id, f"Error sending message to chat ID {chat_id}: {e}")
    
    # Calculate success percentage
    total_attempts = len(chat_ids)
    success_percentage = (successful_sends / total_attempts) * 100 if total_attempts > 0 else 0.0
    announcement_status_dev = f"""
```ANNOUNCEMENT
● STATUS : SENT

● TOTAL USERS  : {total_attempts}

● SUCCESSFULL SENDS : {successful_sends}

● SUCCESS % : {success_percentage}

```
""" 
    # Send success percentage message
    await bot.edit_message_text(admin_or_maintainer_chat_id,message_to_developer.id, announcement_status_dev)
