import json
import os

FOLDERPATH = './data/recipes'

def parse_file(file):
    key_data = {}
    with open(file, 'r') as file:
        recipe = json.load(file)
        key_data['item_name'] = recipe.get('result').get('id')
    print(key_data)

def get_files(folder):
    files = []
    for file in os.walk(folder):
        files.append(file)
    return files[0][2]

def parse_all_files(files):
    base_path = './data/recipes/'

    for i, filename in enumerate(files, start=1):
        cur_path = base_path + filename
        print(f'File #{i}: {cur_path}')
        # parse_file(cur_path)

files = get_files(FOLDERPATH)
parse_all_files(files)
