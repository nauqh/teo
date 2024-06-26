from hikari import Embed, GuildChannel, Message, GuildThreadChannel
from datetime import datetime
import pytz

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


def job_embed(job, company, logo, url, level, location, tag):
    return (
        Embed(
            title=f"{job.text.strip()}",
            description=f"**Company**: {company}",
            colour="#118ab2",
            url=f"https://topdev.vn{url}",
            timestamp=datetime.now().astimezone(pytz.timezone('Asia/Ho_Chi_Minh'))
        )
        .set_thumbnail(logo)
        .add_field(
            "**Position**",
            f"{level.text.strip()}",
            inline=True
        )
        .add_field(
            "**Location**",
            f"{location.text.strip()}",
            inline=True
        )
        .add_field(
            "**Tags**",
            f"{tag}"
        )
        .set_footer(
            text=f"From TopDev",
            icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQIVD7VoNMi4DusIIN0zdRpTU4yueP5fD2Ysg&s"
        )
    )


def job_embed_itviec(title, company, url, logo, mode, location, tags):
    return (
        Embed(
            title=title,
            description=f"**Company**: {company}",
            colour="#118ab2",
            url=url,
            timestamp=datetime.now().astimezone(pytz.timezone('Asia/Ho_Chi_Minh'))
        )
        .set_thumbnail(logo)
        .add_field(
            "**Work mode**",
            mode,
            inline=True
        )
        .add_field(
            "**Location**",
            location,
            inline=True
        )
        .add_field(
            "**Tags**",
            tags
        )
        .set_footer(
            text=f"From ITviec",
            icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQKk8Nc-lBHyDwEMs0drgzArhbsx4Ihq-_DIA&s"
        )
    )
