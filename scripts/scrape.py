import json
import os
from scrapers.itviec import scrape_jobs
from scrapers.topcv import scrape_jobs_topcv
from scrapers.linkedin import scrape_jobs_linkedin

BASE = "data/raw/"


def save_jobs_to_json(job_data, file_path):
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(job_data, file, ensure_ascii=False)


# NOTE: ITViec
itviec_jobs_data = scrape_jobs("https://itviec.com/it-jobs/data-analyst-sql")
itviec_jobs_fsw = scrape_jobs("https://itviec.com/it-jobs/reactjs")
save_jobs_to_json(itviec_jobs_data, BASE + "DS/itviec_jobs_data.json")
save_jobs_to_json(itviec_jobs_fsw, BASE + "FSW/itviec_jobs_fsw.json")
print("Scraped jobs from ITViec")

# NOTE: TopCV
topcv_jobs_data = scrape_jobs_topcv(
    "https://www.topcv.vn/tim-viec-lam-data-analyst?exp=2")
topcv_jobs_fsw = scrape_jobs_topcv(
    "https://www.topcv.vn/tim-viec-lam-reactjs?exp=2")
save_jobs_to_json(topcv_jobs_data, BASE + "DS/topcv_jobs_data.json")
save_jobs_to_json(topcv_jobs_fsw, BASE + "FSW/topcv_jobs_fsw.json")
print("Scraped jobs from TopCV")

# NOTE: LinkedIn
linkedin_jobs_data = scrape_jobs_linkedin(
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Data%20Analyst&location=Vietnam&f_E=2")
linkedin_jobs_fsw = scrape_jobs_linkedin(
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=React.js&location=Vietnam&f_TPR=&f_E=2")
save_jobs_to_json(linkedin_jobs_data, BASE + "DS/linkedin_jobs_data.json")
save_jobs_to_json(linkedin_jobs_fsw, BASE + "FSW/linkedin_jobs_fsw.json")
print("Scraped jobs from LinkedIn")
