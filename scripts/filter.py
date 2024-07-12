from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from dotenv import load_dotenv
import json
import os

load_dotenv()


class JobMatchingAssistant:
    def __init__(self, model="gpt-3.5-turbo-0125"):
        self.llm = ChatOpenAI(model=model)
        self.prompt = self.__create_prompt()
        self.chain = self.prompt | self.llm

    def __create_prompt(self):
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a job matching assistant that evaluates job descriptions and requirements for their suitability to a given candidate. You will be provided with a job's {title}, {description}, and {requirement}, and you will determine if the job is relevant to the given {candidate}. The criteria for determining relevance include the candidate's years of experience and toolset proficiency. Remove any job that requires more than 2 years of experience.

                    Provide a single integer percentage indicating how relevant this job is to the candidate, with 100 being the most suitable and 0 being the least suitable. If the job requires more than 2 years of experience, mark it as irrelevant.

                    Output your response in JSON format with a sample response as follows:
                        "suitability": number
                    """,
                )
            ]
        )

    def __get_parser(self):
        schema = [
            ResponseSchema(
                name='suitability', description="How suitable this job is to the candidate."
            ),
        ]
        return StructuredOutputParser.from_response_schemas(schema)

    def __evaluate_job_suitability(self, job, candidate):
        title = job['title']
        description = job['descriptions']
        requirement = job['requirements']

        relevancy = self.chain.invoke(
            {
                "title": title,
                "description": description,
                "requirement": requirement,
                "candidate": candidate
            }
        )

        # Parse the suitability score from the relevancy response
        suitability = self.__get_parser().parse(
            relevancy.content)['suitability']

        return suitability

    def process_jobs(self, jobs_file, output_file):
        with open(jobs_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        with open('profile.json', 'r') as file:
            candidate = json.load(file)

        for job in data:
            job['suitability'] = self.__evaluate_job_suitability(
                job, candidate[get_folder_name(jobs_file)])

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)


def get_folder_name(path=None):
    if path is None:
        path = os.getcwd()
    return os.path.basename(os.path.dirname(path))


def get_subfolder_names(path=None):
    if path is None:
        path = os.getcwd()

    return os.listdir(path)


if __name__ == "__main__":

    # NOTE: Process jobs
    BASE = 'data/raw'
    subfolders = get_subfolder_names(BASE)
    assistant = JobMatchingAssistant()

    for subfolder in subfolders:
        subfolder_path = os.path.join(BASE, subfolder)
        if os.path.isdir(subfolder_path):
            for filename in os.listdir(subfolder_path):
                if filename.endswith('.json'):
                    jobs_file = os.path.join(subfolder_path, filename)
                    output_file = f"data/processed/{os.path.splitext(filename)[0]}_with_relevancy.json"
                    assistant.process_jobs(jobs_file, output_file)
                print(f"Processed {filename}")

    # NOTE: Filter jobs
    os.makedirs(os.path.dirname('data/filter/'), exist_ok=True)
    filtered = 0
    total = 0
    for path in get_subfolder_names('data/processed'):
        with open(os.path.join('data/processed', path), 'r', encoding='utf-8') as file:
            total += len(json.load(file))
        with open(os.path.join('data/processed', path), 'r', encoding='utf-8') as file:
            filtered_jobs = [
                job
                for job in json.load(file)
                if job['suitability'] >= 50
            ]
            output = os.path.join(
                'data/filter',
                path[:-len('_with_relevancy.json')] + '.json'
            )
            with open(output, 'w', encoding='utf-8') as file:
                json.dump(filtered_jobs, file, ensure_ascii=False, indent=2)
            filtered += len(filtered_jobs)

    print(f"Filtered {filtered} jobs out of {total}")
