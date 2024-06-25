import lightbulb
from hikari import Embed
from datetime import datetime
import pytz
import hikari
import requests
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.utils.embed import job_embed

plugin = lightbulb.Plugin("Jobs", "📝 Job postings")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


async def job_post(url, channel) -> None:
    """
    Scrape job postings from topdev.vn and post them to the job channel

    Job board components:
    - Job title
    - Company name
    - Job level
    - Job location
    - Job tags
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    section = soup.find('section', id='tab-job')

    descriptions = section.find_all('div', class_='flex-1')
    logos = [logo.find('img')['src']
             for logo in soup.find_all('a', class_='block h-[7.5rem] w-[10rem]')]
    tags = [' '.join(f'`{span.text}`' for span in desc.find_all('span'))
            for desc in descriptions]
    jobs = section.find_all('h3', class_='line-clamp-1')
    companies = [company.find('a').text.strip()
                 for company in section.find_all('div', class_='mt-1 line-clamp-1')]
    for i in range(len(jobs[:5])):
        job_link = jobs[i].find('a')['href']
        level = descriptions[i].find_all('p')[0]
        location = descriptions[i].find_all('p')[1]
        embed = job_embed(jobs[i], companies[i], logos[i],
                          job_link, level, location, tags[i])

        await plugin.app.rest.create_message(channel, embed=embed)


async def job_post_itviec(url, channel):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    page = urlopen(Request(url, headers=headers))
    soup = BeautifulSoup(page, "html.parser")

    jobs = soup.find_all('div', class_='ipy-2')

    for job in jobs[:5]:
        job_url = "https://itviec.com/" + job.find('a')['href']
        title = job.find('h3').text.strip()
        company = job.find(
            'div', class_='imy-3 d-flex align-items-center').span.text.strip()
        logo = job.find(
            'div', class_='imy-3 d-flex align-items-center').a.img['data-src']

        mode, location = [div.span.text.strip()
                          for div in job.find_all('div',
                                                  class_='d-flex align-items-center text-dark-grey imt-1')]

        tags = ' '.join([f'`{a.text.strip()}`' for a in job.find(
            'div', class_='imt-3 imb-2').find_all('a')])

        embed = (
            Embed(
                title=title,
                description=f"**Company**: {company}",
                colour="#118ab2",
                url=job_url,
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
                text=f"From TopDev",
                icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQIVD7VoNMi4DusIIN0zdRpTU4yueP5fD2Ysg&s"
            )
        )

        await plugin.app.rest.create_message(channel, embed=embed)


@plugin.listener(hikari.StartingEvent)
async def on_starting(event: hikari.StartingEvent) -> None:
    # Schedule job_post to run every 30 seconds
    plugin.app.d.scheduler = AsyncIOScheduler(timezone='Asia/Ho_Chi_Minh')
    plugin.app.d.scheduler.start()
    plugin.app.d.scheduler.add_job(job_post, 'cron', second=30, args=[
                                   "https://topdev.vn/viec-lam-it/data-analytics-intern-fresher-junior-kt202", 1255062099118395454])
    plugin.app.d.scheduler.add_job(job_post, 'cron', second=30, args=[
                                   "https://topdev.vn/viec-lam-it/react-javascript-kt7367,22", 1255068486573625394])
    plugin.app.d.scheduler.add_job(job_post_itviec, 'cron', second=30, args=[
                                   "https://itviec.com/it-jobs/data-analyst", 1255062099118395454])
    plugin.app.d.scheduler.add_job(job_post_itviec, 'cron', second=30, args=[
        "https://itviec.com/it-jobs/reactjs-javascript", 1255068486573625394])
