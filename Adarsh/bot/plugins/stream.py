#(c) Adarsh-Goel
import os
import random
import asyncio
#from Script import script
from asyncio import TimeoutError
from Adarsh.bot import StreamBot
from Adarsh.utils.database import Database
from Adarsh.utils.human_readable import humanbytes
from Adarsh.vars import Var
from urllib.parse import quote_plus
from pyrogram import filters, Client, enums
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from shortzy import Shortzy

from Adarsh.utils.file_properties import get_name, get_hash, get_media_file_size
db = Database(Var.DATABASE_URL, Var.name)


MY_PASS = os.environ.get("MY_PASS", None)
pass_dict = {}
pass_db = Database(Var.DATABASE_URL, "ag_passwords")

class temp(object):
    U_NAME = None
    B_NAME = None

@StreamBot.on_message(filters.group & filters.command('set_caption'))
async def add_caption(c: Client, m: Message):
    if len(m.command) == 1:
       buttons = [[InlineKeyboardButton('⇇ ᴄʟᴏsᴇ ⇉', callback_data='close') ]]
       return await m.reply_text("**ʜᴇʏ 👋\n\n<u>ɢɪᴠᴇ ᴛʜᴇ ᴄᴀᴩᴛɪᴏɴ</u>\n\nᴇxᴀᴍᴩʟᴇ:- `/set_caption <b>{file_name}\n\nSize : {file_size}\n\n➠ Fast Download Link :\n{download_link}\n\n➠ watch Download Link : {watch_link}\n\n☠️ Powered By : @OMGxLinks</b>`**", reply_markup=InlineKeyboardMarkup(buttons))
    caption = m.text.split(" ", 1)[1]
    await db.set_caption(m.from_user.id, caption=caption)
    buttons = [[InlineKeyboardButton('⇇ ᴄʟᴏsᴇ ⇉', callback_data='close') ]]
    h = await m.reply_sticker("CAACAgIAAxkBAAIBv2TgRm4xVkSMno1IJxfgM-zQSfSvAAIHCQAC-rI5SZwTbXRmStwTHgQ")
    ok = await m.reply_text("<b>ʜᴇʏ {}\n\n✅ sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ᴀᴅᴅ ʏᴏᴜʀ ᴄᴀᴩᴛɪᴏɴ ᴀɴᴅ sᴀᴠᴇᴅ</b>".format(m.from_user.mention, temp.U_NAME, temp.B_NAME), reply_markup=InlineKeyboardMarkup(buttons))
    await asyncio.sleep(5)
    await h.delete(2)
    await ok.delete()
    await m.delete()
    
@StreamBot.on_message(filters.group & filters.command('del_caption'))
async def delete_caption(c: Client, m: Message):
    caption = await db.get_caption(m.from_user.id)  
    if not caption:
       return await m.reply_text("__**😔 Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Aɴy Cᴀᴩᴛɪᴏɴ**__")
    await db.set_caption(m.from_user.id, caption=None)
    buttons = [[InlineKeyboardButton('⇇ ᴄʟᴏsᴇ ⇉', callback_data='close') ]]
    uh = await m.reply_sticker("CAACAgIAAxkBAAIBv2TgRm4xVkSMno1IJxfgM-zQSfSvAAIHCQAC-rI5SZwTbXRmStwTHgQ")
    g = await m.reply_text("<b>ʜᴇʏ {}\n\n✅ sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ʏᴏᴜʀ ᴄᴀᴩᴛɪᴏɴ</b>".format(m.from_user.mention, temp.U_NAME, temp.B_NAME), reply_markup=InlineKeyboardMarkup(buttons))
    await asyncio.sleep(5)
    await uh.delete(2)
    await g.delete()
    await m.delete()

@StreamBot.on_message(filters.group & filters.command(['see_caption', 'view_caption']))
async def see_caption(c: Client, m: Message):
    caption = await db.get_caption(m.from_user.id)  
    if caption:
       await m.reply_text(f"**ʏᴏᴜ'ʀᴇ ᴄᴀᴩᴛɪᴏɴ:-**\n\n`{caption}`")
    else:
       await m.reply_text("__**😔 ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ᴄᴀᴩᴛɪᴏɴ**__")


