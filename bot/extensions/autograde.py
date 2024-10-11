import lightbulb
import hikari
from bot.utils.checks import is_TA

from hikari import Embed
from datetime import datetime
import requests


plugin = lightbulb.Plugin("Autograde", "📝 Autograde exam submissions")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


exams = {
    'M1.1: Basic SQL': 'M11',
    'M1.2: Advanced SQL': 'M12',
    'M2.1: Python 101': 'M21',
    'M3.1: Pandas 101': 'M31'
}


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only, is_TA)
@lightbulb.option('email', 'Learner email', required=True)
@lightbulb.option('exam', 'Module number', choices=['M1.1: Basic SQL',
                                                    'M1.2: Advanced SQL',
                                                    'M2.1: Python 101',
                                                    'M3.1: Pandas 101'], required=True)
@lightbulb.command('autograde', 'Autograde module', auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def resource(ctx: lightbulb.Context):
    email = ctx.options['email']
    exam = ctx.options['exam']
    url = f"https://cspyexamclient.up.railway.app/autograde?email={email}&exam={exams[exam]}"
    response = requests.get(url).json()

    submission_response = (
        "LEARNER SUBMISSION\n" +
        '\n'.join(f"{i+1}: {ans}" for i,
                  ans in enumerate(response['submission']))
    )

    await ctx.respond(f"```\n{submission_response}\n```")
    await ctx.respond(f"```{response['summary']}```")
