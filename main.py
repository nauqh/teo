import subprocess
import requests
import os
import json

# NOTE: CWD is /scripts


def run_script():
    try:
        os.chdir('scripts')
        subprocess.run(['sh', 'script.sh'],
                       check=True)
        print("Script completed successfully.")
    except subprocess.CalledProcessError as e:
        print("Script failed with error:", e)


def get_subfolder_names(path=None):
    if path is None:
        path = os.getcwd()

    return os.listdir(path)


run_script()
