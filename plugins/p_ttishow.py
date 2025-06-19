from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
from pyrogram.errors import ChatAdminRequired
from info import ADMINS, LOG_CHANNEL, SUPPORT_CHAT, MELCOW_VID
from database.users_chats_db import db
from database.ia_filterdb import Media
from utils import get_size, temp, get_settings
from Script import script
import asyncio


@Client.on_message(filters.new_chat_members & filters.group)
async def save_group(bot, message):
    r_j_check = [u.id for u in message.new_chat_members]
    if temp.ME in r_j_check:
        if not await db.get_chat(message.chat.id):
            total = await bot.get_chat_members_count(message.chat.id)
            r_j = message.from_user.mention if message.from_user else "Anonymous"
            await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, r_j))
            await db.add_chat(message.chat.id, message.chat.title)

        if message.chat.id in temp.BANNED_CHATS:
            buttons = [[InlineKeyboardButton('🌐 𝖲𝗎𝗉𝗉𝗈𝗋𝗍 🌐', url=f"https://t.me/{SUPPORT_CHAT}")]]
            reply_markup = InlineKeyboardMarkup(buttons)
            k = await message.reply(
                text='<b>CHAT NOT ALLOWED 🐞\n\nMy admins have restricted me from working here! Contact support.</b>',
                reply_markup=reply_markup,
            )
            try:
                await k.pin()
            except:
                pass
            await bot.leave_chat(message.chat.id)
            return

        buttons = [[
            InlineKeyboardButton('🧩 𝖲𝖴𝖯𝖯𝖮𝖱𝖳 🧩', url=f"https://t.me/{SUPPORT_CHAT}"),
            InlineKeyboardButton('⚡𝖴𝗉𝖽𝖺𝗍𝖾𝗌 ⚡', url="https://t.me/batmancineflix")
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=f"<b>Thank you for adding me in {message.chat.title} ❣️\n\nFor help, contact the support group.</b>",
            reply_markup=reply_markup
        )
    else:
        settings = await get_settings(message.chat.id)
        if settings["welcome"]:
            for u in message.new_chat_members:
                if temp.MELCOW.get('welcome') is not None:
                    try:
                        await temp.MELCOW['welcome'].delete()
                    except:
                        pass
                temp.MELCOW['welcome'] = await message.reply_video(
                    video=MELCOW_VID,
                    caption=script.MELCOW_ENG.format(u.mention, message.chat.title),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton('🧩 𝖲𝖴𝖯𝖯𝖮𝖱𝖳 🧩', url=f"https://t.me/{SUPPORT_CHAT}"),
                        InlineKeyboardButton('⚡𝖴𝗉𝖽𝖺𝗍𝖾𝗌 ⚡', url="https://t.me/batmancineflix")
                    ]]),
                    parse_mode=enums.ParseMode.HTML
                )
                if settings["auto_delete"]:
                    await asyncio.sleep(300)
                    await temp.MELCOW['welcome'].delete()


