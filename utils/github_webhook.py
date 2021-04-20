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
import hmac
import logging
from hashlib import sha256
from json.decoder import JSONDecodeError
from typing import Optional

from aiohttp.web_request import Request
from multidict import CIMultiDictProxy

from config import GH_WEBHOOKS


async def validate_github_webhook(request: Request) -> bool:
    try:
        headers = request.headers
        if not headers.get('User-Agent').startswith('GitHub-Hookshot'):
            logging.warning("User agent: not from GitHub")
            return False
        if headers.get('Content-Type') != 'application/json':
            logging.warning("Content type: not json")
            return False
        payload = await request.json()
        repo_name = payload['repository']['full_name']
        if repo_name not in GH_WEBHOOKS.keys():
            logging.warning("Repository: not in configuration")
            return False
        return await _verify_signature(
            bytes(GH_WEBHOOKS[repo_name]['secret'], 'UTF-8'),
            headers.get('X-Hub-Signature-256').split('=')[1],
            await request.read()
        )
    except (JSONDecodeError, AttributeError) as error:
        logging.warning("Invalid: %s", error)
        return False


async def _verify_signature(secret: bytes, sig: str, msg: bytes) -> bool:
    mac = hmac.new(secret, msg=msg, digestmod=sha256)
    valid_signature = hmac.compare_digest(mac.hexdigest(), sig)
    if not valid_signature:
        logging.warning("Invalid signature")
    return valid_signature


async def format_github_webhook(request: Request) -> Optional[str]:
    headers: CIMultiDictProxy[str] = request.headers
    event: str = headers.get('X-GitHub-Event')
    payload: dict = await request.json()
    if event in ALL_EVENTS:
        title = await _get_event_title(event, payload)
        details = await globals()[f"_format_{event}"](payload)
        return f"{title}\n{details}" if details else title
    return None


async def _format_create(payload: dict) -> str:
    return "\u2192 <a href=\"{url}\">{ref_type}: {ref}</a>".format(
        url=f"{payload['repository']['html_url']}/tree/{payload['ref']}",
        ref_type=payload['ref_type'],
        ref=payload['ref']
    )


async def _format_delete(payload: dict) -> str:
    return "\u2192 {ref_type}: <code>{ref}</code>".format(
        ref_type=payload['ref_type'],
        ref=payload['ref']
    )


async def _format_discussion(payload: dict) -> str:
    discussion = payload['discussion']
    url = discussion['html_url']
    title = f"{discussion['title']} \u00b7 Discussion #{discussion['number']}"
    return f"\u2192 <a href=\"{url}\">{title}</a>"


async def _format_fork(payload: dict) -> str:
    forkee = payload['forkee']
    return "\u2192 <a href=\"{url}\">{name}</a>".format(
        url=forkee['html_url'],
        name=forkee['full_name']
    )


async def _format_issues(payload: dict) -> str:
    issue = payload['issue']
    return "\u2192 <a href=\"{url}\">{title}</a>".format(
        url=issue['html_url'],
        title=f"{issue['title']} \u00b7 Issue #{issue['number']}"
    )


async def _format_ping(payload: dict) -> str:
    repository = payload['repository']
    return "\u2192 <a href=\"{url}\">{name}</a>".format(
        url=repository['html_url'],
        name=repository['full_name']
    )


async def _format_public(payload: dict) -> str:
    repo = payload['repository']
    return "\u2192 <a href=\"{url}\">{name}</a>".format(
        url=repo['html_url'],
        name=repo['full_name']
    )


async def _format_pull_request(payload: dict) -> str:
    pr = payload['pull_request']
    url = pr['html_url']
    user = pr['user']['login']
    title = f"{pr['title']} by {user} \u00b7 Pull Request #{payload['number']}"
    return f"\u2192 <a href=\"{url}\">{title}</a>"


async def _format_push(payload: dict) -> str:
    ref = [f"\u2192 {payload['ref']}"]
    commits = payload['commits']
    commits_list = [
        "\u2192 "
        "<code>{name}</code> {message} [<a href=\"{url}\">{cid}</a>]".format(
            name=commit['author']['username'],
            message=commit['message'],
            url=commit['url'],
            cid=commit['id'][:7]
        )
        for commit in commits
    ]
    return "\n".join(ref + commits_list)


async def _format_star(payload: dict) -> str:
    time = payload['starred_at']
    text = [f"\u2192 starred at <code>{time}</code>"] if time else []
    text.append(await _get_repo_watch_star_fork(payload['repository']))
    return "\n".join(text)


async def _format_watch(payload: dict) -> str:
    return await _get_repo_watch_star_fork(payload['repository'])


async def _get_event_title(event: str, payload: dict) -> str:
    sender = payload['sender']['login']
    action = payload.get('action') or ''
    return "<b>{name}</b> | <i>{summary}</i>".format(
        name=payload['repository']['full_name'],
        summary=" ".join([sender, action, event])
    )


async def _get_repo_watch_star_fork(repo: dict) -> str:
    return '\u2192 ' + ", ".join([
        f"<b>{repo['watchers_count']}</b> watchers",
        f"<b>{repo['stargazers_count']}</b> stargazers",
        f"<b>{repo['forks_count']}</b> forks"
    ])


ALL_EVENTS = tuple(
    i.removeprefix('_format_') for i in dir() if i.startswith('_format_')
)
