#Adarsh goel
from Adarsh.bot import StreamBot
from Adarsh.vars import Var
import logging , asyncio
import asyncio
logger = logging.getLogger(__name__)
from Adarsh.bot.plugins.stream import MY_PASS
from Adarsh.utils.human_readable import humanbytes
from Adarsh.utils.database import Database
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import UserNotParticipant
from Adarsh.utils.file_properties import get_name, get_hash, get_media_file_size
db = Database(Var.DATABASE_URL, Var.name)
from pyrogram.types import ReplyKeyboardMarkup

async def not_subscribed(_, client, message):
    await db.hs_add_user(client, message)
    if not Var.FORCE_SUB:
        return False
    try:             
        user = await client.get_chat_member(Var.FORCE_SUB, message.from_user.id) 
        if user.status == enums.ChatMemberStatus.BANNED:
            return True 
        else:
            return False                
    except UserNotParticipant:
        pass
    return True

class temp(object):
    U_NAME = None
    B_NAME = None
    

@StreamBot.on_message(filters.group & filters.create(not_subscribed))
async def forces_sub(client, message):
    buttons = [[InlineKeyboardButton(text="🥀 ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ 🥀", url=f"https://t.me/{Var.FORCE_SUB}") ]]
    text = "**ʜᴇʏ {}\n\nsᴏʀʀʏ ᴅᴜᴅᴇ ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴊᴏɪɴᴇᴅ ᴍʏ ᴄʜᴀɴɴᴇʟ 😐. sᴏ ᴘʟᴇᴀꜱᴇ ᴊᴏɪɴ ᴏᴜʀ ᴜᴩᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ**"
    try:
        user = await client.get_chat_member(Var.FORCE_SUB, message.from_user.id)    
        if user.status == enums.ChatMemberStatus.BANNED:                                   
            return await client.send_message(message.from_user.id, text="Sᴏʀʀy Yᴏᴜ'ʀᴇ Bᴀɴɴᴇᴅ Tᴏ Uꜱᴇ Mᴇ")  
    except UserNotParticipant:                       
        hari = await message.reply_text(text=text.format(message.from_user.mention, temp.U_NAME, temp.B_NAME), reply_markup=InlineKeyboardMarkup(buttons))
        await asyncio.sleep(30)
        await hari.delete()
        await message.delete()
    ms = await message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    await asyncio.sleep(0)
    await ms.delete()
    await message.delete()

                      
@StreamBot.on_message(filters.command(["start"]) & filters.text & filters.incoming)
async def start(client, message):
    if message.chat.type == enums.ChatType.PRIVATE:
        keyboard = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("✨ ʜꜱ ᠰ ʙᴏᴛꜱ", url="https://t.me/Hs_Botz"),
                InlineKeyboardButton("⛈️ ᴏᴍɢ x ᴄʟᴏᴜᴅ", url="https://t.me/OMGxCLOUD")
            ],[
                InlineKeyboardButton("📝 ʀᴇǫᴜᴇsᴛ ʜᴇʀᴇ ɢʀᴏᴜᴏ 📌", url="https://t.me/+UUCSKv1Mwj1iYWZl")
            ],[
                InlineKeyboardButton("🎭 ʜᴇʟᴘ 🎭", callback_data = "help"),
                InlineKeyboardButton("♻️ ᴀʙᴏᴜᴛ ♻️", callback_data = "about")
            ]]
        )
        await db.hs_add_user(client, message)
        await message.reply_photo(
            photo="https://graph.org/file/5921f2a1d887c6cc2d8aa.jpg",
            caption=(script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME)),
            #disable_web_page_preview=True,
            reply_markup=keyboard)
        
    elif message.chat.type == enums.ChatType.GROUP or enums.ChatType.SUPERGROUP:
        keyboar = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⛈️ ᴏᴍɢ x ᴄʟᴏᴜᴅ ⛈️", url=f"https://t.me/OMGxCLOUD")
                ]
            ]
        )
        await db.hs_add_user(client, message)
        mr = await message.reply_text("<b>👋 ʜᴇʟʟᴏ {}!\n\nɪ» ɪ ᴀᴍ ᴀ ᴘᴏᴡᴇʀꜰᴜʟʟ ғᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ ᴀɴᴅ ᴡᴀᴄᴛʜ ʟɪɴᴋ ʙᴏᴛ\n\ᴡᴏʀᴋɪɴɢ ᴛʜɪs ɢʀᴏᴜᴘ ᴏɴʟʏ - <a href='https://t.me/+Tg9FFZ_4dQk3Y2Q1'>ʜᴇʀᴇ​</a>\n\n» ᴊᴏɪɴ ᴏᴜʀ ᴄʟᴏᴜᴅ ᴄʜᴀɴɴᴇʟ !!</b>".format(message.from_user.mention, temp.U_NAME, temp.B_NAME), disable_web_page_preview=True, reply_markup=keyboar)
        await asyncio.sleep(30)
        await mr.delete()
        await message.delete()


