import hikari
import lightbulb
import pandas as pd

from bot.config import Config
from datetime import datetime

cf = Config('prod')
FORUM_CHANNEL = cf.DATA.FORUM_CHANNEL
GUILD = cf.DATA.GUILD

plugin = lightbulb.Plugin("Forum", "Question center")


def progress_bar(percent: float) -> str:
    progress = ''
    for i in range(20):
        if i == (int)(percent*20):
            progress += '🔘'
        else:
            progress += '▬'
    return progress


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


# @plugin.command()
# @lightbulb.command('threads', 'Get all threads', auto_defer=True)
# @lightbulb.implements(lightbulb.SlashCommand)
# async def get_threads(ctx: lightbulb.Context):
#     data: list[hikari.GuildThreadChannel] = []
#     threads = [thread
#                for thread in await ctx.bot.rest.fetch_active_threads(GUILD)
#                if isinstance(thread, hikari.GuildThreadChannel)
#                and thread.parent_id == FORUM_CHANNEL
#                and thread.created_at.strftime("%Y-%m-%d") >= str(datetime.now().replace(day=1, month=5).date())]
#     msg = await ctx.bot.rest.create_message(ctx.channel_id, f"Extracting {len(threads)} threads")

#     total = len(threads)
#     for count, thread in enumerate(threads, start=1):
#         messages: list[hikari.Message] = await thread.fetch_history()
#         data.append({
#             "id": thread.id,
#             "name": thread.name,
#             "created_at": thread.created_at.strftime("%Y-%m-%d %H:%M:%S"),
#             "author_id": thread.owner_id,
#             "tags": thread.applied_tag_ids,
#             "messages": [{
#                 "id": message.id,
#                 "content": message.content,
#                 "created_at": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
#                 "author": message.author.id
#             } for message in messages]
#         })
#         await msg.edit(progress_bar(count/total))

#     await ctx.respond("Extracted")

#     df = pd.DataFrame(data)
#     df.to_csv("threads_draft.csv", index=False)

#     await msg.edit(attachment="threads_draft.csv")


# @plugin.command()
# @lightbulb.command('members', 'Get all members', auto_defer=True)
# @lightbulb.implements(lightbulb.SlashCommand)
# async def get_members(ctx: lightbulb.Context):
#     data: list[hikari.User] = []
#     guild: hikari.Guild = ctx.get_guild()
#     for uid in guild.get_members():
#         member: hikari.User = guild.get_member(uid)
#         data.append({
#             "id": uid,
#             "name": member.global_name,
#             "is_bot": member.is_bot,
#             "roles": member.role_ids
#         })

#     df = pd.DataFrame(data)
#     df.to_csv("members.csv", index=False)

#     await ctx.respond(attachment="members.csv")
