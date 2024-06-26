import lightbulb
import hikari
import requests
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.utils.embed import job_embed, job_embed_itviec

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
    for i in range(len(jobs)):
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

    for job in jobs:
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

        embed = job_embed_itviec(
            title, company, job_url, logo, mode, location, tags)

        await plugin.app.rest.create_message(channel, embed=embed)


@plugin.listener(hikari.StartingEvent)
async def on_starting(event: hikari.StartingEvent) -> None:
    plugin.app.d.scheduler = AsyncIOScheduler(timezone='Asia/Ho_Chi_Minh')
    plugin.app.d.scheduler.start()

    # Post jobs on Data server
    plugin.app.d.scheduler.add_job(job_post, 'cron', hour=9, minute=0, args=[
                                   "https://topdev.vn/viec-lam-it/data-analytics-intern-fresher-junior-kt202", 1255062099118395454])
    plugin.app.d.scheduler.add_job(job_post_itviec, 'cron', hour=9, minute=1, args=[
                                   "https://itviec.com/it-jobs/data-analyst", 1255062099118395454])

    # Post jobs on FSW server
    plugin.app.d.scheduler.add_job(job_post, 'cron', hour=9, minute=2, args=[
        "https://topdev.vn/viec-lam-it/react-javascript-kt7367,22", 1255068486573625394])
    plugin.app.d.scheduler.add_job(job_post_itviec, 'cron', hour=9, minute=3, args=[
        "https://itviec.com/it-jobs/reactjs-javascript", 1255068486573625394])
