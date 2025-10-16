import json
import os

FOLDERPATH = './data/recipes'

def get_files(folder):
    files = []
    for file in os.walk(folder):
        files.append(file)
    return files[0][2]

def parse_all_files(files):
    base_path = './data/recipes/'

    for i, filename in enumerate(files, start=1):
        cur_path = base_path + filename
        parse_file(cur_path)

files = get_files(FOLDERPATH)
parse_all_files(files)
