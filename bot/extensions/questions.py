import hikari
import lightbulb


plugin = lightbulb.Plugin("Q&A", "🙋‍♂️ Question Center")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


@plugin.listener(hikari.GuildThreadCreateEvent)
async def on_thread_create(event: hikari.GuildThreadCreateEvent) -> None:
    """
    Handles the creation of a new thread in the question center and responds to the first message.
    """
    thread: hikari.GuildThreadChannel = await event.fetch_channel()

    if thread.parent_id == 1081063200377806899:
        messages = await thread.fetch_history()
        if messages:
            message: hikari.Message = messages[0]
        await plugin.app.rest.create_forum_post(
            1317000937700593664,
            thread.name,
            message.content,
            attachments=message.attachments
        )
