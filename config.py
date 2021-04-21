import json
from os import environ

if environ.get('DYNO'):
    data = json.loads(environ.get("HOOK_CONFIG"))
else:
    with open("config.json") as f:
        data = json.load(f)

BOT_TOKEN = data['bot_token']
PORT = data.get('port')
GH_WEBHOOKS = data['gh_webhooks']
