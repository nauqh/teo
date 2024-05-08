import hikari
import lightbulb
import pandas as pd
import os
import requests
from .config import settings

FORUM_CHANNEL = settings['FORUM_CHANNEL']
GUILD = settings['GUILD']


async def get_tags(app: lightbulb.BotApp):
    forum: hikari.GuildForumChannel = await app.rest.fetch_channel(FORUM_CHANNEL)
    return forum.available_tags


async def get_roles(app: lightbulb.BotApp):
    guild: hikari.Guild = await app.rest.fetch_guild(GUILD)
    return guild.roles


def progress_bar(percent: float) -> str:
    progress = ''
    for i in range(20):
        if i == (int)(percent*20):
            progress += '🔘'
        else:
            progress += '▬'
    return progress

# NOTE: lightbulb commands


def get_google_sheet(url: str, out_dir='data', out_file='output.csv') -> None:
    url = url.replace("edit?usp=sharing", "export?format=csv")

    response = requests.get(url)

    if response.status_code == 200:
        os.makedirs(out_dir, exist_ok=True)
        filepath = os.path.join(out_dir, out_file)
        with open(filepath, 'wb') as f:
            f.write(response.content)
            print(f'CSV file saved to: {filepath}')
    else:
        print(f'Error downloading Google Sheet: {response.status_code}')


# get_google_sheet(
#     'https://docs.google.com/spreadsheets/d/1x8zSk-E2J9b32yJZ64z_N75uPnrCwgRLI7ltdCgNdnQ/edit?usp=sharing')


async def get_threads(ctx: lightbulb.Context):
    data: list[hikari.GuildThreadChannel] = []
    threads = [thread
               for thread in await ctx.bot.rest.fetch_active_threads(GUILD)
               if isinstance(thread, hikari.GuildThreadChannel)
               and thread.parent_id == FORUM_CHANNEL
               and thread.created_at.strftime("%Y-%m-%d %H:%M:%S") >= '2024-04-01']  # Only threads in April
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
                "author": message.author
            } for message in messages]
        })
        await msg.edit(progress_bar(count/total))

    await ctx.respond("Extracted")

    df = pd.DataFrame(data)
    df.to_csv("threads_draft.csv", index=False)

    await ctx.author.send(attachment="threads_draft.csv")


async def get_members(ctx: lightbulb.Context):
    data: list[hikari.User] = []
    guild: hikari.Guild = ctx.get_guild()
    for uid in guild.get_members():
        member: hikari.User = guild.get_member(uid)
        data.append({
            "id": uid,
            "name": member.global_name,
            "is_bot": member.is_bot,
            "roles": member.role_ids
        })

    df = pd.DataFrame(data)
    df.to_csv("members.csv", index=False)

    await ctx.respond(attachment="members.csv")
