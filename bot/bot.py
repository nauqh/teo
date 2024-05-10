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

app = lightbulb.BotApp(TOKEN,
                       intents=hikari.Intents.ALL,
                       default_enabled_guilds=GUILD,
                       help_slash_command=True,
                       banner=None)


@app.listen(hikari.StartingEvent)
async def on_starting(event: hikari.StartingEvent) -> None:
    app.d.admin = await app.rest.fetch_user(ADMIN)


async def check_threads():
    CHECK_INTERVAL = 900  # 15min
    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        threads = [
            thread for thread in await app.rest.fetch_active_threads(GUILD)
            if isinstance(thread, hikari.GuildThreadChannel) and
            thread.parent_id == FORUM_CHANNEL and thread.created_at.date() in
            [datetime.now().date(),
             datetime.now().date() - timedelta(days=1)]
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
                        "<@815706256463364116> "
                        "this thread remains unresolved for more than 15min"),
                    embed=embed)


async def check_exam_requests():
    CHECK_INTERVAL = 900
    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        messages = await app.rest.fetch_messages(EXAM_CHANNEL).take_while(
            lambda message: message.created_at.date() == datetime.now().date()
        )

        for message in messages:
            author = await app.rest.fetch_member(GUILD, message.author.id)
            # # Filter messages from learner (not have TA role) and has no reactions
            if 1194665960376901773 not in [role.id for role in author.get_roles()] and not message.reactions:
                print(
                    f"Request exam from {message.author} has not been resolved")


@ app.listen(hikari.StartedEvent)
async def on_started(event: hikari.StartedEvent) -> None:
    asyncio.create_task(check_threads())
    asyncio.create_task(check_exam_requests())


@ app.listen(lightbulb.CommandErrorEvent)
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
