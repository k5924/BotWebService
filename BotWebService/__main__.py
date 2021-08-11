import os
import datetime
import aiohttp

from aiohttp import web

from gidgethub import routing, sansio
from gidgethub import aiohttp as gh_aiohttp

routes = web.RouteTableDef()

router = routing.Router()


@router.register("issues", action="opened")
async def issue_opened_event(event, gh, *args, **kwargs):
    """
    Whenever an issue is opened, greet the author and say thanks.
    """
    url = event.data["issue"]["comments_url"]
    author = event.data["issue"]["user"]["login"]

    message = f"Thanks @{author}!\n\n\nI will report this to @k5924 ASAP!\n\n\nHeres a cookie: 🍪  -- Maid-Chan."
    await gh.post(url, data={"body": message})

    await rate_limit_comment(event, gh)


async def rate_limit_comment(event, gh):
    comments_url = event.data["pull_request"]["comments_url"]
    rate_limit = gh.rate_limit
    remaining = rate_limit.remaining
    total = rate_limit.limit
    reset_datetime = rate_limit.reset_datetime

    if remaining <= 10:
        message = f"\**:WARNING::WARNING::WARNING::WARNING::WARNING:WARNING**:\n\n\nMaid-Chan is reaching near my API limit.\nI have only {remaining} of {total} API requests left. They will reset on {reset_datetime} (GMT), which is in {reset_datetime - datetime.datetime.now(datetime.timezone.gmt)}\n\n\nCookies will OVERLOAD NOW: 🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪🍪."
    await gh.post(comments_url, data={"body": message})


@router.register("pull_request", action="closed")
async def pull_request_closed_event(event, gh, *args, **kwargs):
    """
    Whenever a pull request is closed, check if it has been merged or simply closed
    """
    url = event.data["pull_request"]["issue_url"]
    pr_number = event.data["pull_request"]["number"]
    message = f"Pull Request #{pr_number} was {event.data['action']}."
    if not event.data['pull_request']['merged']:
        message += "\n\n\nIt was closed without merging, skipping\n\n\n-- Maid-Chan"
    else:
        message += "\n\n\nIt was merged to the code base. Heres a cookie: 🍪\n\n\n-- Maid-Chan"
    await gh.post(url, data={"body": message})

    await rate_limit_comment(event, gh)


@routes.post("/")
async def main(request):
    body = await request.read()

    secret = os.environ.get("GH_SECRET")
    oauth_token = os.environ.get("GH_AUTH")

    event = sansio.Event.from_http(request.headers, body, secret=secret)
    async with aiohttp.ClientSession() as session:
        gh = gh_aiohttp.GitHubAPI(session, "k5924",
                                  oauth_token=oauth_token)
        await router.dispatch(event, gh)
    return web.Response(status=200)


if __name__ == "__main__":
    app = web.Application()
    app.add_routes(routes)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)

    web.run_app(app, port=port)
