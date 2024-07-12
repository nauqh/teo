from bs4 import BeautifulSoup
import requests


def scrape_jobs(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    jobs = soup.find_all('div', class_='ipy-2')

    job_data = []
    for job in jobs:
        job_url = "https://itviec.com/" + job.find('a')['href']
        title = job.find('h3').text.strip()

        if any(keyword in title.lower() for keyword in ['senior', 'manager', 'leader', 'sr.']):
            continue

        company = job.find(
            'div', class_='imy-3 d-flex align-items-center').span.text.strip()
        logo = job.find(
            'div', class_='imy-3 d-flex align-items-center').a.img['data-src']

        mode, location = [div.span.text.strip()
                          for div in job.find_all('div',
                                                  class_='d-flex align-items-center text-dark-grey imt-1')]

        tags = ' '.join([f'`{a.text.strip()}`' for a in job.find(
            'div', class_='imt-3 imb-2').find_all('a')])

        page = requests.get(job_url, headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")
        job_description = soup.find_all('div', class_='imy-5 paragraph')[0]
        job_requirement = soup.find_all('div', class_='imy-5 paragraph')[1]

        # Handle different types of list items (Some pages have ul and li, some pages have p)
        descriptions = [
            f"{li.get_text(strip=True)}"
            for ul in job_description.find_all("ul")
            for li in ul.find_all("li")
        ]
        descriptions += [
            f"{p.get_text(strip=True)}"
            for p in job_description.find_all("p")
        ]

        requirements = [
            f"{li.get_text(strip=True)}"
            for ul in job_requirement.find_all("ul")
            for li in ul.find_all("li")
        ]
        requirements += [
            f"{p.get_text(strip=True)}"
            for p in job_requirement.find_all("p")
        ]

        job_data.append({
            'title': title,
            'company': company,
            'logo': logo,
            'url': job_url,
            'location': location,
            'mode': mode,
            'descriptions': descriptions,
            'requirements': requirements
        })

    return job_data
