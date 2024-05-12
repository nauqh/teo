import bot
import hikari
import lightbulb
from datetime import datetime
from utils.embed import noti_embed
from config import Config as cf

import asyncio


app = lightbulb.BotApp(
    cf.TOKEN,
    intents=hikari.Intents.ALL,
    default_enabled_guilds=cf.GUILD,
    help_slash_command=True,
    banner=None
)


@app.listen(hikari.StartingEvent)
async def on_starting(event: hikari.StartingEvent) -> None:
    app.d.admin = await app.rest.fetch_user(cf.ADMIN)


def is_today(dt: datetime) -> bool:
    return dt.date() == datetime.now().date()


async def check_threads():
    CHECK_INTERVAL = 1000  # 15min
    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        threads = [
            thread for thread in await app.rest.fetch_active_threads(cf.GUILD)
            if isinstance(thread, hikari.GuildThreadChannel) and
            thread.parent_id == cf.FORUM_CHANNEL and
            is_today(thread.created_at)
        ]
        for thread in threads:
            messages: list[hikari.Message] = await thread.fetch_history()
            members = {message.author.id for message in messages}
            if len(members) <= 1:
                author = await app.rest.fetch_member(cf.GUILD, thread.owner_id)
                attachments = [att.url for att in messages[0].attachments]

                embed = noti_embed(thread.name, messages[0].content,
                                   f"https://discord.com/channels/{thread.guild_id}/{thread.id}", author)

                if attachments:
                    embed.set_image(attachments[0])

                await app.rest.create_message(
                    1237424754739253279,
                    content=(
                        "<@&1194665960376901773> "
                        "<@1214095592372969505> "
                        "this thread remains unresolved for more than 15min"),
                    embed=embed
                )


async def check_exam_requests():
    CHECK_INTERVAL = 1000
    channel = await app.rest.fetch_messages(cf.EXAM_CHANNEL)
    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        messages = await app.rest.fetch_messages(cf.EXAM_CHANNEL).take_while(
            lambda message: message.created_at.date() == datetime.now().date()
        )

        for message in messages:
            author = await app.rest.fetch_member(cf.GUILD, message.author.id)
            # Filter messages from learner (not have TA role) and has no reactions
            if 1194665960376901773 not in [role.id for role in author.get_roles()] and not message.reactions:

                embed = noti_embed(
                    message.name, message.content,
                    f"https://discord.com/channels/{channel.guild_id}/{channel.id}", author)

                await app.rest.create_message(
                    1237424754739253279,
                    content=(
                        "<@&1194665960376901773> "
                        "<@1214095592372969505> "
                        "this exam request remains unresolved for more than 15min"),
                    embed=embed
                )


@app.listen(hikari.StartedEvent)
async def on_started(event: hikari.StartedEvent) -> None:
    asyncio.create_task(check_threads())
    asyncio.create_task(check_exam_requests())


@app.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    exception = event.exception
    if isinstance(exception, lightbulb.CheckFailure):
        causes = exception.causes or [exception]
        error_msg = causes[0]
    else:
        raise exception
    await event.context.respond(error_msg, flags=hikari.MessageFlag.EPHEMERAL)


def run() -> None:
    app.run(
        activity=hikari.Activity(
            name=f"v{bot.__version__}",
            type=hikari.ActivityType.LISTENING,
            state="💡teodocs | /help")
    )
