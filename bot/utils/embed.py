from hikari import Embed, GuildChannel, Message, GuildThreadChannel
from datetime import datetime

color = {
    "Question": "#118ab2",
    "Message": "#06d6a0",
    "Exam": "#ef476f"
}


def make_embed(channel: GuildChannel | GuildThreadChannel,
               message: Message,
               title: str,
               action: str,
               tag: str = None) -> Embed:
    title_text = f"{tag} - {title}" if tag else title
    return (
        Embed(
            title=title_text,
            timestamp=datetime.now().astimezone(),
            description=message.content,
            color=color[action],
            url=f"https://discord.com/channels/{channel.guild_id}/{channel.id}"
        )
        .set_footer(
            text=f"Requested by {message.author.username}",
            icon=message.author.avatar_url
        )
    )


def noti_embed(title, description, url, author):
    return Embed(
        title=title,
        description=description,
        color="#118ab2",
        url=url
    ).set_footer(
        text=f"Posted by {author.global_name}",
        icon=author.avatar_url
    )
