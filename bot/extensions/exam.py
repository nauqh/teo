import hikari
import lightbulb
from ..utils.embed import make_embed
from ..utils.config import settings

EXAM_CHANNEL = settings['EXAM_CHANNEL']


plugin = lightbulb.Plugin("Exam", "Exam request")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


@plugin.listener(hikari.GuildMessageCreateEvent)
async def onMessage(event: hikari.GuildMessageCreateEvent) -> None:
    if event.author.is_bot or not event.channel_id == EXAM_CHANNEL:
        return

    channel = await event.message.fetch_channel()

    admin = plugin.bot.cache.get_user(plugin.bot.d.admin)
    embed = make_embed(channel, event.message, channel.name, "Exam")

    await admin.send(embed=embed)
