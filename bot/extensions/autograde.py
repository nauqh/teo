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
@lightbulb.option('view_submission', 'View learner submission', choices=['True', 'False'], default=False)
@lightbulb.command('autograde', 'Autograde module', auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def resource(ctx: lightbulb.Context):
    email = ctx.options['email']
    exam = ctx.options['exam']
    view_submission = ctx.options['view_submission']
    url = f"https://cspyexamclient.up.railway.app/autograde?email={email}&exam={exams[exam]}"
    response = requests.get(url)

    if response.status_code != 200:
        await ctx.respond(response.json()['detail'])

    else:
        response = response.json()
        if view_submission:
            await ctx.respond("Created thread!")
            submission_response = (
                f"LEARNER SUBMISSION - {email}\n" +
                '\n'.join(f"{i+1}: {ans}" for i,
                          ans in enumerate(response['submission']))
            )

            thread = await ctx.app.rest.create_thread(
                ctx.get_channel(),
                hikari.ChannelType.GUILD_PUBLIC_THREAD,
                exam
            )

            exam_type = 'sql' if exam.startswith('M1') else 'python'

            await thread.send(f"```{exam_type}\n{submission_response}\n```")
            await thread.send(f"```{response['summary']}```")
        else:
            await ctx.respond(f"```{response['summary']}```")
