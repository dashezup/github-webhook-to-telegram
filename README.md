## GitHub Webhook to Telegram

Receive GitHub webhook events and send to Telegram chats
with [AIOHTTP](https://github.com/aio-libs/aiohttp)
through [Telegram Bot API](https://core.telegram.org/bots/api#sendmessage)

What this project do is very simple, it does not use any Telegram Bot API
framework/library nor receive updates from Telegram, but calling `sendMessage`
method of Telegram Bot API directly by sending `GET` requests through AIOHTTP.
It should be able to be used along with any existing Telegram bot without
conflicts.

1. Receive GitHub webhooks (`POST` request)
2. Verify the SHA256 signature
3. Format and send the text to a Telegram chat through "sendMessage" method of
   Telegram Bot API (`GET` request)

### Setup

You need a Telegram bot token, create a Telegram bot with
[BotFather](https://t.me/BotFather) if you don't have one yet.

#### Configuration

1. Go to your GitHub project `Settings - Webhooks - Add webhook`, fill "Payload
   URL", "Content Type" (must be `application/json`) and "Secret". You can also
   do this after start running the project.
2. Create a new `config.py` file based on this template. `chat_id` can be
   user/group/channel id (integer) or username (string), just make sure the bot
   is started or member of the chat with permission to send messages
   ```
   BOT_TOKEN = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
   PORT = 12345

   GH_WEBHOOKS = {
       "Codertocat/Hello-World": {
           "chat_id": -1001234567890,
           "secret": "FPAh9pwRHCLpRL7j"
       },
       "Octocoders/Hello-World": {
           "chat_id": "@username",
           "secret": "H4xvfPNCnUhPTERq"
       }
   }
   ```
3. Configure reverse proxy for this app, corresponding configuration for Nginx
   looks like this
   ```
   location /github {
       rewrite ^/github(.*) /$1 break;
       proxy_pass http://127.0.0.1:12345;
   }
   ```

#### Run

```
virtualenv venv
venv/bin/pip install -U -r requirements.txt
venv/bin/python main.py
```

### LICENSE

AGPL-3.0-or-later

```

    github-webhook-to-telegram, receive GitHub webhooks and send to Telegram
    Copyright (C) 2021  Dash Eclipse

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

```
