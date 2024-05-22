
import requests
import os
import logging

import json

logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)

BASE_URL = "https://api.modrinth.com/v2/"

# Get mod list from json config (config.json)

CONFIG = json.load(open("config.json"))
PROJECT_SLUGS = CONFIG["mods"]
GAME_VERSION = CONFIG["version"]
LOADER = CONFIG["loader"]

HEADERS = {"User-Agent": "mamu/1.0.0"}

def get_mod_dir() -> str:

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
    params = {"game_versions": [game_version,], "loaders": [loader,]}
    res = json.loads(requests.get(f"{BASE_URL}project/{id}/version", params=params, headers=HEADERS).text)
    if len(res) == 0:
        return
    return res[0]

def download_version(id: str):
    res = json.loads(requests.get(f"{BASE_URL}version/{id}", headers=HEADERS).text)
    for file in res["files"]:
        logging.info(f"Downloading file {file['filename']}")
        with open(os.path.join(MOD_DIR, file["filename"]), "wb") as f:
            f.write(requests.get(file["url"]).content)

def main():

    # Compile mod slugs + mod dependencies

    project_slugs = set(PROJECT_SLUGS)
    mod_ids = set()
    
    for project in project_slugs:

        use_version = get_best_version(project, GAME_VERSION, LOADER)
        if use_version == None:
            logging.error(f"Could not find any versions for {project} that satisfy your requirements")
            continue

        logging.info(f"Using version {use_version['version_number']} for {project} (id {use_version['id']})")
        mod_ids.add(use_version["id"])

        total_dependencies = 0
        for dependency in use_version["dependencies"]:
            if dependency["dependency_type"] == "required":

                version_id = dependency['version_id']
                if version_id == None:
                    version_id = get_best_version(dependency['project_id'], GAME_VERSION, LOADER)["id"]
                
                logging.debug(f"Found required dependency {dependency['project_id']} (id {version_id})")
                mod_ids.add(version_id)
                total_dependencies += 1

        if total_dependencies > 0:
            logging.info(f"Found {total_dependencies} required dependencies")

    logging.info(f"Compiled {len(mod_ids)} total mods to download")
    logging.debug(mod_ids)

    if input("Would you like to delete existing mods in the mods directory? [Y/n] ").lower().strip() != "n":

        deleted = 0
        for file in os.listdir(MOD_DIR):
            full_path = os.path.join(MOD_DIR, file)
            if file.endswith(".jar") and os.path.isfile(full_path):
                os.remove(full_path)
                deleted += 1

        logging.info(f"Deleted {deleted} mods")

    for id in mod_ids:
        logging.debug(f"Downloading id {id}")
        download_version(id)

if __name__ == "__main__":
    main()