import shutil
import sys
from pathlib import Path
import re

# module NORMALIZE
# transliterates Cyrillic characters into Latin (except for extension)
# replaces all characters except Latin letters and numbers with the character '_'

from typing import Set, Any

UKRAINIAN_SYMBOLS = 'абвгдеєжзиіїйклмнопрстуфхцчшщьюя'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "je", "zh", "z", "y", "i", "ji", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "ju", "ja")


TRANS = {}

for key, value in zip(UKRAINIAN_SYMBOLS, TRANSLATION):
    TRANS[ord(key)] = value
    TRANS[ord(key.upper())] = value.upper()


def normalize(name):
    name, *extension = name.split('.')
    new_name = name.translate(TRANS)
    new_name = re.sub(r'\W', "_", new_name)
    return f"{new_name}.{'.'.join(extension)}"

# module SCAN
# sorting all files into groups, creating lists

images = list()
video_files = list()
documents = list()
music = list()
archives = list()
unknown = list()
unknown_extensions = set()
extensions = set()
folders = list()

registered_extensions = {
    ('JPEG', 'PNG', 'JPG', 'SVG'): images,
    ('AVI', 'MP4', 'MOV', 'MKV'): video_files,
    ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'): documents,
    ('MP3', 'OGG', 'WAV', 'AMR'): music,
    ('ZIP', 'GZ', 'TAR'): archives
}
groups_files = {
    "images": images,
    "video_files": video_files,
    "documents": documents,
    "music": music,
    "archives": archives,
    "unknown": unknown
}
list_reg_extensions = []
for group_extensions in registered_extensions:
    for extension in group_extensions:
        list_reg_extensions.append(extension)
list_groups_files = []
for group in groups_files:
    list_groups_files.append(group.upper())


def get_extensions(file_name):
    return Path(file_name).suffix[1:].upper()


def scan(folder):
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in list_groups_files:
                folders.append(item)
                scan(item)
            continue

        extension = get_extensions(file_name=item.name)
        new_name = folder/item.name
        if extension in list_reg_extensions:
            try:
                for key_dict, val in registered_extensions.items():
                    if extension in key_dict:
                        container = registered_extensions.get(key_dict)
                        extensions.add(extension)
                        container.append(new_name)
            except KeyError:
                unknown_extensions.add(extension)
                unknown.append(new_name)
        else:
            unknown.append(new_name)
            if extension != "":
                unknown_extensions.add(extension)


# module MAIN


def hande_file(path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)
    path.replace(target_folder/normalize(path.name))


def handle_archive(path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)

    new_name = normalize(re.sub(r"(.zip|.gz|.tar)", '', path.name))
    archive_folder = target_folder / new_name
    archive_folder.mkdir(exist_ok=True)
    archive_folder = Path(archive_folder)

    try:
        shutil.unpack_archive(str(path.resolve()), archive_folder.resolve())
    except shutil.ReadError:
        archive_folder.rmdir()
        print(f"shutil.ReadError {path.name}")
        path.replace(root_folder / "UNKNOWN" / path.name)
        return
    except FileNotFoundError:
        archive_folder.rmdir()
        path.replace(root_folder / "UNKNOWN" / path.name)
        print("FileNotFoundError")
        return
    path.unlink()


def remove_empty_folders(path):
    for item in path.iterdir():
        if item.is_dir():
            remove_empty_folders(item)
            try:
                item.rmdir()
            except OSError:
                pass


def get_folder_objects(root_path):
    for folder in root_path.iterdir():
        if folder.is_dir():
            remove_empty_folders(folder)
            try:
                folder.rmdir()
            except OSError:
                pass


def main():
    path = sys.argv[1]
    print(f"Start in {path}")
    folder_path = Path(path)

    scan(folder_path)
    for group_name, list_files in groups_files.items():
        print(f"'{group_name}': {list_files}\n")
        for file in list_files:
            if group_name == "archives":
                handle_archive(file, folder_path, "ARCHIVES")
                continue
            hande_file(file, folder_path, group_name.upper())

    print(f"All extensions: {extensions}\n")
    print(f"Unknown extensions: {unknown_extensions}\n")

    get_folder_objects(folder_path)


if __name__ == '__main__':
    path = sys.argv[1]
    #print(f"Start in {path}")
    #arg = Path(path)
    #main(arg.resolve())
