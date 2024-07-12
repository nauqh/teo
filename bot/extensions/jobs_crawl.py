import subprocess
import json
import os
import lightbulb
import hikari
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from hikari import Embed
from datetime import datetime
import pytz


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
    for path in get_subfolder_names('scripts/data/filter/'):
        channel = 1255062099118395454 if 'data' in path else 1255068486573625394
        with open(os.path.join('scripts/data/filter/', path), 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                embed = (
                    Embed(
                        title=item['title'],
                        description=f"**Company**: {item['company']}",
                        colour="#118ab2",
                        url=item['url'],
                        timestamp=datetime.now().astimezone(pytz.timezone('Asia/Ho_Chi_Minh'))
                    )
                    .set_thumbnail(item['logo'])

                    .add_field(
                        "**Location**",
                        item['location'],
                        inline=True
                    )
                )
                await plugin.app.rest.create_message(channel, embed=embed)


@ plugin.listener(hikari.StartingEvent)
async def on_starting(event: hikari.StartingEvent) -> None:
    plugin.app.d.scheduler = AsyncIOScheduler(timezone='Asia/Ho_Chi_Minh')
    plugin.app.d.scheduler.start()

    plugin.app.d.scheduler.add_job(
        run_script, 'cron', day_of_week='fri', hour=15, minute=0)
    plugin.app.d.scheduler.add_job(
        post_jobs, 'cron', day_of_week='fri', hour=15, minute=5)
