import os
import json
import requests


def get_subfolder_names(path=None):
    if path is None:
        path = os.getcwd()

    return os.listdir(path)


if __name__ == "__main__":
    # NOTE: Upload jobs
    URL = "https://jobboard.up.railway.app"
    BASE = 'data/filter'
    subfolders = get_subfolder_names(BASE)

    for path in get_subfolder_names('data/filter/'):
        tag = 'data' if 'data' in path else 'fsw'
        with open(os.path.join('data/filter/', path), 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                item['tag'] = tag
            response = requests.post(URL + "/jobs", json=data)
            print(response.text)
