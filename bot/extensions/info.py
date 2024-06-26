import lightbulb
import hikari
from hikari import Embed
from bot.utils.checks import valid_learner
from datetime import datetime, timezone
import pytz


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
@lightbulb.command('teo', 'Bot information', auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def get_info(ctx: lightbulb.Context):
    bot: hikari.Member = await ctx.app.rest.fetch_member(
        ctx.guild_id, 1225375931300970556)

    roles = [f"<@&{id}>" for id in bot.role_ids]
    if ctx.guild_id == 957854915194126336:
        ta = 1194665960376901773
        job_board = 1255062099118395454
        questions = 1081063200377806899
    elif ctx.guild_id == 912307061310783538:
        ta = 912553106124972083
        job_board = 1255068486573625394
        questions = 1077118780523679787
    embed = (
        Embed(
            title=f"🧋 A greeting from T.è.o",
            colour="#118ab2",
            url="https://teodocs.vercel.app/",
            description=f"Hello, I'm T.è.o, a virtual assistant for Coderschool TA. I'm here to help you with your learning journey.\n\n Every week on Monday and Thursday, I will send you an update on new job posting for your desired position. You can find it on the <#{job_board}> channel. \n\nIf you have any questions, feel free to ask my fellow <@&{ta}> via <#{questions}>. They will be here to help you.",
            timestamp=datetime.now().astimezone(pytz.timezone('Asia/Ho_Chi_Minh'))
        )
        .set_thumbnail(bot.avatar_url)
        .set_footer(
            text=f"Requested by {ctx.author.username}",
            icon=ctx.author.avatar_url
        )
    )
    await ctx.respond(embed)
