from bs4 import BeautifulSoup
import requests


def find_description(soup):
    try:
        description = soup.find('div', class_='job-description__item')
        if not description:
            description = soup.find_all('div', class_='box-info')[1]
    except Exception as e:
        print(e)
    return description.text


def find_requirement(soup):
    try:
        requirement = soup.find_all('div', class_='job-description__item')
        if requirement:
            requirement = requirement[1]
        else:
            requirement = soup.find_all('div', class_='box-info')[2]
    except Exception as e:
        print(e)
    return requirement.text


def scrape_jobs_topcv(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    jobs = soup.find_all('div', class_='job-item-search-result')

    job_data = []
    for job in jobs:
        title = job.find('h3').text.strip()
        company = job.find('a', class_='company').text.strip()
        try:
            logo = job.find('img')['src']
        except Exception:
            logo = job.find('img')['data-src']
        job_url = job.find('a')['href']
        location = job.find('label', class_='address').text.strip()
        salary = job.find('label', class_='title-salary').text.strip()
        status = job.find('label', class_='address mobile-hidden').text.strip()

        page = requests.get(job_url, headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")

        try:
            descriptions = find_description(soup)
            requirements = find_requirement(soup)
        except Exception as e:
            print(f"Exception for job {title}: {e}")

        job_data.append({
            'title': title,
            'company': company,
            'logo': logo,
            'url': job_url,
            'location': location,
            'salary': salary,
            'status': status,
            'descriptions': descriptions,
            'requirements': requirements
        })

    return job_data
