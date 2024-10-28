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
            requests.put(url)

        exam_type = 'sql' if exam.startswith('M1') else 'python'

        # Handle excessive submission
        await thread.send(f"```{exam_type}\n{submission_response[:submission_response.find('13:')]}\n```")
        await thread.send(f"```{exam_type}\n{submission_response[submission_response.find('13:'):]}\n```")

        # if exam == 'M1.1 Basic SQL':
        #     issue = response['summary'][response['summary'].find('Issue'):]
        #     await thread.send(f"```{response['summary'][:response['summary'].find('Issue')]}```")
        #     await thread.send(f"```{issue[:len(issue)//2]}```")
        #     await thread.send(f"```{issue[len(issue)//2:]}```")
        # else:
        await thread.send(f"```{response['summary']}```")
        # with open(f'assets/solutions/{exam}.pdf', 'rb') as f:
        #     await thread.send(hikari.Bytes(f, 'solutions.pdf'))
        solutions = {
            "M11": "https://drive.google.com/file/d/1tvZyXZX2ttlD8S7RJl6RJHtKtYxS5j6s/view?usp=drive_link",
            "M12": "https://drive.google.com/file/d/1-0767BUsbseekFHzufuhDKEG253vclsg/view?usp=drive_link",
            "M21": "https://drive.google.com/file/d/1aUYMDcDpnk0YymyHiSyzxULnPjvpLzOE/view?usp=drive_link",
            "M31": "https://drive.google.com/file/d/17fS11_ClRjgGvL7x6MnP3019CkO8AFe6/view?usp=drive_link"
        }
        await thread.send(solutions[exams[exam]])


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
        await ctx.respond(f"{ctx.author.mention} updated score for learner {email}.\nNew score is `{score}`.")


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only, is_TA)
@lightbulb.option('email', 'Learner email', required=True)
@lightbulb.command('history', 'View learner submission history', auto_defer=True)
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
            exam = submission['exam']
            score = submission['score']
            submitted_at = submission['submitted_at'].replace('T', ' ')
            channel = "Use `/submission` to update channel link" if not submission[
                'channel'] else submission['channel']
            embed.add_field(
                name=exam,
                value=f"**Score**: {score}\n **Submitted at**: {submitted_at}\n **Channel**: {channel}",
            )
        await ctx.respond(embed=embed)
