import sys
import os
from pathlib import Path


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_first_file(directory, file_name) -> str:
    return str(next(Path(os.path.abspath(directory)).glob(file_name)))


def valid_link(link) -> str:
    forbidden = ["{", "}"]
    for i in range(len(link)):
        if link[i] in forbidden:
            link = link[0:i]
            break

    return link


def get_image_name(link) -> str:
    return link.split("/")[-2]
