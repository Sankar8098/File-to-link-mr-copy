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

class TempVars:
    U_NAME = None
    B_NAME = None

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Command to set caption
@StreamBot.on_message(filters.group & filters.command('set_caption'))
async def add_caption(c: Client, m: Message):
    if len(m.command) == 1:
        buttons = [[InlineKeyboardButton('⇇ ᴄʟᴏsᴇ ⇉', callback_data='close')]]
        await m.reply_text(
            "**ʜᴇʏ 👋\n\n<u>ɢɪᴠᴇ ᴛʜᴇ ᴄᴀᴩᴛɪᴏɴ</u>\n\nᴇxᴀᴍᴩʟᴇ:- `/set_caption <b>{file_name}\n\nSize : {file_size}\n\n➠ Fast Download Link :\n{download_link}\n\n➠ Watch Link : {watch_link}\n\n☠️ Powered By : @OMGxLinks</b>`**",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    caption = m.text.split(" ", 1)[1]
    await db.set_caption(m.from_user.id, caption=caption)
    buttons = [[InlineKeyboardButton('⇇ ᴄʟᴏsᴇ ⇉', callback_data='close')]]
    ok = await m.reply_text(f"<b>ʜᴇʏ {m.from_user.mention}\n\n✅ Caption successfully added and saved</b>", reply_markup=InlineKeyboardMarkup(buttons))
    await asyncio.sleep(5)
    await ok.delete()
    await m.delete()

# Command to delete caption
@StreamBot.on_message(filters.group & filters.command('del_caption'))
async def delete_caption(c: Client, m: Message):
    caption = await db.get_caption(m.from_user.id)
    if not caption:
        await m.reply_text("__**😔 You don't have any caption**__")
        return

    await db.set_caption(m.from_user.id, caption=None)
    buttons = [[InlineKeyboardButton('⇇ ᴄʟᴏsᴇ ⇉', callback_data='close')]]
    g = await m.reply_text(f"<b>ʜᴇʏ {m.from_user.mention}\n\n✅ Caption successfully deleted</b>", reply_markup=InlineKeyboardMarkup(buttons))
    await asyncio.sleep(5)
    await g.delete()
    await m.delete()

# Command to see/view caption
@StreamBot.on_message(filters.group & filters.command(['see_caption', 'view_caption']))
async def see_caption(c: Client, m: Message):
    caption = await db.get_caption(m.from_user.id)
    if caption:
        await m.reply_text(f"**Your caption:-**\n\n`{caption}`")
    else:
        await m.reply_text("__**😔 You don't have any caption**__")

# Handle media messages
@StreamBot.on_message(filters.group & (filters.document | filters.video | filters.audio | filters.photo), group=4)
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
    file_name = m.caption or ""
    file_name = file_name.replace(".mkv", "").replace("HEVC", "#HEVC").replace("Sample video.", "#SampleVideo").replace(",", " ")

    try:
        user = await db.get_user(m.from_user.id)
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)

        # Generate stream and download links
        hs_stream_link = f"{Var.URL}watch/{log_msg.id}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        stream_link = await short_link(hs_stream_link, user)

        hs_online_link = f"{Var.URL}{log_msg.id}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        online_link = await short_link(hs_online_link, user)

        await log_msg.reply_text(
            f"**Requested by :** [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n**User ID :** `{m.from_user.id}`\n**Stream link :** {stream_link}",
            disable_web_page_preview=True, quote=True
        )

        # Caption formatting
        c_caption = await db.get_caption(m.from_user.id)
        caption = None
        if c_caption:
            caption = c_caption.format(
                file_name=file_name,
                file_size=humanbytes(get_media_file_size(m)),
                download_link=online_link,
                watch_link=stream_link
            )

        # Send cached media with the caption
        await c.send_cached_media(
            chat_id=m.chat.id,
            file_id=media.file_id,
            caption=caption
        )

        buttons = [[InlineKeyboardButton('⇇ ᴄʟᴏsᴇ ⇉', callback_data='close')]]
        await m.reply(
            "<b>❗⚠️ Important Notice! This file will be deleted in 10 minutes due to overuse! Please forward/save it!</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except FloodWait as e:
        logger.error(f"FloodWait encountered: {e.x} seconds.")
        await asyncio.sleep(e.x)
        await c.send_message(
            chat_id=Var.BIN_CHANNEL,
            text=f"Got FloodWait of {e.x} seconds from [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n**User ID :** `{m.from_user.id}`",
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Error processing media message: {str(e)}")
        await m.reply("❌ Failed to process your request due to an internal error.")

# Shorten link with optional user details
async def short_link(link, user=None):
    retries = 3
    while retries > 0:
        try:
            if not user:
                return link

            api_key = user.get("shortner_api")
            base_site = user.get("shortner_url")

            if api_key and base_site and Var.USERS_CAN_USE:
                shortzy = Shortzy(api_key, base_site)
                return await shortzy.convert(link)
            return link
        except aiohttp.ClientResponseError as e:
            logger.error(f"Shortener Error: Status={e.status}, {await e.response.text()}")
            if e.status in {429, 503}:
                retries -= 1
                await asyncio.sleep(2)
            else:
                break
        except Exception as e:
            logger.error(f"Unexpected error during shortening: {e}")
            break
    return link

# Callback handler for closing buttons
@StreamBot.on_callback_query(filters.regex(r"^close$"))
async def close_button(c: Client, cb: CallbackQuery):
    await cb.message.delete()
    try:
        await cb.message.reply_to_message.delete()
    except:
        pass
    await cb.answer()

# Run the bot
if __name__ == "__main__":
    StreamBot.run()
    
