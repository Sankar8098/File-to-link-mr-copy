import asyncio
import logging
import sys
import glob
import importlib.util
from pathlib import Path
from aiohttp import web
from pyrogram import idle
from .bot import StreamBot
from .vars import Var
from .server import web_server
from .utils.keepalive import ping_server
from .bot.clients import initialize_clients

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

ppath = "Adarsh/bot/plugins/*.py"
files = glob.glob(ppath)

loop = asyncio.get_event_loop()

async def start_services():
    print('------------------- Initializing Telegram Bot -------------------')
    await StreamBot.start()
    bot_info = await StreamBot.get_me()
    StreamBot.username = bot_info.username
    print(f"Bot Username: {StreamBot.username}")

    print("\n---------------------- Initializing Clients ----------------------")
    await initialize_clients()
    
    print('\n--------------------------- Importing Plugins ---------------------------')
    for name in files:
        with open(name) as a:
            plugin_name = Path(a.name).stem
            plugins_dir = Path(f"Adarsh/bot/plugins/{plugin_name}.py")
            import_path = f".plugins.{plugin_name}"
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules[f"Adarsh.bot.plugins.{plugin_name}"] = load
            print(f"Imported => {plugin_name}")
    
    if Var.ON_HEROKU:
        print("\n------------------ Starting Keep Alive Service ------------------")
        asyncio.create_task(ping_server())

    print('-------------------- Initializing Web Server -------------------------')
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0" if Var.ON_HEROKU else Var.BIND_ADDRESS
    await web.TCPSite(app, bind_address, Var.PORT).start()
    
    print('\n----------------------- Service Started ---------------------------')
    print(f"Bot =>> {bot_info.first_name}")
    print(f"Server IP =>> {bind_address}:{Var.PORT}")
    print(f"Owner =>> {Var.OWNER_USERNAME}")
    if Var.ON_HEROKU:
        print(f"App running on =>> {Var.FQDN}")
    print('--------------------------------------------------------------')
    await idle()

if __name__ == "__main__":
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        logging.info('----------------------- Service Stopped -----------------------')
    