@Client.on_message(filters.command('leave') & filters.user(ADMINS))
async def leave_a_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        pass
    try:
        buttons = [[
            InlineKeyboardButton('🧩 SUPPORT 🧩', url=f"https://t.me/{SUPPORT_CHAT}"),
            InlineKeyboardButton('⚡UPDATES ⚡', url="https://t.me/batmancineflix")
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat,
            text='<b>My admin has told me to leave this group. If you want to add me again, contact support.</b>',
            reply_markup=reply_markup
        )
        await bot.leave_chat(chat)
        await message.reply(f"Left the chat {chat}")
    except Exception as e:
        await message.reply(f'Error - {e}')


@Client.on_message(filters.command('disable') & filters.user(ADMINS))
async def disable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    cha_t = await db.get_chat(chat_)
    if not cha_t:
        return await message.reply("Chat Not Found In DB")
    if cha_t['is_disabled']:
        return await message.reply(f"Already disabled:\nReason-<code>{cha_t['reason']}</code>")
    await db.disable_chat(chat_, reason)
    temp.BANNED_CHATS.append(chat_)
    await message.reply('Chat Successfully Disabled')
    try:
        buttons = [[
            InlineKeyboardButton('🧩 SUPPORT 🧩', url=f"https://t.me/{SUPPORT_CHAT}"),
            InlineKeyboardButton('⚡UPDATES ⚡', url="https://t.me/batmancineflix")
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat_,
            text=f'<b>Hello Friends,\nMy admin has told me to leave. If you want to add me again, contact support.</b>\nReason: <code>{reason}</code>',
            reply_markup=reply_markup
        )
        await bot.leave_chat(chat_)
    except Exception as e:
        await message.reply(f"Error - {e}")


@Client.on_message(filters.command('enable') & filters.user(ADMINS))
async def re_enable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    sts = await db.get_chat(chat_)
    if not sts:
        return await message.reply("Chat Not Found In DB")
    if not sts.get('is_disabled'):
        return await message.reply('This chat is not yet disabled.')
    await db.re_enable_chat(chat_)
    temp.BANNED_CHATS.remove(chat_)
    await message.reply("Chat Successfully re-enabled")


@Client.on_message(filters.command('stats') & filters.incoming)
async def get_stats(bot, message):
    rju = await message.reply('Fetching stats...')
    total_users = await db.total_users_count()
    totl_chats = await db.total_chat_count()
    files = await Media.count_documents()
    size = await db.get_db_size()
    free = 536870912 - size
    size = get_size(size)
    free = get_size(free)
    await rju.edit(script.STATUS_TXT.format(files, total_users, totl_chats, size, free))


@Client.on_message(filters.command('invite') & filters.user(ADMINS))
async def gen_invite(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    try:
        link = await bot.create_chat_invite_link(chat)
    except ChatAdminRequired:
        return await message.reply("I don't have permission to generate invite link.")
    except Exception as e:
        return await message.reply(f'Error {e}')
    await message.reply(f'Here is your Invite Link {link.invite_link}')


@Client.on_message(filters.command('ban') & filters.user(ADMINS))
async def ban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a user id or username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        user_id = message.text.split(None, 2)[1]
    else:
        user_id = message.command[1]
        reason = "No reason Provided"
    try:
        user = await bot.get_users(user_id)
    except PeerIdInvalid:
        return await message.reply("Invalid user. Make sure I’ve met them before.")
    except Exception as e:
        return await message.reply(f'Error - {e}')
    jar = await db.get_ban_status(user.id)
    if jar['is_banned']:
        return await message.reply(f"{user.mention} is already banned\nReason: {jar['ban_reason']}")
    await db.ban_user(user.id, reason)
    temp.BANNED_USERS.append(user.id)
    await message.reply(f"Successfully banned {user.mention}")


@Client.on_message(filters.command('unban') & filters.user(ADMINS))
async def unban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a user id or username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        user_id = message.text.split(None, 2)[1]
    else:
        user_id = message.command[1]
        reason = "No reason Provided"
    try:
        user = await bot.get_users(user_id)
    except PeerIdInvalid:
        return await message.reply("Invalid user. Make sure I’ve met them before.")
    except Exception as e:
        return await message.reply(f'Error - {e}')
    jar = await db.get_ban_status(user.id)
    if not jar['is_banned']:
        return await message.reply(f"{user.mention} is not yet banned.")
    await db.remove_ban(user.id)
    temp.BANNED_USERS.remove(user.id)
    await message.reply(f"Successfully unbanned {user.mention}")


@Client.on_message(filters.command('users') & filters.user(ADMINS))
async def list_users(bot, message):
    raju = await message.reply('Getting list of users...')
    users = await db.get_all_users()
    out = "Users Saved In DB:\n\n"
    async for user in users:
        out += f"<a href='tg://user?id={user['id']}'>{user['name']}</a>"
        if user['ban_status']['is_banned']:
            out += ' (Banned)'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('users.txt', 'w+') as f:
            f.write(out)
        await message.reply_document('users.txt', caption="List Of Users")


@Client.on_message(filters.command('chats') & filters.user(ADMINS))
async def list_chats(bot, message):
    raju = await message.reply('Getting list of chats...')
    chats = await db.get_all_chats()
    out = "Chats Saved In DB:\n\n"
    async for chat in chats:
        out += f"Title: {chat['title']}\nID: {chat['id']}"
        if chat['chat_status']['is_disabled']:
            out += ' (Disabled)'
        out += '\n\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('chats.txt', 'w+') as f:
            f.write(out)
        await message.reply_document('chats.txt', caption="List Of Chats")
