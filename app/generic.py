import hashlib
import os

def create_folder_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def chunkify_by_size(list, size):
    return [list[i * size:(i + 1) * size] for i in range((len(list) + size - 1) // size)]