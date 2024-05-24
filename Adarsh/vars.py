# (c) adarsh-goel
import os, re
from os import getenv, environ
from dotenv import load_dotenv
id_pattern = re.compile(r'^.\d+$') 


load_dotenv()

class Var(object):
    MULTI_CLIENT = False
    API_ID = int(getenv('API_ID', ""))
    API_HASH = str(getenv('API_HASH', ""))
    BOT_TOKEN = str(getenv('BOT_TOKEN', ""))
    name = str(getenv('name', 'filetolinkbot'))
    SLEEP_THRESHOLD = int(getenv('SLEEP_THRESHOLD', ''))
    WORKERS = int(getenv('WORKERS', ''))
    CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", "<b>ɴᴀᴍᴇ : {file_name}\n\nꜱɪᴢᴇ : {file_size}</b>")
    BIN_CHANNEL = int(getenv('BIN_CHANNEL', "-1001682397310"))
    DELETE_PICS = (environ.get('DELETE_PICS', 'https://telegra.ph/file/f58fbfbf2774cc93f5e14.jpg')).split()
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", '-1001870015374'))
    PERMANENT_GROUP = os.environ.get("PERMANENT_GROUP", "-1002120533046")
    GROUP_ID = [int(ch) for ch in (os.environ.get("GROUP_ID", f"{PERMANENT_GROUP}")).split()]
    FORCE_SUB   = os.environ.get("FORCE_SUB", "SK_MoviesOffl")
    PORT = int(getenv('PORT', "8"))
    BIND_ADRESS = str(getenv('WEB_SERVER_BIND_ADDRESS', ''))
    PING_INTERVAL = int(environ.get("PING_INTERVAL", "11"))  # 20 minutes
    ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '1426588906').split()]
    OWNER_ID = set(int(x) for x in os.environ.get("OWNER_ID", "5821871362").split())  
    NO_PORT = bool(getenv('NO_PORT', False))
    APP_NAME = str(getenv('APP_NAME'))
    OWNER_USERNAME = str(getenv('OWNER_USERNAME'))
    if 'DYNO' in environ:
        ON_HEROKU = True
        APP_NAME = str(getenv('APP_NAME'))
    
    else:
        ON_HEROKU = False
    #FQDN = str(getenv('FQDN', '167.172.134.62:8282')) if not ON_HEROKU or getenv('FQDN', '167.172.134.62:8282') else APP_NAME+'.herokuapp.com'
    FQDN = str(getenv('FQDN', BIND_ADRESS)) if not ON_HEROKU or getenv('FQDN') else APP_NAME+'.herokuapp.com'
    HAS_SSL=bool(getenv('HAS_SSL',False))
    if HAS_SSL:
        URL = "https://{}/".format(FQDN)
    else:
        URL = "http://{}/".format(FQDN)
    USERS_CAN_USE = getenv('USERS_CAN_USE', True)
    DATABASE_URL = str(getenv('DATABASE_URL', "mongodb+srv://sankar:sankar@sankar.lldcdsx.mongodb.net/?retryWrites=true&w=majority"))
    UPDATES_CHANNEL = str(getenv('UPDATES_CHANNEL', None))
    BANNED_CHANNELS = list(set(int(x) for x in str(getenv("BANNED_CHANNELS", "-1001362659779")).split())) 
