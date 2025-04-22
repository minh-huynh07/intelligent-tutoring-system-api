import os
import time
import requests

from constants import RATE_LIMIT_STATUS_CODE, MAX_RETRY_COUNT


def create_folder(path):
    if os.path.exists(path):
        return
    os.makedirs(path)
    print(f"Folder created: {path}")

def get_data(url, response_type="json"):
    response = requests.get(url)

    retry_count = 1
    while (response.status_code == RATE_LIMIT_STATUS_CODE
           and retry_count <= MAX_RETRY_COUNT):
        print(f"Rate limit exceeded. Retrying in {60} seconds...")
        time.sleep(60)
        retry_count += 1
        response = requests.get(url)

    if response.status_code == 200:
        if response_type == "json":
            return response.json()
        elif response_type == "html":
            return response.text
        else:
            raise ValueError("Invalid response type. Use 'json' or 'html'.")

    raise Exception(f"Request failed with status code {response.status_code}")

def save_file(filename, content):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)