@StreamBot.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data 
    user = query.from_user
    message = query.message
    if data == "start":
        await query.message.edit_text(
            text=(script.START_TXT.format(query.from_user.mention)),
            #disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton("✨ ʜꜱ ᠰ ʙᴏᴛꜱ", url="https://t.me/Hs_Botz"),
                    InlineKeyboardButton("⛈️ ᴏᴍɢ x ᴄʟᴏᴜᴅ", url="https://t.me/OMGxCLOUD")
                ],[
                    InlineKeyboardButton("📝 ʀᴇǫᴜᴇsᴛ ʜᴇʀᴇ ɢʀᴏᴜᴘ 📌", url="https://t.me/+UUCSKv1Mwj1iYWZl")
                ],[
                    InlineKeyboardButton("🎭 ʜᴇʟᴘ 🎭", callback_data = "help"),
                    InlineKeyboardButton("♻️ ᴀʙᴏᴜᴛ ♻️", callback_data = "about")
                ]]
            )
        )
    elif data == "help":
        await query.message.edit_text(
            text=(script.HELP_TXT),
            #disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup( [[
               InlineKeyboardButton("⇇ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇉", callback_data = "start")
               ]]
            )
        )
    elif data == "about":
        await query.message.edit_text(
            text=(script.ABOUT_TXT),
            #disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[    
               InlineKeyboardButton("⇇ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇉", callback_data = "start")
               ]]
            )
        )
    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
        except:
            await query.message.delete()

@StreamBot.on_message(filters.command('comments') & filters.group)
async def about_handler(bot, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        await bot.send_message(
            Var.BIN_CHANNEL,
            f"#NEW_USER: \n\nNew User [{message.from_user.first_name}](tg://user?id={message.from_user.id}) Started !!"
        )
    hs=await message.reply_photo(
             photo="https://graph.org/file/68a0935f0d19ffd647a09.jpg",
             caption=(script.COMMENTS_TXT.format(message.from_user.mention)),
             reply_markup=InlineKeyboardMarkup(
                [[
                  InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data = "close")
                ]]
            ),
            
    )
    await asyncio.sleep(20)
    await hs.delete()
    await message.delete()

@StreamBot.on_message(filters.command('stats') & filters.incoming)
async def get_ststs(bot, message):
    rju = await message.reply('<b>ᴀᴄᴄᴇssɪɴɢ sᴛᴀᴛᴜs ᴅᴇᴛᴀɪʟs...</b>')
    total_users = await db.total_users_count()
    totl_chats = await db.total_chat_count()
    buttons = [[InlineKeyboardButton('⇇ ᴄʟᴏsᴇ ⇉', callback_data='close') ]]
    i = await rju.edit_text(text=script.STATUS_TXT.format(total_users, totl_chats), reply_markup=InlineKeyboardMarkup(buttons))
    await asyncio.sleep(20)
    await i.delete()
    #await message.delete()
    
@StreamBot.on_message(filters.command("shortner_api") & filters.group)
async def shortner_api_handler(bot, m):
    user_id = m.from_user.id
    user = await db.get_user(user_id)
    api = user.get("shortner_api")
    cmd = m.command
    if len(cmd) == 1:
        text = f"<b>👋 ʜᴇʏ\n\nᴄᴜʀʀᴇɴᴛ sʜᴏʀᴛɴᴇʀ ᴀᴘɪ :\n<code>{api}</code>\n\nᴇx</b>:<code>/shortner_api ec8ba7deff6128848def53bf2d4e69608443cf27</code>\n\n<b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ - <a href='https://t.me/Hs_Botz'>ʜꜱ ᠰ ʙᴏᴛꜱ</a></b>"
        buttons = [[InlineKeyboardButton('⇇ ᴄʟᴏsᴇ ⇉', callback_data='close') ]]
        return await m.reply(text= text, reply_markup=InlineKeyboardMarkup(buttons) ,disable_web_page_preview=True)
    elif len(cmd) == 2:
        api = cmd[1].strip()
        await db.update_user_info(user_id, {"shortner_api": api})
        buttons = [[InlineKeyboardButton('⇇ ᴄʟᴏsᴇ ⇉', callback_data='close') ]]
        mi = await m.reply_sticker("CAACAgIAAxkBAAIBv2TgRm4xVkSMno1IJxfgM-zQSfSvAAIHCQAC-rI5SZwTbXRmStwTHgQ")
        await asyncio.sleep(1)
        await mi.delete()
        n = await m.reply("<b>👋 ʜᴇʏ {}\n\n✅ sʜᴏʀᴛᴇɴᴇʀ ᴀᴘɪ ᴜᴘᴅᴀᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ᴛᴏ\n\n~ ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ ›› <a href='https://t.me/Hari_OP'>ʜᴀʀɪ ᠰ ᴛɢ​</a></b>".format(m.from_user.mention, temp.U_NAME, temp.B_NAME), disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(buttons))
        await asyncio.sleep(12)
        await n.delete()
        await m.delete()

