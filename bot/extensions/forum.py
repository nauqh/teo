import hikari
import lightbulb
import pandas as pd

from ..utils.embed import make_embed
from ..utils.config import settings
from ..db.models import Thread, User
from ..utils.log import get_logger
from ..utils.utils import progress_bar
from datetime import datetime

log = get_logger(__name__)

FORUM_CHANNEL = settings['FORUM_CHANNEL']
GUILD = settings['GUILD']

plugin = lightbulb.Plugin("Forum", "Question center")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


async def get_tag(channel: hikari.GuildThreadChannel) -> str:
    forum = await plugin.app.rest.fetch_channel(FORUM_CHANNEL)
    tag_id = channel.applied_tag_ids[0]
    return next((tag.name for tag in forum.available_tags if tag.id == tag_id), None)


async def is_valid_thread(event: hikari.GuildMessageCreateEvent) -> bool:
    return not event.author.is_bot and isinstance(
        await event.message.fetch_channel(),
        hikari.GuildThreadChannel)


def create_embed(thread: hikari.GuildThreadChannel,
                 message: hikari.Message,
                 tag: str,
                 is_question: bool = True) -> hikari.Embed:
    title = f"{thread.name} (cont)" if not is_question else thread.name
    embed_type = "Question" if is_question else "Message"
    return make_embed(thread, message, title, embed_type, tag=tag)


async def send_embed_with_attachments(admin: hikari.User,
                                      embed: hikari.Embed,
                                      attachments: list[str]) -> None:
    if len(attachments) == 1:
        embed.set_image(attachments[0])
        await admin.send(embed=embed)
    else:
        await admin.send(embed=embed)
        if attachments:
            await admin.send(attachments=attachments)


@plugin.listener(hikari.GuildMessageCreateEvent)
async def on_new_thread(event: hikari.GuildMessageCreateEvent) -> None:
    """Listens for new posts in guild channels and processes them accordingly."""
    if not await is_valid_thread(event):
        return

    thread = await event.message.fetch_channel()
    messages = await plugin.bot.rest.fetch_messages(thread)
    tag = await get_tag(thread)

    is_question = len(messages) == 1
    embed = create_embed(thread, event.message, tag, is_question)

    admin = plugin.bot.d.admin
    attachments = [att.url for att in event.message.attachments]
    await send_embed_with_attachments(admin, embed, attachments)

    # Add to database
    with plugin.app.d.Session() as session:
        thread = Thread(id=thread.id,
                        name=thread.name,
                        created_at=thread.created_at.strftime(
                            "%Y-%m-%d %H:%M:%S"),
                        tags=thread.applied_tag_ids,
                        messages=[message.id for message in messages],
                        author_id=thread.owner_id)
        session.add(thread)
        session.commit()
        log.info(f"Added one thread: {thread.name}")


@plugin.command()
@lightbulb.command('thread', 'Module resources', auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def get_threads(ctx: lightbulb.Context):
    data: list[hikari.GuildThreadChannel] = []
    threads = [thread
               for thread in await ctx.bot.rest.fetch_active_threads(GUILD)
               if isinstance(thread, hikari.GuildThreadChannel)
               and thread.parent_id == FORUM_CHANNEL
               and thread.created_at.strftime("%Y-%m-%d") >= str(datetime.now().replace(day=1).date())]
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

    # await ctx.author.send(attachment="threads_draft.csv")
