import sys
import os

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "clippy")
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Base directory is the parent of the 'utils' directory, which is 'clippy'
BASE_DIR = get_base_dir()

DATA_FILE = os.path.join(BASE_DIR, "data", "pets_data.json")
LIST_FILE = os.path.join(BASE_DIR, "data", "pets_list.json")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
EXTRA_ROOT = os.path.join(BASE_DIR, "media", "extraIcons")
LOGO_DIR = os.path.join(BASE_DIR, "logo.ico")

def ap(path):
    return os.path.abspath(path)
