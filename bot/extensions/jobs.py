import subprocess
import os
import lightbulb
import hikari
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from hikari import Embed
from datetime import datetime
import pytz
import requests


plugin = lightbulb.Plugin("Jobs crawl", "📝 Job postings")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


# NOTE: CWD is /scripts


def run_script():
    try:
        os.chdir('scripts')
        subprocess.run(['sh', 'script.sh'],
                       check=True)
        print("Script completed successfully.")
    except subprocess.CalledProcessError as e:
        print("Script failed with error:", e)


def get_subfolder_names(path=None):
    if path is None:
        path = os.getcwd()

    return os.listdir(path)


async def post_jobs():
    response = requests.get(
        "https://jobboard.up.railway.app/jobs?filtered=True")

    jobs = response.json()

    for job in jobs:
        if 'itviec' in job['url']:
            icon_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQKk8Nc-lBHyDwEMs0drgzArhbsx4Ihq-_DIA&s"
            icon_title = "ITviec"
        elif 'linkedin' in job['url']:
            icon_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/LinkedIn_logo_initials.png/600px-LinkedIn_logo_initials.png"
            icon_title = "LinkedIn"
        else:
            icon_url = "https://play-lh.googleusercontent.com/SsaNLtRaJR44BSM1tX1jOax7rvfG4UgxqonLxui7nXQBh1Osa4EsZMUHZVXKZINo4A"
            icon_title = "TopCV"

        channel = 1255062099118395454 if job['tag'] == 'data' else 1255068486573625394

        embed = (
            Embed(
                title=job['title'],
                description=f"**Company**: {job['company']}",
                colour="#118ab2",
                url=job['url'],
                timestamp=datetime.now().astimezone(pytz.timezone('Asia/Ho_Chi_Minh'))
            )
            .set_thumbnail(job['logo'])
            .add_field(
                "**Location**",
                job['location'],
                inline=True
            )
            .set_footer(
                text=f"From {icon_title}",
                icon=icon_url
            )
        )
        await plugin.app.rest.create_message(channel, embed=embed)


@plugin.listener(hikari.StartingEvent)
async def on_starting(event: hikari.StartingEvent) -> None:
    plugin.app.d.scheduler = AsyncIOScheduler(timezone='Asia/Ho_Chi_Minh')
    plugin.app.d.scheduler.start()

    plugin.app.d.scheduler.add_job(
        run_script, 'cron', day_of_week='mon', hour=8)
    plugin.app.d.scheduler.add_job(
        post_jobs, 'cron', day_of_week='mon', hour=9)
