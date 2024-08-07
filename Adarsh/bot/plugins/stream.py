import os
import random
import aiohttp
import asyncio
from urllib.parse import quote_plus
import logging

from pyrogram import filters, Client
from pyrogram.errors import FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from shortzy import Shortzy

from Adarsh.bot import StreamBot
from Adarsh.utils.database import Database
from Adarsh.utils.human_readable import humanbytes
from Adarsh.vars import Var
from Adarsh.utils.file_properties import get_name, get_hash, get_media_file_size

# Initialize databases
db = Database(Var.DATABASE_URL, Var.name)
pass_db = Database(Var.DATABASE_URL, "ag_passwords")

MY_PASS = os.environ.get("MY_PASS", None)
pass_dict = {}

class temp(object):
    U_NAME = None
    B_NAME = None

# Set up logging
logging.basicConfig(level=logging.DEBUG)

@StreamBot.on_message(filters.group & filters.command('set_caption'))
async def add_caption(c: Client, m: Message):
    if len(m.command) == 1:
        buttons = [[InlineKeyboardButton('⇇ ᴄʟᴏsᴇ ⇉', callback_data='close')]]
        return await m.reply_text(
            "**ʜᴇʏ 👋\n\n<u>ɢɪᴠᴇ ᴛʜᴇ ᴄᴀᴩᴛɪᴏɴ</u>\n\nᴇxᴀᴍᴩʟᴇ:- `/set_caption <b>{file_name}\n\nSize : {file_size}\n\n➠ Fast Download Link :\n{download_link}\n\n➠ watch Download Link : {watch_link}\n\n☠️ Powered By : @OMGxLinks</b>`**",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    caption = m.text.split(" ", 1)[1]
    await db.set_caption(m.from_user.id, caption=caption)
    buttons = [[InlineKeyboardButton('⇇ ᴄʟᴏsᴇ ⇉', callback_data='close')]]
    ok = await m.reply_text(f"<b>ʜᴇʏ {m.from_user.mention}\n\n✅ sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ᴀᴅᴅᴇᴅ ʏᴏᴜʀ ᴄᴀᴩᴛɪᴏɴ ᴀɴᴅ sᴀᴠᴇᴅ</b>", reply_markup=InlineKeyboardMarkup(buttons))
    await asyncio.sleep(5)
    await ok.delete()
    await m.delete()

@StreamBot.on_message(filters.group & filters.command('del_caption'))
async def delete_caption(c: Client, m: Message):
    caption = await db.get_caption(m.from_user.id)
    if not caption:
        return await m.reply_text("__**😔 Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Aɴy Cᴀᴩᴛɪᴏɴ**__")
    await db.set_caption(m.from_user.id, caption=None)
    buttons = [[InlineKeyboardButton('⇇ ᴄʟᴏsᴇ ⇉', callback_data='close')]]
    g = await m.reply_text(f"<b>ʜᴇʏ {m.from_user.mention}\n\n✅ sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ʏᴏᴜʀ ᴄᴀᴩᴛɪᴏɴ</b>", reply_markup=InlineKeyboardMarkup(buttons))
    await asyncio.sleep(5)
    await g.delete()
    await m.delete()

@StreamBot.on_message(filters.group & filters.command(['see_caption', 'view_caption']))
async def see_caption(c: Client, m: Message):
    caption = await db.get_caption(m.from_user.id)
    if caption:
        await m.reply_text(f"**ʏᴏᴜʀ ᴄᴀᴩᴛɪᴏɴ:-**\n\n`{caption}`")
    else:
        await m.reply_text("__**😔 Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Aɴy Cᴀᴩᴛɪᴏɴ**__")

@StreamBot.on_message((filters.group) & (filters.document | filters.video | filters.audio | filters.photo), group=4)
async def private_receive_handler(c: Client, m: Message):
    if str(m.chat.id).startswith("-100") and m.chat.id not in Var.GROUP_ID:
        return
    elif m.chat.id not in Var.GROUP_ID:
        if not await db.is_user_exist(m.from_user.id):
            await db.add_user(m.from_user.id)
            await c.send_message(
                Var.BIN_CHANNEL,
                f"New User Joined! : \n\n Name : [{m.from_user.first_name}](tg://user?id={m.from_user.id}) Started Your Bot!!"
            )
            return

    media = m.document or m.video or m.audio
    file_name = f"{m.caption}" if m.caption else ""
    file_name = file_name.replace(".mkv", "").replace("HEVC", "#HEVC").replace("Sample video.", "#SampleVideo").replace(".", " ")

    try:
        user = await db.get_user(m.from_user.id)
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
        
        hs_stream_link = f"{Var.URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        logging.debug(f"Generating short link for hs_stream_link: {hs_stream_link} and user: {user}")
        stream_link = await short_link(hs_stream_link, user)
        logging.debug(f"Generated stream_link: {stream_link}")

        hs_online_link = f"{Var.URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        logging.debug(f"Generating short link for hs_online_link: {hs_online_link} and user: {user}")
        online_link = await short_link(hs_online_link, user)
        logging.debug(f"Generated online_link: {online_link}")

        await log_msg.reply_text(
            text=f"**RᴇQᴜᴇꜱᴛᴇᴅ ʙʏ :** [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n**Uꜱᴇʀ ɪᴅ :** `{m.from_user.id}`\n**Stream ʟɪɴᴋ :** {stream_link}",
            disable_web_page_preview=True,
            quote=True
        )
        
        c_caption = await db.get_caption(m.from_user.id)
        if c_caption:
            try:
                caption = c_caption.format(file_name='' if file_name is None else file_name, file_size=humanbytes(get_media_file_size(m)), download_link=online_link, watch_link=stream_link)
            except Exception as e:
                logging.error(f"Error formatting caption: {e}")
                return
        else:
            caption = None

        await c.send_cached_media(
            caption=caption,
            chat_id=m.chat.id,
            file_id=media.file_id
        )
        
        buttons = [[InlineKeyboardButton('⇇ ᴄʟᴏsᴇ ⇉', callback_data='close')]]
        await m.reply(
            "<b>❗⚠️❗🚨 ɪᴍᴘᴏʀᴛᴀɴᴛ 🚨❗⚠️❗️\n\n🎭 ᴛʜɪꜱ ᴍᴏᴠɪᴇ ғɪʟᴇ/ᴠɪᴅᴇᴏ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪɴ <code>𝟷𝟶 ᴍɪɴᴜᴛᴇꜱ</code> ʙᴇᴄᴀᴜꜱᴇ ɪᴛꜱ ᴏᴠᴇʀ ᴜꜱᴀɢᴇ❗\n\n<b>ᴘʟᴇᴀꜱᴇ ꜰᴏʀᴡᴀʀᴅ/ꜱᴀᴠᴇ ᴛʜɪꜱ ᴍᴏᴠɪᴇ/ᴠɪᴅᴇᴏ ꜰɪʟᴇ ɪɴ ʏᴏᴜʀ ᴏᴡɴ ᴄʜᴀᴛ/ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴛʜᴇɴ ꜱᴇɴᴅ ᴛʜᴇ ʟɪɴᴋ ᴛᴏ ʏᴏᴜʀ ᴍᴇᴍʙᴇʀꜱ🚀</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except FloodWait as e:
        logging.error(f"FloodWait encountered: {str(e.x)}s")
        await asyncio.sleep(e.x)
        await c.send_message(chat_id=Var.BIN_CHANNEL, text=f"Got FloodWait of {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n**User ID :** `{str(m.from_user.id)}`", disable_web_page_preview=True)

async def short_link(link, user=None):
    if not user:
        return link

    api_key = user.get("shortner_api")
    base_site = user.get("shortner_url")

    logging.debug(f"Shortening link: {link} with API: {api_key} and base_site: {base_site}")

    if bool(api_key and base_site) and Var.USERS_CAN_USE:
        shortzy = Shortzy(api_key, base_site)
        try:
            link = await shortzy.convert(link)
        except aiohttp.ClientResponseError as e:
            logging.error(f"ClientResponseError: {e.status}, message='{e.message}', url={e.request_info.url}")
            return link  # Return the original link if conversion fails
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return link  # Return the original link if any other error occurs

    return link

@StreamBot.on_callback_query(filters.regex(r"^close$"))
async def close_button(c: Client, cb: CallbackQuery):
    await cb.message.delete()
    try:
        await cb.message.reply_to_message.delete()
    except:
        pass
    await cb.answer()

if __name__ == "__main__":
    StreamBot.run()
