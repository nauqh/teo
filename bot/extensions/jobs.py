import lightbulb
import hikari
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.utils.embed import job_embed

plugin = lightbulb.Plugin("Jobs", "📝 Job postings")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


async def job_post() -> None:
    """
    Scrape job postings from topdev.vn and post them to the job channel

    Job board components:
    - Job title
    - Company name
    - Job level
    - Job location
    - Job tags
    """
    # response = requests.get(
    #     "https://topdev.vn/viec-lam-it/react-javascript-ho-chi-minh-intern-fresher-junior-kt7367,22l79")
    response = requests.get(
        "https://topdev.vn/viec-lam-it/data-analytics-kt202")
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
    for i in range(len(jobs)):
        job_link = jobs[i].find('a')['href']
        level = descriptions[i].find_all('p')[0]
        location = descriptions[i].find_all('p')[1]
        embed = job_embed(jobs[i], companies[i], logos[i],
                          job_link, level, location, tags[i])

        await plugin.app.rest.create_message(1255062099118395454, embed=embed)


@plugin.listener(hikari.StartingEvent)
async def on_starting(event: hikari.StartingEvent) -> None:
    plugin.app.d.scheduler = AsyncIOScheduler()
    # plugin.app.d.scheduler.add_job(job_post, 'interval', seconds=20)
    # plugin.app.d.scheduler.add_job(job_post, 'cron', day_of_week='mon')
    plugin.app.d.scheduler.add_job(job_post, 'cron', hour=9, minute=0)


@plugin.listener(hikari.StartedEvent)
async def on_started(event: hikari.StartedEvent) -> None:
    plugin.app.d.scheduler.start()
