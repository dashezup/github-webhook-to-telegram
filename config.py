import json
from os import environ

if environ.get('DYNO'):
    data = json.loads(environ.get("HOOK_CONFIG"))
    PORT = int(environ.get('PORT'))
else:
    with open("config.json") as f:
        data = json.load(f)
    PORT = data.get('port')

BOT_TOKEN = data['bot_token']
GH_WEBHOOKS = data['gh_webhooks']
