import hikari
import lightbulb
import pandas as pd

from bot.config import Config
from ..utils.utils import progress_bar
from datetime import datetime

cf = Config('prod')
FORUM_CHANNEL = cf.DATA.FORUM_CHANNEL
GUILD = cf.DATA.GUILD

plugin = lightbulb.Plugin("Forum", "Question center")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


@plugin.command()
@lightbulb.command('thread', 'Module resources', auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def get_threads(ctx: lightbulb.Context):
    data: list[hikari.GuildThreadChannel] = []
    threads = [thread
               for thread in await ctx.bot.rest.fetch_active_threads(GUILD)
               if isinstance(thread, hikari.GuildThreadChannel)
               and thread.parent_id == FORUM_CHANNEL
               and thread.created_at.strftime("%Y-%m-%d") >= str(datetime.now().replace(day=1, month=5).date())]
    msg = await ctx.bot.rest.create_message(ctx.channel_id, f"Extracting {len(threads)} threads")

    total = len(threads)
    for count, thread in enumerate(threads, start=1):
        messages: list[hikari.Message] = await thread.fetch_history()
        data.append({
            "id": thread.id,
            "name": thread.name,
            "created_at": thread.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "author_id": thread.owner_id,
            "tags": thread.applied_tag_ids,
            "messages": [{
                "id": message.id,
                "content": message.content,
                "created_at": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "author": message.author.id
            } for message in messages]
        })
        await msg.edit(progress_bar(count/total))

    await ctx.respond("Extracted")

    df = pd.DataFrame(data)
    df.to_csv("threads_draft.csv", index=False)
