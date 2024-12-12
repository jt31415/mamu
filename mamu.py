
import requests
import os
import logging
import re
import json
import argparse

logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)

parser = argparse.ArgumentParser(
    description="Automatically downloads and updates mods from Modrinth")
parser.add_argument(
    "--config", "-c", help="Path to config file", default="config.json")
parser.add_argument(
    "--moddir", "-d", help="Path to the mods directory", default=None)
args = parser.parse_args()

BASE_URL = "https://api.modrinth.com/v2/"

# Get mod list from json config (config.json)

CONFIG = json.load(open(args.config))
PROJECT_SLUGS = CONFIG["mods"]
GAME_VERSION = CONFIG["version"]
LOADER = CONFIG["loader"]

HEADERS = {"User-Agent": "mamu/1.0.0"}


def get_mod_dir() -> str:

    if args.moddir:
        return args.moddir

    APPDATA = os.environ['APPDATA']

    if not os.path.exists(os.path.join(APPDATA, ".minecraft")):
        logging.error("Minecraft not installed, exiting")
        exit(1)

    MOD_DIR = os.path.join(APPDATA, ".minecraft\\mods")

    if os.path.exists(MOD_DIR):
        logging.info(f"Found mods directory: {repr(MOD_DIR)}")
    else:
        if input(f"Could not find mods directory, would you like to create a new folder at {repr(MOD_DIR)}? [Y/n] ").lower().strip() == "n":
            logging.error("Exiting")
            exit(1)
        else:
            logging.info(f"Creating mods directory at {repr(MOD_DIR)}")
            os.mkdir(MOD_DIR)

    return MOD_DIR

# Get the path to the Minecraft mods folder


MOD_DIR = get_mod_dir()


def get_best_version(id: str, game_version: str, loader: str):
    params = {"game_versions": f'["{game_version}"]',
              "loaders": f'["{loader}"]'}
    res = json.loads(requests.get(
        f"{BASE_URL}project/{id}/version", params=params, headers=HEADERS).text)
    if len(res) == 0:
        return
    if "error" in res:
        raise Exception("Incorrect mod id")
    
    return res[0]

def download_file(url: str, filepath: str):
    res = requests.get(url)
    with open(filepath, "wb") as f:
        if res.status_code != 404:
            f.write(res.content)
        else:
            return False
    return True

def download_version(id: str):
    res = json.loads(requests.get(
        f"{BASE_URL}version/{id}", headers=HEADERS).text)
    for file in res["files"]:
        logging.info(f"Downloading file {file['filename']}")
        download_file(file["url"], os.path.join(MOD_DIR, file["filename"]))


def main():

    logging.info(
        f"Using version game version {GAME_VERSION} and {LOADER} loader")

    # Compile mod slugs + mod dependencies

    project_slugs = set(PROJECT_SLUGS)
    mod_ids = set()

    direct_downloads = set()

    for project in project_slugs:

        m = re.fullmatch(r"https://modrinth.com/mod/([A-Za-z0-9\-]+)", project)
        if m != None:
            project = m.group(1)

        try:
            use_version = get_best_version(project, GAME_VERSION, LOADER)
        except Exception as e:
            direct_downloads.add(project)
        else:

            if use_version == None:
                logging.error(
                    f"Could not find any versions for {project} that satisfy your requirements")
                continue

            logging.info(
                f"Using version {use_version['version_number']} for {project} (id {use_version['id']})")
            mod_ids.add(use_version["id"])

            # Figure out dependencies
            total_dependencies = 0
            for dependency in use_version["dependencies"]:
                if dependency["dependency_type"] == "required":

                    version_id = get_best_version(
                        dependency['project_id'], GAME_VERSION, LOADER)["id"]

                    logging.debug(
                        f"Found required dependency {dependency['project_id']} (id {version_id})")
                    mod_ids.add(version_id)
                    total_dependencies += 1

            if total_dependencies > 0:
                logging.info(f"Found {total_dependencies} required dependencies")

    logging.info(f"Compiled {len(mod_ids)} total mods to download")
    logging.debug(mod_ids)
    logging.debug(direct_downloads)


    # Optionally deletes .jar files that are already in the mods directory
    if input("Would you like to delete existing mods in the mods directory? [Y/n] ").lower().strip() != "n":

        deleted = 0
        for file in os.listdir(MOD_DIR):
            full_path = os.path.join(MOD_DIR, file)
            if file.endswith(".jar") and os.path.isfile(full_path):
                os.remove(full_path)
                deleted += 1

        logging.info(f"Deleted {deleted} mods")

    # Download mods + dependencies from modrinth
    for id in mod_ids:
        logging.debug(f"Downloading id {id}")
        download_version(id)

    # Attempt to directly download mods
    for url in direct_downloads:
        filename = os.path.basename(url)
        if download_file(url, os.path.join(MOD_DIR, filename)):
            logging.info(f"Downloaded {filename} from {url}")
        else:
            logging.error(f"Could not download {filename} from {url}")


if __name__ == "__main__":
    main()
