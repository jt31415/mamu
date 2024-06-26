# Modrinth Automatic Mod Updater (MAMU)

A simple Python script you can use to update your mods automatically from Modrinth, using the Labrinth API

# Usage

1. Adjust `config.json` with the game version, loader, and mods that you would like to use. Note that dependencies such as the Fabric API and core libraries might be downloaded automatically, however, often they are not and need to be listed manually.
    - **IMPORTANT**: For now, mods must be listed in either of these ways:
      - Using their **slug**, which is located in this part of the projects's page: `https://modrinth.com/mod/<SLUG HERE>`
      - Using their whole **project URL**

2. Then run `python3 mamu.py` and sit back while your mods are being downloaded! You will also be prompted to delete any existing mods in the current mods directory.

## Known Limitations

- [ ] Only works on Windows
- [ ] Mod folder cannot be specified
- [ ] Modpacks cannot be generated
- [ ] Mods must be listed by their slugs exactly