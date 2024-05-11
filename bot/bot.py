import bot
import hikari
import lightbulb
from datetime import datetime, timedelta
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD = int(os.getenv("GUILD"))
ADMIN = int(os.getenv("ADMIN"))
FORUM_CHANNEL = int(os.getenv("FORUM_CHANNEL"))
EXAM_CHANNEL = int(os.getenv("EXAM_CHANNEL"))
STAFF_CHANNEL = int(os.getenv("STAFF_CHANNEL"))

app = lightbulb.BotApp(
    TOKEN,
    intents=hikari.Intents.ALL,
    default_enabled_guilds=GUILD,
    help_slash_command=True,
    banner=None
)


@app.listen(hikari.StartingEvent)
async def on_starting(event: hikari.StartingEvent) -> None:
    app.d.admin = await app.rest.fetch_user(ADMIN)


def is_today(dt: datetime) -> bool:
    return dt.date() == datetime.now().date()


async def check_threads():
    CHECK_INTERVAL = 900  # 15min
    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        threads = [
            thread for thread in await app.rest.fetch_active_threads(GUILD)
            if isinstance(thread, hikari.GuildThreadChannel) and
            thread.parent_id == FORUM_CHANNEL and
            is_today(thread.created_at)
        ]
        for thread in threads:
            messages: list[hikari.Message] = await thread.fetch_history()
            members = {message.author.id for message in messages}
            if len(members) <= 1:
                author = await app.rest.fetch_member(GUILD, thread.owner_id)
                attachments = [att.url for att in messages[0].attachments]

                embed = hikari.Embed(
                    title=thread.name,
                    description=messages[0].content,
                    color="#118ab2",
                    url=f"https://discord.com/channels/{thread.guild_id}/{thread.id}"
                ).set_footer(text=f"Posted by {author.global_name}",
                             icon=author.avatar_url)

                if attachments:
                    embed.set_image(attachments[0])

                await app.rest.create_message(
                    1237424754739253279,
                    content=(
                        "<@&1194665960376901773> "
                        "<@1214095592372969505> "
                        "this thread remains unresolved for more than 15min"),
                    embed=embed)


async def check_exam_requests():
    CHECK_INTERVAL = 900
    channel = await app.rest.fetch_messages(EXAM_CHANNEL)
    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        messages = channel.take_while(
            lambda message: is_today(message.created_at)
        )

        for message in messages:
            author = await app.rest.fetch_member(GUILD, message.author.id)
            # Filter messages from learner (not have TA role) and has no reactions
            if 1194665960376901773 not in [role.id for role in author.get_roles()] and not message.reactions:
                embed = hikari.Embed(
                    title=message.name,
                    description=message.content,
                    color="#118ab2",
                    url=f"https://discord.com/channels/{channel.guild_id}/{channel.id}"
                ).set_footer(text=f"Posted by {author.global_name}",
                             icon=author.avatar_url)
                await app.rest.create_message(
                    1237424754739253279,
                    content=(
                        "<@&1194665960376901773> "
                        "<@1214095592372969505> "
                        "this exam request remains unresolved for more than 15min"),
                    embed=embed)


@app.listen(hikari.StartedEvent)
async def on_started(event: hikari.StartedEvent) -> None:
    # asyncio.create_task(check_threads())
    # asyncio.create_task(check_exam_requests())
    ...


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
