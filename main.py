"""

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

"""
import asyncio

from aiohttp import web, ClientSession
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from config import PORT
from utils.github_webhook import validate_github_webhook
from utils.telegram import send_to_telegram

# import logging

routes = web.RouteTableDef()


@routes.get("/")
async def main(_):
    return web.Response(status=405, text="405: Method Not Allowed")


@routes.post("/")
async def github_webhook_post_handler(request: Request) -> Response:
    valid_github_webhook = await validate_github_webhook(request)
    if not valid_github_webhook:
        return web.Response(status=403, text="403: Forbidden")
    tg_status = await send_to_telegram(session, request)
    return web.Response(text=f"Send to Telegram: {tg_status}")


async def get_session() -> ClientSession:
    return ClientSession()


async def on_shutdown(_):
    await session.close()


if __name__ == "__main__":
    # FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    # logging.basicConfig(level=logging.INFO, format=FORMAT)
    session: ClientSession \
        = asyncio.get_event_loop().run_until_complete(get_session())
    app = web.Application()
    app.add_routes(routes)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, port=PORT)