@StreamBot.on_message(filters.command("shortner_url") & filters.group)
async def shortner_url_handler(bot, m):
    user_id = m.from_user.id
    user = await db.get_user(user_id)
    cmd = m.command
    site = user.get("shortner_url")
    text = f"<b>👋 ʜᴇʏ\n\nᴄᴜʀʀᴇɴᴛ sʜʀᴛɴᴇʀ ᴜʀʟ :\n<code>{site}</code>\n\n ᴇx</b>: <code>/shortner_url v2.kpslink.in</code>\n\n<b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ - <a href='https://t.me/Hs_Botz'>ʜꜱ ᠰ ʙᴏᴛꜱ</a></b>"
    if len(cmd) == 1:
        buttons = [[InlineKeyboardButton('⇇ ᴄʟᴏsᴇ ⇉', callback_data='close') ]]
        return await m.reply(text=text, reply_markup=InlineKeyboardMarkup(buttons) , disable_web_page_preview=True)
    elif len(cmd) == 2:
        shortner_url = cmd[1].strip()
        await db.update_user_info(user_id, {"shortner_url": shortner_url})
        buttons = [[InlineKeyboardButton('⇇ ᴄʟᴏsᴇ ⇉', callback_data='close') ]]
        mit = await m.reply_sticker("CAACAgIAAxkBAAIBv2TgRm4xVkSMno1IJxfgM-zQSfSvAAIHCQAC-rI5SZwTbXRmStwTHgQ")
        await asyncio.sleep(1)
        await mit.delete()
        hb = await m.reply("<b>👋 ʜᴇʏ {}\n\nsʜᴏʀᴛɴᴇʀ ᴜʀʟ ᴜᴘᴅᴀᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ\n\n~ ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ ›› <a href='https://t.me/Hari_OP'>ʜᴀʀɪ ᠰ ᴛɢ​</a></b>".format(m.from_user.mention, temp.U_NAME, temp.B_NAME), disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(buttons))
        await asyncio.sleep(12)
        await hb.delete()
        await m.delete()

@StreamBot.on_message(filters.command("remove_shortener_api") & filters.group)
async def remove_shortener(c, m):
    user_id = m.from_user.id
    user = await db.get_user(user_id)
    if user.get("shortner_api"):
        await db.update_user_info(user_id, {"shortner_api": None})
        buttons = [[InlineKeyboardButton('⇇ ᴄʟᴏsᴇ ⇉', callback_data='close') ]]
        await m.reply("<b>sʜᴏʀᴛᴇɴᴇʀ ᴀᴘɪ ʀᴇᴍᴏᴠᴇᴅ ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ</b>", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        buttons = [[InlineKeyboardButton('⇇ ᴄʟᴏsᴇ ⇉', callback_data='close') ]]
        await m.reply("<b>ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ꜱʜᴏʀᴛᴇɴᴇʀ ᴀᴘɪ</b>", reply_markup=InlineKeyboardMarkup(buttons))


@StreamBot.on_message(filters.command("remove_shortner_url") & filters.group)
async def remove_shortner(c, m):
    user_id = m.from_user.id
    user = await db.get_user(user_id)
    print(user)
    if user.get("shortner_url"):
        await db.update_user_info(user_id, {"shortner_url": None})
        buttons = [[InlineKeyboardButton('⇇ ᴄʟᴏsᴇ ⇉', callback_data='close') ]]
        await m.reply("<b>sʜᴏʀᴛᴇɴᴇʀ ᴜʀʟ ʀᴇᴍᴏᴠᴇᴅ ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ</b>", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        buttons = [[InlineKeyboardButton('⇇ ᴄʟᴏsᴇ ⇉', callback_data='close') ]]
        await m.reply("<b>ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ꜱʜᴏʀᴛᴇɴᴇʀ ᴜʀʟ</b>", reply_markup=InlineKeyboardMarkup(buttons))
