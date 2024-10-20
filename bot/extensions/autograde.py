import lightbulb
import hikari
from bot.utils.checks import is_TA

from hikari import Embed
from datetime import datetime
import requests
import pytz


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
async def view_submission(ctx: lightbulb.Context):
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

        # Add this communication to database
        if not response['channel']:
            channel = f"https://discord.com/channels/{thread.guild_id}/{thread.id}"
            url = f"https://cspyexamclient.up.railway.app/channels/{exams[exam]}/{email}?channel={channel}"
            response = requests.put(url)

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
@lightbulb.command('update', 'Update exam score', auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def update_score(ctx: lightbulb.Context):
    email = ctx.options['email']
    exam = ctx.options['exam']
    score = ctx.options['score']
    url = f"https://cspyexamclient.up.railway.app/submissions/{exams[exam]}/{email}?new_score={score}"
    response = requests.put(url)

    if response.status_code != 200:
        await ctx.respond(response.json()['detail'])
    else:
        await ctx.respond(f"Updated score for learner {email}. New score is {score}.")


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only, is_TA)
@lightbulb.option('email', 'Learner email', required=True)
@lightbulb.command('history', 'View submission history of a learner', auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def view_history(ctx: lightbulb.Context):
    email = ctx.options['email']
    author = ctx.author

    url = f"https://cspyexamclient.up.railway.app/history/{email}"
    response = requests.get(url)

    if response.status_code != 200:
        await ctx.respond(response.json()['detail'])
    else:
        response = response.json()
        embed = hikari.Embed(
            title=f"📑 Submission History",
            description=f"**Learner email**: {email}",
            color="#118ab2"
        ).set_thumbnail(
            "https://i.imgur.com/4Qf2VHJ.png"
        ).set_footer(
            text=f"Requested by {author.global_name}",
            icon=author.avatar_url
        )
        for submission in response:
            embed.add_field(
                name=f"**Exam**: {submission['exam']}",
                value=f"**Score**: {submission['score']}\n **Submitted at**: {submission['submitted_at'].replace('T', ' ')}\n **Channel**: {submission['channel']}",
            )
        await ctx.respond(embed=embed)
