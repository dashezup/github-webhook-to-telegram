from json import loads
from os import environ

BOT_TOKEN = environ.get("BOT_TOKEN")
PORT = int(environ.get("PORT", "5000"))
GH_WEBHOOKS = loads(environ.get("GH_WEBHOOKS", "{}"))
