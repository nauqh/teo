import lightbulb
import hikari
from hikari import Embed
from bot.utils.checks import valid_learner
from datetime import datetime, timezone


plugin = lightbulb.Plugin("Info", "📝 Course info")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


info = {
    "1: Python 101": {
        "url": "https://learn.coderschool.vn/course/dv-m11-basic-python",
        "logo": "https://cdn3.iconfinder.com/data/icons/logos-and-brands-adobe/512/267_Python-512.png"
    },
    "2: SQL Basics & Advanced": {
        "url": "https://learn.coderschool.vn/course/dv-m21-db-sql-intro",
        "logo": "https://symbols.getvecta.com/stencil_28/61_sql-database-generic.90b41636a8.png"
    },
    "3: Cleaning Data w/ Pandas": {
        "url": "https://learn.coderschool.vn/course/dv-m31-pandas-101",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Pandas_mark.svg/1200px-Pandas_mark.svg.png"
    },
    "4: Data Visualization": {
        "url": "https://learn.coderschool.vn/course/dv-m41-analysis-and-visualization",
        "logo": "https://www.lundatech.com/hubfs/tableau-logo.png"
    }
}


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only, valid_learner)
@lightbulb.option('module', 'Module number', choices=['1: Python 101',
                                                      '2: SQL Basics & Advanced',
                                                      '3: Cleaning Data w/ Pandas',
                                                      '4: Data Visualization'])
@lightbulb.command('resource', 'Module resources', auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def resource(ctx: lightbulb.Context):
    embed = (
        Embed(
            title=f"✨ Module {ctx.options['module']}",
            colour="#77ACBF",
            url=info[ctx.options['module']]['url'],
            timestamp=datetime.now(tz=timezone.utc)
        )
        .set_thumbnail(info[ctx.options['module']]['logo'])
        .add_field(
            "**Python cheatsheet**",
            "https://www.pythoncheatsheet.org/"
        )
        .add_field(
            "**Regex**",
            "https://regexr.com/"
        )
        .add_field(
            "**Plotly tutorial**",
            "https://youtu.be/GGL6U0k8WYA?si=U_YTPyxLKaPTg4dn"
        )
        .set_footer(
            text=f"Requested by {ctx.author.username}",
            icon=ctx.author.avatar_url
        )
    )
    await ctx.respond(embed)


@plugin.command()
@lightbulb.command('info', 'Bot information', auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def get_info(ctx: lightbulb.Context):
    bot: hikari.Member = ctx.app.rest.fetch_member(
        ctx.guild_id, 1225375931300970556)
    embed = (
        Embed(
            title=f"✨ User Info",
            colour="#06d6a0",
            url="https://teodocs.vercel.app/",
            timestamp=datetime.now()
        )
        .set_thumbnail(bot.avatar_url)
        .add_field(
            "**Basic**",
            f"Username: {bot.display_name}\n"
            f"User ID: {bot.id}\n"
        )
        .add_field(
            "**Regex**",
            f"Register date: {bot.created_at.date()}"
        )
        .set_footer(
            text=f"Requested by {ctx.author.username}",
            icon=ctx.author.avatar_url
        )
    )
    await ctx.respond(embed)
