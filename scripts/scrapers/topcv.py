from bs4 import BeautifulSoup
from urllib.request import urlopen, Request


def extract_nested_data(soup, find_description=True):
    i, j = (0, 1) if find_description else (1, 2)
    descriptions = []
    try:
        content = soup.find_all('div', class_='job-description__item')[i]
        if content:
            # Extract text from paragraphs
            paragraphs = content.find_all('p')
            for para in paragraphs:
                descriptions.append(para.text.strip())

            # Extract text from list items
            list_items = content.find_all('li')
            for item in list_items:
                descriptions.append(item.text.strip())
    except Exception:
        box_info = soup.find_all('div', class_='box-info')[j]
        if box_info:
            title = box_info.find('h2', class_='title').text.strip()
            content = box_info.find('div', class_='content-tab')
            if content:
                paragraphs = content.find_all('p')
                for para in paragraphs:
                    descriptions.append((title, para.text.strip()))
    return descriptions


def scrape_jobs_topcv(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    page = urlopen(Request(url, headers=headers))
    soup = BeautifulSoup(page, "html.parser")

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

        page = urlopen(Request(job_url, headers=headers))
        soup = BeautifulSoup(page, "html.parser")
        descriptions = extract_nested_data(soup)
        requirements = extract_nested_data(soup, find_description=False)

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