@StreamBot.on_message((filters.group) & (filters.document | filters.video | filters.audio | filters.photo) , group=4)
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

    if (m.document or m.video or m.audio): 
        if m.caption:                        
           file_name = f"{m.caption}"                
        else:
           file_name = ""
    file_name = file_name.replace(".mkv", "")
    file_name = file_name.replace("HEVC", "#HEVC")
    file_name = file_name.replace("Sample video.", "#SampleVideo")
    file_name = file_name.replace(".", " ")
        #return
    
    try:
        user = await db.get_user(m.from_user.id)   
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
        
        hs_stream_link = f"{Var.URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        stream_link = await short_link(hs_stream_link, user)
        
        hs_online_link = f"{Var.URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        online_link = await short_link(hs_online_link, user)
       
        await log_msg.reply_text(text=f"**RᴇQᴜᴇꜱᴛᴇᴅ ʙʏ :** [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n**Uꜱᴇʀ ɪᴅ :** `{m.from_user.id}`\n**Stream ʟɪɴᴋ :** {stream_link}", disable_web_page_preview=True,  quote=True)
        c_caption = await db.get_caption(m.from_user.id)
        if c_caption:
            try:
                caption=c_caption.format(file_name ='' if file_name is None else file_name, file_size=humanbytes(get_media_file_size(m)), download_link=online_link, watch_link=stream_link)
            except Exception as e:
                return
            else:
                caption=caption.format(file_name ='' if file_name is None else file_name, file_size=humanbytes(get_media_file_size(m)), download_link=online_link, watch_link=stream_link)
        op = await m.reply_sticker("CAACAgIAAxkBAAIBvmTgRm76VICSvZ67FSwRmUwH2ogDAAJxCAAChJRBSW9oCRqmu85zHgQ")
        await asyncio.sleep(2)
        await op.delete()
        msg = await c.send_cached_media(
            caption=caption,
            chat_id=m.chat.id,
            file_id=media.file_id
        )
        buttons = [[InlineKeyboardButton('⇇ ᴄʟᴏsᴇ ⇉', callback_data='close') ]]
        hs = k = await msg.reply("<b>❗⚠️❗🚨 ɪᴍᴘᴏʀᴛᴀɴᴛ 🚨❗⚠️❗️\n\n🎭 ᴛʜɪꜱ ᴍᴏᴠɪᴇ ғɪʟᴇ/ᴠɪᴅᴇᴏ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪɴ <code>𝟷𝟶 ᴍɪɴꜱ</code>\n\n🔎 ᴅᴜᴇ ᴛᴏ ᴄᴏᴘʏʀɪɢʜᴛ ɪsꜱᴜᴇꜱ 🔎\n\n🥀 ᴘʟᴇᴀꜱᴇ ғᴏʀᴡᴀʀᴅ ᴛʜɪꜱ ғɪʟᴇ/ᴠɪᴅᴇᴏ ᴛᴏ ʏᴏᴜʀ Sᴀᴠᴇᴅ ᴍᴇꜱꜱᴀɢᴇꜱ ᴀɴᴅ sᴛᴀʀᴛ ᴅᴏᴡɴʟᴏᴀᴅ ᴛʜᴇʀᴇ</b>",quote=True)
        await asyncio.sleep(600)
        await msg.delete()
        await hs.delete()
        del msg, hs
        u = await k.reply_sticker("CAACAgIAAxkBAAIBuGTgP9O80ox5ll9VbTKM8y-Kj6b1AAK5DgACbG7wSanYX9efd6YGHgQ")
        await asyncio.sleep(1)
        await u.delete()
        x = await k.reply_photo(photo=random.choice(Var.DELETE_PICS),caption="<b>🥀 ʏᴏᴜʀ ғɪʟᴇ/ᴠɪᴅᴇᴏ ɪꜱ ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ!!!✅\n\n~ ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ ›› <a href='https://t.me/Hari_OP'>ʜᴀʀɪ ᠰ ᴛɢ​</a></b>",reply_markup=InlineKeyboardMarkup(buttons))
        await asyncio.sleep(8)
        await x.delete()
        await k.delete()
        del x, k
            
    except FloodWait as e:
        print(f"Sleeping for {str(e.x)}s")
        await asyncio.sleep(e.x)
        await c.send_message(chat_id=Var.BIN_CHANNEL, text=f"Gᴏᴛ FʟᴏᴏᴅWᴀɪᴛ ᴏғ {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n**𝚄𝚜𝚎𝚛 𝙸𝙳 :** `{str(m.from_user.id)}`", disable_web_page_preview=True)

async def short_link(link, user=None):
    if not user:
        return link

    api_key = user.get("shortner_api")
    base_site = user.get("shortner_url")

    if bool(api_key and base_site) and Var.USERS_CAN_USE:
        shortzy = Shortzy(api_key, base_site)
        link = await shortzy.convert(link)

    return link
