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
import logging
from typing import Optional
from typing import Union

from aiohttp import ClientSession, ClientResponse
from aiohttp.web_request import Request

from config import BOT_TOKEN, GH_WEBHOOKS
from utils.github_webhook import format_github_webhook


async def send_to_telegram(session: ClientSession, request: Request) -> str:
    message_text: Optional[str] = await format_github_webhook(request)
    chat_id: int = await get_corresponding_chat_id(await request.json())
    if not message_text:
        tg_status = "nothing to send"
    else:
        tg_succeed: bool = await send_message(session, chat_id, message_text)
        tg_status: str = f"{'succeed' if tg_succeed else 'failed'}"
    return tg_status


async def get_corresponding_chat_id(payload: dict) -> int:
    repo_name = payload['repository']['full_name']
    return GH_WEBHOOKS[repo_name]['chat_id']


async def send_message(session: ClientSession,
                       chat_id: Union[int, str],
                       text: str) -> bool:
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = dict(
        chat_id=chat_id,
        text=text,
        parse_mode='HTML',
        disable_web_page_preview=True
    )
    async with session.post(api_url,
                            data=data) as resp:  # type: ClientResponse
        logging.info('%s, %s, %s', str(chat_id), str(resp.status), repr(text))
        tg_response = await resp.json()
        logging.info("Telegram response: %s", tg_response)
        msg_link = await get_telegram_message_link(tg_response)
    return bool(msg_link)


async def get_telegram_message_link(json_data: dict) -> Optional[str]:
    result = json_data.get('result')
    if not result:
        logging.error("no result for link")
        return None
    msg_link = "https://t.me/{chat_id}/{message_id}".format(
        message_id=result['message_id'],
        chat_id=int(str(result['chat']['id']).removeprefix('-100'))
    )
    logging.info(msg_link)
    return msg_link
