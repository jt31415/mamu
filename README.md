# Modrinth Automatic Mod Updater (MAMU)

A simple Python script you can use to update your mods automatically from Modrinth, using the Labrinth API

# Usage

1. Adjust `config.json` with the game version, loader, and mods that you would like to use. Note that dependencies such as the Fabric API and core libraries should be downloaded automatically and should not need to be listed (if for some reason they aren't downloaded, you can add them).
    - **IMPORTANT**: For now, mods must be listed using their **slug**, which is located in this part of the projects's page: `https://modrinth.com/mod/<SLUG HERE>`

2. Then run `python mamu.py` and sit back while your mods are being downloaded! You will also be prompted to delete any existing mods in the current mods directory.

## Known Limitations

- [ ] Only works on Windows
- [ ] Mod folder cannot be specified
- [ ] Modpacks cannot be generated
- [ ] Mods must be listed by their slugs exactly