import os

# Base directory is the parent of the 'utils' directory, which is 'clippy'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_FILE = os.path.join(BASE_DIR, "data", "pets_data.json")
LIST_FILE = os.path.join(BASE_DIR, "data", "pets_list.json")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
EXTRA_ROOT = os.path.join(BASE_DIR, "media", "extraIcons")
LOGO_DIR = os.path.join(BASE_DIR, "logo.ico")

def ap(path):
    return os.path.abspath(path)
