from pyrogram import Client, filters, enums from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid from pyrogram.errors import ChatAdminRequired from info import ADMINS, LOG_CHANNEL, SUPPORT_CHAT, MELCOW_VID from database.users_chats_db import db from database.ia_filterdb import Media from utils import get_size, temp, get_settings from Script import script import asyncio

SUPPORT_BTN = [ [ InlineKeyboardButton('🧩 Ւ՘Ւ՘ԾՒՐՐ 🧩', url=f"https://t.me/{SUPPORT_CHAT}"), InlineKeyboardButton('⚡ՒքխԹՐպ⚡', url="https://t.me/piroxbots") ] ]

@Client.on_message(filters.new_chat_members & filters.group) async def save_group(bot, message): new_ids = [u.id for u in message.new_chat_members] if temp.ME in new_ids: if not await db.get_chat(message.chat.id): total = await bot.get_chat_members_count(message.chat.id) adder = message.from_user.mention if message.from_user else "Anonymous" await bot.send_message( LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, adder) ) await db.add_chat(message.chat.id, message.chat.title)

if message.chat.id in temp.BANNED_CHATS:
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton('🌐 Կվփտօրտ 🌐', url=f"https://t.me/{SUPPORT_CHAT}")
        ]])
        msg = await message.reply(
            '<b>CHAT NOT ALLOWED 🐞\n\nMy admins have restricted me from working here! Contact support to learn more.</b>',
            reply_markup=reply_markup
        )
        try: await msg.pin()
        except: pass
        return await bot.leave_chat(message.chat.id)

    await message.reply_text(
        f"<b>Thank you for adding me in {message.chat.title} ❣️\n\nFor help and questions, contact the support group.</b>",
        reply_markup=InlineKeyboardMarkup(SUPPORT_BTN)
    )
else:
    settings = await get_settings(message.chat.id)
    if settings.get("welcome"):
        for u in message.new_chat_members:
            try:
                if temp.MELCOW.get('welcome'):
                    await temp.MELCOW['welcome'].delete()
            except: pass
            temp.MELCOW['welcome'] = await message.reply_video(
                video=MELCOW_VID,
                caption=script.MELCOW_ENG.format(u.mention, message.chat.title),
                reply_markup=InlineKeyboardMarkup(SUPPORT_BTN),
                parse_mode=enums.ParseMode.HTML
            )

    if settings.get("auto_delete"):
        await asyncio.sleep(300)
        try: await temp.MELCOW['welcome'].delete()
        except: pass

@Client.on_message(filters.command('leave') & filters.user(ADMINS)) async def leave_a_chat(bot, message): if len(message.command) == 1: return await message.reply('Give me a chat id') chat = message.command[1] try: chat = int(chat) except: pass try: await bot.send_message( chat_id=chat, text='<b>Hello Friends, my admin asked me to leave the group. If you want to add me again, contact support.</b>', reply_markup=InlineKeyboardMarkup(SUPPORT_BTN) ) await bot.leave_chat(chat) await message.reply(f"Left the chat {chat}") except Exception as e: await message.reply(f"Error - {e}")

@Client.on_message(filters.command('disable') & filters.user(ADMINS)) async def disable_chat(bot, message): if len(message.command) < 2: return await message.reply('Give me a chat id') args = message.text.split(None, 2) chat, reason = args[1], args[2] if len(args) > 2 else "No reason Provided" try: chat = int(chat) except: return await message.reply('Invalid Chat ID')

chat_data = await db.get_chat(chat)
if not chat_data:
    return await message.reply("Chat not found in DB")
if chat_data.get('is_disabled'):
    return await message.reply(f"Already disabled. Reason: <code>{chat_data['reason']}</code>")

await db.disable_chat(chat, reason)
temp.BANNED_CHATS.append(chat)
await message.reply('Chat successfully disabled')
try:
    await bot.send_message(
        chat_id=chat,
        text=f'<b>Hello friends, I was asked to leave this group.</b>\nReason: <code>{reason}</code>',
        reply_markup=InlineKeyboardMarkup(SUPPORT_BTN)
    )
    await bot.leave_chat(chat)
except Exception as e:
    await message.reply(f"Error - {e}")

@Client.on_message(filters.command('enable') & filters.user(ADMINS)) async def re_enable_chat(bot, message): if len(message.command) < 2: return await message.reply('Give me a chat id') try: chat = int(message.command[1]) except: return await message.reply('Invalid Chat ID')

status = await db.get_chat(chat)
if not status:
    return await message.reply("Chat not found in DB")
if not status.get('is_disabled'):
    return await message.reply("This chat is not disabled")

await db.re_enable_chat(chat)
temp.BANNED_CHATS.remove(chat)
await message.reply("Chat successfully re-enabled")

@Client.on_message(filters.command('stats') & filters.incoming) async def get_stats(bot, message): msg = await message.reply('Fetching stats...') total_users = await db.total_users_count() total_chats = await db.total_chat_count() files = await Media.count_documents() size_used = await db.get_db_size() size_free = 536870912 - size_used await msg.edit(script.STATUS_TXT.format(files, total_users, total_chats, get_size(size_used), get_size(size_free)))

@Client.on_message(filters.command('invite') & filters.user(ADMINS)) async def gen_invite(bot, message): if len(message.command) < 2: return await message.reply('Give me a chat id') try: chat = int(message.command[1]) except: return await message.reply('Invalid Chat ID') try: link = await bot.create_chat_invite_link(chat) await message.reply(f"Here is your Invite Link: {link.invite_link}") except ChatAdminRequired: await message.reply("Invite Link Generation Failed: Insufficient Rights") except Exception as e: await message.reply(f"Error: {e}")
