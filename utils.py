import os


def create_folder(path):
    if os.path.exists(path):
        return
    os.makedirs(path)
    print(f"Folder created: {path}")