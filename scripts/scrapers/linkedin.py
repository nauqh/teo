from bs4 import BeautifulSoup
import requests
import time


def scrape_jobs_linkedin(url):

    attempts = 0
    ids = []

    while attempts < 3 and not ids:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = soup.find_all('li')
        for job in jobs:
            base_card = job.find('div', {"class": "base-card"})
            if base_card is not None:
                ids.append(base_card.get('data-entity-urn').split(":")[3])
        attempts += 1

    job_data = []
    print(ids)
    for id in ids:
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{id}"
        retries = 0

        while retries < 3:
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')

                title = soup.find('h2').text
                company = soup.find(
                    'a', class_='topcard__org-name-link').text.strip()
                logo = soup.find('img').get('data-delayed-url')

                job_url = soup.find('a', class_='topcard__link').get('href')
                location = soup.find(
                    'span', class_='topcard__flavor topcard__flavor--bullet').text.strip().split(',')[0]
                descriptions = [item.text.strip() for item in soup.find(
                    'div', class_='description__text').find_all('ul')[0].find_all('li')]
                requirements = [item.text.strip() for item in soup.find(
                    'div', class_='description__text').find_all('ul')[1].find_all('li')]
                job_data.append({
                    'title': title,
                    'company': company,
                    'logo': logo,
                    'url': job_url,
                    'location': location,
                    'descriptions': descriptions,
                    'requirements': requirements
                })
                break
            except Exception as e:
                print(f"{e}. Retrying...")
                retries += 1
                time.sleep(2)
        else:
            print(f"Skipping ID {id} after 3 retries.")
    return job_data
