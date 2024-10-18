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
    'M1.1 Basic SQL': 'M11',
    'M1.2 Advanced SQL': 'M12',
    'M2.1 Python 101': 'M21',
    'M3.1 Pandas 101': 'M31'
}


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only, is_TA)
@lightbulb.option('email', 'Learner email', required=True)
@lightbulb.option('exam', 'Module number', choices=['M1.1 Basic SQL',
                                                    'M1.2 Advanced SQL',
                                                    'M2.1 Python 101',
                                                    'M3.1 Pandas 101'], required=True)
@lightbulb.command('submission', 'Get learner submission', auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def resource(ctx: lightbulb.Context):
    email = ctx.options['email']
    exam = ctx.options['exam']
    url = f"https://cspyexamclient.up.railway.app/submissions/{exams[exam]}/{email}"
    response = requests.get(url)

    if response.status_code != 200:
        await ctx.respond(response.json()['detail'])

    else:
        response = response.json()
        await ctx.respond("Created thread!", flags=hikari.MessageFlag.EPHEMERAL)
        submission_response = (
            f"LEARNER SUBMISSION - {email}\n" +
            '\n'.join(f"{i+1}: {ans}" for i,
                      ans in enumerate([question['answer'] for question in response['answers']]))
        )

        thread = await ctx.app.rest.create_thread(
            ctx.get_channel(),
            hikari.ChannelType.GUILD_PUBLIC_THREAD,
            f"{email} - {exam}"
        )

        exam_type = 'sql' if exam.startswith('M1') else 'python'

        # Handle excessive submission
        await thread.send(f"```{exam_type}\n{submission_response[:submission_response.find('13:')]}\n```")
        await thread.send(f"```{exam_type}\n{submission_response[submission_response.find('13:'):]}\n```")
        await thread.send(f"```{response['summary']}```")

        with open(f'assets/solutions/{exam}.pdf', 'rb') as f:
            await thread.send(hikari.Bytes(f, 'solutions.pdf'))


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only, is_TA)
@lightbulb.option('score', 'New score', required=True)
@lightbulb.option('email', 'Learner email', required=True)
@lightbulb.option('exam', 'Module number', choices=['M1.1 Basic SQL',
                                                    'M1.2 Advanced SQL',
                                                    'M2.1 Python 101',
                                                    'M3.1 Pandas 101'], required=True)
@lightbulb.command('update', 'Update exam score', auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def resource(ctx: lightbulb.Context):
    email = ctx.options['email']
    exam = ctx.options['exam']
    score = ctx.options['score']
    url = f"https://cspyexamclient.up.railway.app/submissions/{exams[exam]}/{email}?new_score={score}"
    response = requests.put(url)

    if response.status_code != 200:
        await ctx.respond(response.json()['detail'])
    else:
        await ctx.respond(f"Updated score for learner {email}. New score is {score}.")
