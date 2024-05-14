import bot
import hikari
import lightbulb

from bot.config import Config
from bot.utils.embed import noti_embed
from bot.utils.helpers import today, yesterday

import asyncio

cf = Config('prod')

app = lightbulb.BotApp(
    cf.TOKEN,
    intents=hikari.Intents.ALL,
    default_enabled_guilds=[cf.DATA.GUILD, cf.FSW.GUILD],
    help_slash_command=True,
    banner=None
)

app.load_extensions_from("./bot/extensions", must_exist=True)


@app.listen(hikari.StartingEvent)
async def on_starting(event: hikari.StartingEvent) -> None:
    app.d.admin = await app.rest.fetch_user(cf.ADMIN)


async def check_threads(
    guild: int,
    forum_channel: int,
    staff_channel: int
):
    CHECK_INTERVAL = 1500
    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        threads = [
            thread for thread in await app.rest.fetch_active_threads(guild)
            if isinstance(thread, hikari.GuildThreadChannel) and
            thread.parent_id == forum_channel and
            thread.created_at.date() in [today(), yesterday()]
        ]
        for thread in threads:
            messages: list[hikari.Message] = await thread.fetch_history()
            members = {message.author.id for message in messages}
            if len(members) <= 1:
                author = await app.rest.fetch_member(guild, thread.owner_id)
                attachments = [att.url for att in messages[0].attachments]

                embed = noti_embed(thread.name, messages[0].content,
                                   f"https://discord.com/channels/{thread.guild_id}/{thread.id}", author)

                if attachments:
                    embed.set_image(attachments[0])

                if guild == 957854915194126336:
                    ta_role = 1194665960376901773
                else:
                    ta_role = 912553106124972083

                await app.rest.create_message(
                    staff_channel,
                    content=(
                        f"<@&{ta_role}> "
                        f"<@{cf.ADMIN}> "
                        "this thread remains unresolved for more than 15min"),
                    embed=embed
                )


async def check_exam_requests(guild, exam_channel, staff_channel):
    channel = await app.rest.fetch_channel(exam_channel)
    CHECK_INTERVAL = 1200
    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        messages = await app.rest.fetch_messages(exam_channel).take_while(
            lambda message: message.created_at.date() == today()
        )

        for message in messages:
            author = await app.rest.fetch_member(guild, message.author.id)

            if guild == 957854915194126336:
                ta_role = 1194665960376901773
            else:
                ta_role = 912553106124972083
            # Filter messages from learner (not have TA role) and has no reactions
            if ta_role not in [role.id for role in author.get_roles()] and not message.reactions:
                embed = noti_embed(
                    channel.name, message.content,
                    f"https://discord.com/channels/{channel.guild_id}/{channel.id}", author)

                await app.rest.create_message(
                    staff_channel,
                    content=(
                        f"<@&{ta_role}> "
                        f"<@{cf.ADMIN}> "
                        "this exam request remains unresolved for more than 15min"),
                    embed=embed
                )


@app.listen(hikari.StartedEvent)
async def on_started(event: hikari.StartedEvent) -> None:
    # Check question center
    asyncio.create_task(check_threads(
        cf.DATA.GUILD, cf.DATA.FORUM_CHANNEL, cf.DATA.STAFF_CHANNEL))
    asyncio.create_task(check_threads(
        cf.FSW.GUILD, cf.FSW.FORUM_CHANNEL, cf.FSW.STAFF_CHANNEL))

    # Check exam request
    asyncio.create_task(check_exam_requests(
        cf.DATA.GUILD, cf.DATA.EXAM_CHANNEL, cf.DATA.STAFF_CHANNEL))
    asyncio.create_task(check_exam_requests(
        cf.FSW.GUILD, cf.FSW.EXAM_CHANNEL, cf.FSW.STAFF_CHANNEL))


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
            state="💡teodocs | /help"
        )
    )
